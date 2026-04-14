# QLoRA training (feedback routing)

Train a small classifier-style SFT on **`message` → `is_feedback`** JSONL (see `trainset_example.jsonl`).

## Prerequisites

- NVIDIA GPU; **Linux or WSL** recommended (`bitsandbytes` 4-bit is unreliable on native Windows).
- Python 3.10+.

## Install

```bash
python -m venv .venv-train
source .venv-train/bin/activate   # Windows: .venv-train\Scripts\activate
pip install -U pip
pip install -r requirements-train.txt
```

## Dataset

Put your examples in **`training/trainset.jsonl`** (same shape as `trainset_example.jsonl`):

```json
{"message": "Hello world!", "is_feedback": false}
```

Each line: `message` (string), `is_feedback` (boolean).

## Train

Edit constants at the top of `train_qlora.py` (model id, paths, hyperparameters), then:

```bash
python training/train_qlora.py
```

Adapter and tokenizer are written to **`training/outputs/qlora-feedback-router/`** (default `OUTPUT_DIR` in the script).
