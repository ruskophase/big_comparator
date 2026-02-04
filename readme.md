# big_comparator

CLI app for comparing unrelated things numerically using an AI-guided conversation.

## What it does
- Shows a welcome ASCII screen and runtime timer.
- Uses OpenAI conversation to help you turn two concepts into agreed numbers.
- Computes ratio, inverse ratio, absolute difference, percent difference, and order-of-magnitude gap.
- Adds contextual comparisons to known constants, each with a source URL.
- Restarts cleanly if numbers cannot support calculations.

## Requirements
- Python 3.10+
- `OPENAI_API_KEY` environment variable

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run
```bash
export OPENAI_API_KEY="your_api_key"
# optional: defaults to gpt-5
export OPENAI_MODEL="gpt-5"
python app.py
```

## Spec
Implementation notes are in `docs/mvp_spec.md`.
