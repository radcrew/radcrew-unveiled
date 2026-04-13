# QLoRA training (RadCrew chat generator)

This folder holds a **separate** GPU training stack for supervised fine-tuning of the main chat model. It mirrors production layout from the plan: the user turn is the full `build_chat_prompt` string (one message); the assistant turn is the target answer. Dataset details and parity rules are in [DATASET.md](DATASET.md).

## Prerequisites

- NVIDIA GPU with a recent driver; **Linux or WSL** is strongly recommended (`bitsandbytes` 4-bit is unreliable on native Windows).
- Python 3.10+.
- Enough VRAM for the base model in 4-bit plus LoRA and activations. Rough guide for **defaults** (`Qwen/Qwen2.5-1.5B-Instruct`, batch1, grad accumulation 8, `max_length` 4096): about **8–12 GB**; increase headroom for longer sequences or larger batches.

## Install

```bash
python -m venv .venv-train
source .venv-train/bin/activate   # Windows: .venv-train\Scripts\activate
pip install -U pip
pip install -r requirements-train.txt
```

Do not commit API tokens. For Hub uploads, set `HUGGINGFACE_API_KEY` in the environment, not in the repo.

## Train (QLoRA + TRL `SFTTrainer`)

From the repo root (or any cwd; use absolute paths if you prefer):

```bash
python training/train_qlora.py \
  --model-id Qwen/Qwen2.5-1.5B-Instruct \
  --train-file training/data/train.jsonl \
  --output-dir training/outputs/my-run \
  --epochs 1 \
  --learning-rate 2e-4 \
  --per-device-train-batch-size 1 \
  --gradient-accumulation-steps 8 \
  --max-length 4096
```

Optional validation:

```bash
python training/train_qlora.py \
  --train-file training/data/train.jsonl \
  --eval-file training/data/val.jsonl \
  --output-dir training/outputs/my-run \
  ...
```

Behavior notes:

- JSONL rows must follow [DATASET.md](DATASET.md): either `messages` (`user` then `assistant`) or `prompt` / `completion`.
- By default, **`assistant_only_loss` is on** so loss is computed on the assistant reply only (recommended for chat SFT). Pass `--no-assistant-only-loss` to train on the full sequence.
- Checkpoints and the final **LoRA adapter** are written to `--output-dir`.

## Merge adapter into full weights

After training, `--output-dir` contains a PEFT adapter. To produce a single merged model directory (full weights, larger on disk) suitable for local inference or some hosts:

```bash
python training/train_qlora.py \
  --train-file training/data/train.jsonl \
  --output-dir training/outputs/my-run \
  --merge-into training/outputs/my-run-merged
```

You can also merge programmatically: load the base model in `float16`/`bfloat16`, wrap with `PeftModel.from_pretrained`, call `merge_and_unload()`, then `save_pretrained` (see `merge_adapter_to_base` in `train_qlora.py`).

## Push to the Hugging Face Hub

1. Log in: `huggingface-cli login` (or export `HUGGINGFACE_API_KEY`).
2. Train, then push the adapter:

```bash
python training/train_qlora.py \
  --train-file training/data/train.jsonl \
  --output-dir training/outputs/my-run \
  --push-to-hub \
  --hub-model-id YOUR_ORG/radcrew-qwen-qlora \
  --hub-private
```

**Serving constraint:** production uses `HUGGINGFACE_MODEL` in the backend; pointing it at your Hub repo only works if your inference provider actually loads that model id. Otherwise self-host (vLLM, TGI, llama.cpp, etc.) and point the backend at a compatible endpoint (follow-up work outside this folder).

## Optional: prompt parity check

For rows that include `question`, `context_chunks`, and optional `history` (see [DATASET.md](DATASET.md)), verify that the stored user turn (`messages[0].content` or `prompt`) matches a fresh `build_chat_prompt` rebuild:

```bash
python training/scripts/validate_prompt_parity.py path/to/dataset.jsonl
```

Use `--verbose` for a unified diff on mismatch, `--max-rows N` to scan only the first N JSON objects, and `--strict` to fail if an auditable row has no stored user content. Backend tests in `backend/app/tests/test_validate_prompt_parity.py` cover the same contract.
