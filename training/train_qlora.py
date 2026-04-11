#!/usr/bin/env python3
"""QLoRA supervised fine-tuning with TRL SFTTrainer + PEFT (RadCrew chat generator).

Expects JSONL aligned with production: each row has either `messages` (user+assistant)
or `prompt`/`completion` matching DATASET.md. See README.md for usage.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import torch
from datasets import Dataset, load_dataset
from peft import LoraConfig, PeftModel, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from trl import SFTConfig, SFTTrainer

# Match backend/app/config.py default for HUGGINGFACE_MODEL.
DEFAULT_BASE_MODEL = "meta-llama/Meta-Llama-3-8B-Instruct"

# Attention + MLP projections for Qwen2 / Qwen2.5 style models.
DEFAULT_LORA_TARGETS = ("q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj")


def _messages_from_row(row: dict) -> dict:
    if "messages" in row:
        msgs = row["messages"]
        if not isinstance(msgs, list) or len(msgs) != 2:
            raise ValueError("'messages' must be a list of exactly two turns [user, assistant].")
        if msgs[0].get("role") != "user" or msgs[1].get("role") != "assistant":
            raise ValueError("messages[0] must be user and messages[1] must be assistant.")
        return {"messages": msgs}
    if "prompt" in row and "completion" in row:
        return {
            "messages": [
                {"role": "user", "content": row["prompt"]},
                {"role": "assistant", "content": row["completion"]},
            ]
        }
    raise ValueError(
        "Each JSONL row needs either 'messages' or both 'prompt' and 'completion'. "
        f"Got keys: {sorted(row.keys())}"
    )


def load_jsonl_dataset(path: Path, num_proc: int | None) -> Dataset:
    raw = load_dataset("json", data_files=str(path), split="train")

    def _map_fn(example: dict) -> dict:
        return _messages_from_row(example)

    kwargs: dict = {"remove_columns": raw.column_names}
    if num_proc and num_proc > 1:
        kwargs["num_proc"] = num_proc
    return raw.map(_map_fn, **kwargs)


def build_bnb_config() -> BitsAndBytesConfig:
    return BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
    )


def merge_adapter_to_base(*, base_model_id: str, adapter_dir: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    tokenizer = AutoTokenizer.from_pretrained(base_model_id, trust_remote_code=True)
    dtype = torch.bfloat16 if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else torch.float16
    base = AutoModelForCausalLM.from_pretrained(
        base_model_id,
        torch_dtype=dtype,
        device_map="auto",
        trust_remote_code=True,
    )
    model = PeftModel.from_pretrained(base, str(adapter_dir))
    merged = model.merge_and_unload()
    merged.save_pretrained(str(out_dir))
    tokenizer.save_pretrained(str(out_dir))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="QLoRA SFT for RadCrew-style chat JSONL.")
    p.add_argument(
        "--model-id",
        default=DEFAULT_BASE_MODEL,
        help=f"Hugging Face base model id (default: {DEFAULT_BASE_MODEL}).",
    )
    p.add_argument(
        "--train-file",
        type=Path,
        required=True,
        help="Path to training JSONL (messages or prompt/completion per DATASET.md).",
    )
    p.add_argument(
        "--eval-file",
        type=Path,
        default=None,
        help="Optional validation JSONL in the same format.",
    )
    p.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./qlora-out"),
        help="Directory for checkpoints and final LoRA adapter.",
    )
    p.add_argument("--epochs", type=float, default=1.0)
    p.add_argument("--learning-rate", type=float, default=2e-4)
    p.add_argument("--per-device-train-batch-size", type=int, default=1)
    p.add_argument("--gradient-accumulation-steps", type=int, default=8)
    p.add_argument("--max-length", type=int, default=4096, help="Tokenized sequence cap (raise for long RAG prompts).")
    p.add_argument("--logging-steps", type=int, default=10)
    p.add_argument("--save-strategy", default="epoch", choices=("no", "epoch", "steps"))
    p.add_argument("--save-steps", type=int, default=500)
    p.add_argument("--eval-steps", type=int, default=500)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--lora-r", type=int, default=16)
    p.add_argument("--lora-alpha", type=int, default=32)
    p.add_argument("--lora-dropout", type=float, default=0.05)
    p.add_argument(
        "--dataset-num-proc",
        type=int,
        default=4,
        help="Processes for JSONL map (1 disables multiprocessing).",
    )
    p.add_argument(
        "--no-assistant-only-loss",
        action="store_true",
        help="Train with NLL on the full sequence (not recommended for chat SFT).",
    )
    p.add_argument(
        "--merge-into",
        type=Path,
        default=None,
        help="If set, merge LoRA into base weights and save full model to this directory after training.",
    )
    p.add_argument("--push-to-hub", action="store_true", help="Upload trained adapter to the Hub after training.")
    p.add_argument(
        "--hub-model-id",
        default=None,
        help="Target Hub repo id (e.g. org/radcrew-qwen-qlora). Required with --push-to-hub.",
    )
    p.add_argument("--hub-private", action="store_true", help="Create/use a private Hub repo when pushing.")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if not torch.cuda.is_available():
        print("Error: CUDA is required for 4-bit QLoRA (bitsandbytes).", file=sys.stderr)
        return 1

    if args.push_to_hub and not args.hub_model_id:
        print("Error: --hub-model-id is required when using --push-to-hub.", file=sys.stderr)
        return 1

    if not args.train_file.is_file():
        print(f"Error: train file not found: {args.train_file}", file=sys.stderr)
        return 1

    args.output_dir.mkdir(parents=True, exist_ok=True)

    torch.manual_seed(args.seed)

    num_proc = args.dataset_num_proc if args.dataset_num_proc > 1 else None
    train_ds = load_jsonl_dataset(args.train_file, num_proc)
    eval_ds = None
    if args.eval_file is not None:
        if not args.eval_file.is_file():
            print(f"Error: eval file not found: {args.eval_file}", file=sys.stderr)
            return 1
        eval_ds = load_jsonl_dataset(args.eval_file, num_proc)

    tokenizer = AutoTokenizer.from_pretrained(args.model_id, trust_remote_code=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    bnb_config = build_bnb_config()
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )
    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)
    model.config.use_cache = False

    peft_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=list(DEFAULT_LORA_TARGETS),
    )

    use_bf16 = torch.cuda.is_bf16_supported()
    eval_strategy = "no"
    if eval_ds is not None:
        eval_strategy = "steps"

    training_args = SFTConfig(
        output_dir=str(args.output_dir),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.per_device_train_batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        learning_rate=args.learning_rate,
        logging_steps=args.logging_steps,
        save_strategy=args.save_strategy,
        save_steps=args.save_steps if args.save_strategy == "steps" else None,
        eval_strategy=eval_strategy,
        eval_steps=args.eval_steps if eval_strategy == "steps" else None,
        bf16=use_bf16,
        fp16=not use_bf16,
        max_length=args.max_length,
        assistant_only_loss=not args.no_assistant_only_loss,
        gradient_checkpointing=True,
        report_to="none",
        seed=args.seed,
    )

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=eval_ds,
        processing_class=tokenizer,
        peft_config=peft_config,
    )

    trainer.train()
    trainer.save_model(str(args.output_dir))
    tokenizer.save_pretrained(str(args.output_dir))

    if args.merge_into:
        print(f"Merging adapter into base, saving to {args.merge_into} …")
        merge_adapter_to_base(
            base_model_id=args.model_id,
            adapter_dir=args.output_dir,
            out_dir=args.merge_into,
        )

    if args.push_to_hub:
        token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_API_KEY")
        print(f"Pushing adapter to {args.hub_model_id} …")
        trainer.model.push_to_hub(args.hub_model_id, private=args.hub_private, token=token)
        tokenizer.push_to_hub(args.hub_model_id, private=args.hub_private, token=token)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
