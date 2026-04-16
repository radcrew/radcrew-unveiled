# QLoRA training (feedback routing)

Train a small classifier-style SFT on **`message` → `is_feedback`** JSONL (see `trainset_example.jsonl`).

## Prerequisites

- NVIDIA GPU; **Linux or WSL** recommended (`bitsandbytes` 4-bit is unreliable on native Windows).
- Python 3.10+.

## Install

Create a virtualenv under **`training/.venv`** (paths below assume that layout):

```bash
cd training
python -m venv .venv
```

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -r requirements.txt
```

**macOS / Linux:**

```bash
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

## Dataset

Put your examples in **`training/trainset.jsonl`** (same shape as `trainset_example.jsonl`):

```json
{"message": "Hello world!", "is_feedback": false}
```

Each line: `message` (string), `is_feedback` (boolean).

## Train

Edit constants at the top of `train_qlora.py` (model id, paths, hyperparameters).

### Windows: UTF-8 before starting Python

On native Windows, importing **TRL** can fail with `UnicodeDecodeError: 'charmap' codec can't decode ...` because some TRL assets are UTF-8 text while Python’s default text encoding may be **cp1252** unless UTF-8 mode is enabled.

**`PYTHONUTF8` must be set in the environment before the `python` process starts** (setting it inside `train_qlora.py` is too late).

**Recommended (project-local):** from the repo root, run the launcher:

```powershell
.\training\run_train.ps1
```

That script sets `PYTHONUTF8=1` and `PYTHONIOENCODING=utf-8`, then runs `training/.venv/Scripts/python.exe training/train_qlora.py`.

**Manual (same shell only):**

```powershell
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
python training/train_qlora.py
```

On **Linux / WSL**, you can usually run `python training/train_qlora.py` without extra steps.

### Default output

Adapter and tokenizer are written to **`training/outputs/qlora-feedback-router/`** (see `OUTPUT_DIR` in `train_qlora.py`).
