import os
import re
import sys
import time
from decimal import Decimal, InvalidOperation, getcontext
from typing import List, Tuple

from openai import OpenAI

from reference_data import REFERENCE_FACTS, ReferenceFact

getcontext().prec = 50

BANNER = r"""
 ____  _       ____                                 _
| __ )(_) __ _/ ___|___  _ __ ___  _ __   __ _ _ __| |_ ___  _ __
|  _ \| |/ _` | |   / _ \| '_ ` _ \| '_ \ / _` | '__| __/ _ \| '__|
| |_) | | (_| | |__| (_) | | | | | | |_) | (_| | |  | || (_) | |
|____/|_|\__, |\____\___/|_| |_| |_| .__/ \__,_|_|   \__\___/|_|
         |___/                      |_|
"""

FINAL_NUMBER_RE = re.compile(r"FINAL_NUMBER\s*=\s*([^\n\r]+)", re.IGNORECASE)
FINAL_UNIT_RE = re.compile(r"FINAL_UNIT\s*=\s*([^\n\r]+)", re.IGNORECASE)


class ComparisonError(Exception):
    pass


def elapsed_str(start: float) -> str:
    elapsed = int(time.monotonic() - start)
    hours, rem = divmod(elapsed, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def timed_print(start: float, text: str = "") -> None:
    print(f"[{elapsed_str(start)}] {text}")


def timed_input(start: float, prompt: str) -> str:
    return input(f"[{elapsed_str(start)}] {prompt}")


def format_decimal(value: Decimal) -> str:
    if value == 0:
        return "0"
    abs_v = abs(value)
    if abs_v >= Decimal("1e9") or abs_v < Decimal("1e-3"):
        return f"{value:.6E}"
    normalized = value.normalize()
    return format(normalized, "f")


def parse_decimal(text: str) -> Decimal:
    cleaned = text.strip().replace(",", "")
    return Decimal(cleaned)


def strip_final_lines(text: str) -> str:
    lines = []
    for line in text.splitlines():
        if line.strip().upper().startswith("FINAL_NUMBER="):
            continue
        if line.strip().upper().startswith("FINAL_UNIT="):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def extract_final_number(text: str) -> Tuple[Decimal, str] | Tuple[None, None]:
    number_match = FINAL_NUMBER_RE.search(text)
    if not number_match:
        return None, None

    raw_value = number_match.group(1).strip()
    try:
        value = parse_decimal(raw_value)
    except InvalidOperation:
        return None, None

    unit_match = FINAL_UNIT_RE.search(text)
    unit = unit_match.group(1).strip() if unit_match else "unitless"
    return value, unit


def ask_ai(client: OpenAI, model: str, system_prompt: str, history: List[dict]) -> str:
    messages = [{"role": "system", "content": system_prompt}] + history
    response = client.chat.completions.create(model=model, messages=messages)
    return response.choices[0].message.content or ""


def ground_number(
    client: OpenAI,
    model: str,
    start_time: float,
    label: str,
) -> Tuple[Decimal, str, str]:
    system_prompt = (
        "You are helping the user convert a concept into a single numeric value. "
        "Use concise, friendly English. Ask clarifying questions until you have enough information. "
        "When you can propose a final value, include these exact lines at the end of your message:\n"
        "FINAL_NUMBER=<plain numeric literal, optionally scientific notation>\n"
        "FINAL_UNIT=<short unit label>\n"
        "Do not stop asking questions until a meaningful number is possible."
    )

    concept = timed_input(start_time, f"Enter {label} concept: ").strip()
    while not concept:
        concept = timed_input(start_time, f"Enter {label} concept: ").strip()

    history: List[dict] = [{"role": "user", "content": concept}]

    while True:
        ai_text = ask_ai(client, model, system_prompt, history)
        visible_text = strip_final_lines(ai_text)
        if visible_text:
            timed_print(start_time, f"AI: {visible_text}")

        proposed_value, proposed_unit = extract_final_number(ai_text)

        if proposed_value is not None:
            timed_print(
                start_time,
                f"Proposed {label} value: {format_decimal(proposed_value)} {proposed_unit}",
            )
            confirmation = timed_input(
                start_time,
                "Type 'y' to accept, 'n' to continue chatting, or type a number to override: ",
            ).strip()
            if confirmation.lower() == "y":
                return proposed_value, proposed_unit, concept
            if confirmation.lower() == "n":
                follow_up = timed_input(start_time, "Tell AI what to correct: ").strip()
                history.append({"role": "assistant", "content": ai_text})
                history.append({"role": "user", "content": follow_up})
                continue
            try:
                manual_value = parse_decimal(confirmation)
                manual_unit = timed_input(start_time, "Unit for your override value: ").strip() or "unitless"
                return manual_value, manual_unit, concept
            except InvalidOperation:
                timed_print(start_time, "Invalid override value. Continuing conversation.")
                history.append({"role": "assistant", "content": ai_text})
                history.append(
                    {
                        "role": "user",
                        "content": "Your proposed final number format was invalid; please retry with valid numeric FINAL_NUMBER.",
                    }
                )
                continue

        user_reply = timed_input(start_time, "You: ").strip()
        history.append({"role": "assistant", "content": ai_text})
        history.append({"role": "user", "content": user_reply})


def require_usable_number(value: Decimal, label: str) -> None:
    if not value.is_finite():
        raise ComparisonError(f"{label} is not finite.")
    if value == 0:
        raise ComparisonError(f"{label} is zero, and ratio metrics would fail.")


def log10_abs(value: Decimal) -> Decimal:
    return abs(value).log10()


def choose_reference_matches(value: Decimal, count: int = 4) -> List[Tuple[ReferenceFact, Decimal]]:
    scored = []
    for fact in REFERENCE_FACTS:
        factor = value / fact.value
        distance = abs(log10_abs(factor))
        scored.append((distance, fact, factor))
    scored.sort(key=lambda item: item[0])
    return [(fact, factor) for _, fact, factor in scored[:count]]


def print_comparison(
    start_time: float,
    a_value: Decimal,
    a_unit: str,
    a_concept: str,
    b_value: Decimal,
    b_unit: str,
    b_concept: str,
) -> None:
    require_usable_number(a_value, "First value")
    require_usable_number(b_value, "Second value")

    ratio_ab = a_value / b_value
    ratio_ba = b_value / a_value
    abs_diff = abs(a_value - b_value)
    midpoint = (abs(a_value) + abs(b_value)) / Decimal("2")
    if midpoint == 0:
        raise ComparisonError("Midpoint is zero, so percent difference cannot be computed.")
    pct_diff = (abs_diff / midpoint) * Decimal("100")
    mag_gap = abs(log10_abs(ratio_ab))

    timed_print(start_time, "")
    timed_print(start_time, "=== Comparison Result ===")
    timed_print(start_time, f"{a_concept} ({a_unit}): {format_decimal(a_value)}")
    timed_print(start_time, f"{b_concept} ({b_unit}): {format_decimal(b_value)}")
    timed_print(start_time, f"A / B: {format_decimal(ratio_ab)}")
    timed_print(start_time, f"B / A: {format_decimal(ratio_ba)}")
    timed_print(start_time, f"Absolute difference: {format_decimal(abs_diff)}")
    timed_print(start_time, f"Percent difference: {format_decimal(pct_diff)}%")
    timed_print(start_time, f"Order-of-magnitude gap: {format_decimal(mag_gap)}")

    timed_print(start_time, "")
    timed_print(start_time, "=== Contextual Comparisons (with sources) ===")
    for heading, value in [("First number", a_value), ("Second number", b_value)]:
        timed_print(start_time, f"{heading}:")
        for fact, factor in choose_reference_matches(value):
            timed_print(
                start_time,
                (
                    f"- vs {fact.name} ({fact.unit}): {format_decimal(value)} is "
                    f"{format_decimal(factor)}x | source: {fact.source_url}"
                ),
            )


def main() -> int:
    start_time = time.monotonic()
    model = os.getenv("OPENAI_MODEL", "gpt-5")
    api_key = os.getenv("OPENAI_API_KEY")

    print(BANNER)
    timed_print(start_time, "Welcome to Big Comparator.")
    timed_print(start_time, f"Model: {model}")

    if not api_key:
        timed_print(start_time, "Missing OPENAI_API_KEY. Set it and run again.")
        return 1

    client = OpenAI(api_key=api_key)

    while True:
        try:
            timed_print(start_time, "")
            timed_print(start_time, "Let's establish your first number.")
            a_value, a_unit, a_concept = ground_number(client, model, start_time, "first")

            timed_print(start_time, "")
            timed_print(start_time, "Now let's establish your second number.")
            b_value, b_unit, b_concept = ground_number(client, model, start_time, "second")

            print_comparison(start_time, a_value, a_unit, a_concept, b_value, b_unit, b_concept)
            break
        except ComparisonError as exc:
            timed_print(start_time, f"Error: {exc}")
            timed_print(start_time, "Restarting full comparison flow from the beginning.")
        except KeyboardInterrupt:
            timed_print(start_time, "Interrupted by user.")
            return 130

    timed_print(start_time, "Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
