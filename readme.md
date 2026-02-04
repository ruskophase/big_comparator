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

## Install Python on Windows
1. Download Python 3 from the official site: `https://www.python.org/downloads/windows/`
2. Run the installer and **enable** `Add python.exe to PATH`.
3. Choose `Install Now`.
4. Open a new terminal (PowerShell or Command Prompt) and verify:
   ```powershell
   python --version
   ```
   If `python` is not found, try:
   ```powershell
   py --version
   ```

## Setup
### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows (PowerShell)
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run
### macOS / Linux
```bash
export OPENAI_API_KEY="your_api_key"
# optional: defaults to gpt-5
export OPENAI_MODEL="gpt-5"
python app.py
```

### Windows (PowerShell)
```powershell
$env:OPENAI_API_KEY="your_api_key"
# optional: defaults to gpt-5
$env:OPENAI_MODEL="gpt-5"
python app.py
```

### Windows (Command Prompt)
```bat
set OPENAI_API_KEY=your_api_key
set OPENAI_MODEL=gpt-5
python app.py
```

## Spec
Implementation notes are in `docs/mvp_spec.md`.
