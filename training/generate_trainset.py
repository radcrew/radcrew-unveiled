"""Helpers for generating trainset data via Hugging Face Inference. Config from ``training/.env``."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

_ENV_FILE = Path(__file__).resolve().parent / ".env"
load_dotenv(_ENV_FILE)

prompt = "\n".join(
    "Suppose you are a feedback trainset generator which generates real feedback texts or non-feedback texts."
    "The output should be a JSON object with the following fields: message (string), is_feedback (boolean) as shown below."
    '{"message": "Hello world!", "is_feedback": false}'
    "The output shouldn't have JSON fences."
)

def generate_trainset(prompt: str):
    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=os.environ["HUGGINGFACE_API_KEY"],
    )

    completion = client.chat.completions.create(
        model="zai-org/GLM-5.1:together",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
    )

    return completion.choices[0].message.content

if __name__ == "__main__":
    result = generate_trainset(prompt)
    print(result)