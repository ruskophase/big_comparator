# Big Comparator MVP Spec

## Goal
Build a CLI app that helps users compare two unrelated things numerically through open-ended AI-guided conversation.

## Core UX
1. Show welcome screen with ASCII art.
2. Prompt for first concept.
3. Enter unlimited conversation to converge on an agreed numeric value.
4. Repeat for second concept.
5. Compute and print comparison metrics.
6. Print contextual comparisons against known reference constants, each with source link.
7. Keep a visible runtime timer throughout.

## Conversation Rules
- Language: English.
- No hard turn/token limits for MVP.
- AI asks clarifying questions until a usable number is agreed.
- Once AI proposes a final number, user must confirm.
- User can override with direct numeric input at any time.

## Validation & Error Handling
- Usable numbers are finite decimal/scientific-notation values.
- If calculation cannot proceed (e.g., zero denominator for selected metric), display error and restart the full comparison flow.

## Outputs
### Primary stats
- `A / B` and `B / A` ratios.
- Absolute difference `|A - B|`.
- Percent difference using midpoint formula.
- Order-of-magnitude gap (base-10 log ratio).

### Context stats
- Compare each user number to selected constants from a local dataset.
- Show factor and source URL for each constant.

## Technical Choices
- Runtime: Python CLI.
- Model default: `gpt-5` (override with `OPENAI_MODEL`).
- API key via `OPENAI_API_KEY`.
- Timer based on process monotonic clock.

## Non-goals (MVP)
- No persistence/history storage.
- No UI besides terminal output.
- No strict cost/latency guardrails.

## Future tighten-ups
- Turn limits and confidence thresholds.
- Better source retrieval for user-provided entities.
- Structured output schema and richer unit handling.
