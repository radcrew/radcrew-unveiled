#!/usr/bin/env python3
"""QLoRA SFT for feedback intent: JSONL rows like trainset_example.jsonl (message + is_feedback)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import torch
from datasets import load_dataset
from peft import LoraConfig, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from trl import SFTConfig, SFTTrainer

# --- paths (same directory as this script) ---
_TRAIN_DIR = Path(__file__).resolve().parent
TRAIN_JSONL = _TRAIN_DIR / "trainset.jsonl"
OUTPUT_DIR = _TRAIN_DIR / "outputs" / "qlora-feedback-router"

# --- model / training ---
MODEL_ID = "meta-llama/Meta-Llama-3-8B-Instruct"
SEED = 42
EPOCHS = 1.0
LEARNING_RATE = 2e-4
PER_DEVICE_TRAIN_BATCH_SIZE = 1
GRADIENT_ACCUMULATION_STEPS = 8
MAX_LENGTH = 2048
LOGGING_STEPS = 10

LORA_R = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.05
LORA_TARGET_MODULES = ("q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj")


def _row_to_messages(row: dict) -> dict:
    if "message" not in row or "is_feedback" not in row:
        raise ValueError("each row needs 'message' and 'is_feedback'")

    msg, flag = row["message"], row["is_feedback"]

    if not isinstance(msg, str) or not msg.strip():
        raise ValueError("'message' must be a non-empty string")
    if not isinstance(flag, bool):
        raise ValueError("'is_feedback' must be a boolean")

    user_content = msg
    assistant_content = json.dumps({"is_feedback": flag}, separators=(",", ":"))
    return {
        "messages": [
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": assistant_content},
        ]
    }


def _load_train_dataset():
    if not TRAIN_JSONL.is_file():
        raise FileNotFoundError(f"missing training file: {TRAIN_JSONL}")

    raw = load_dataset("json", data_files=str(TRAIN_JSONL), split="train")
    return raw.map(_row_to_messages, remove_columns=raw.column_names)


def main() -> int:
    if not torch.cuda.is_available():
        print("CUDA is required for 4-bit QLoRA.", file=sys.stderr)
        return 1

    torch.manual_seed(SEED)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    train_ds = _load_train_dataset()

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    bnb = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
    )
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        quantization_config=bnb,
        device_map="auto",
        trust_remote_code=True,
    )
    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)
    model.config.use_cache = False

    peft = LoraConfig(
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=list(LORA_TARGET_MODULES),
    )

    use_bf16 = torch.cuda.is_bf16_supported()
    training_args = SFTConfig(
        output_dir=str(OUTPUT_DIR),
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=PER_DEVICE_TRAIN_BATCH_SIZE,
        gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
        learning_rate=LEARNING_RATE,
        logging_steps=LOGGING_STEPS,
        save_strategy="epoch",
        eval_strategy="no",
        bf16=use_bf16,
        fp16=not use_bf16,
        max_length=MAX_LENGTH,
        assistant_only_loss=True,
        gradient_checkpointing=True,
        report_to="none",
        seed=SEED,
    )

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        processing_class=tokenizer,
        peft_config=peft,
    )
    trainer.train()
    trainer.save_model(str(OUTPUT_DIR))
    tokenizer.save_pretrained(str(OUTPUT_DIR))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
