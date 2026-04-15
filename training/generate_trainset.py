from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
import json
from openai import OpenAI

_ENV_FILE = Path(__file__).resolve().parent / ".env"
load_dotenv(_ENV_FILE)

prompt = "\n".join([
    "You're visiting a company website and wanna leave a feedback. Please generate a feedback message."
    "The output should be a JSON object with the following fields: message (string), is_feedback (boolean) as shown below."
    '{"message": "Hello world!", "is_feedback": true}'
    "The output mustn't have JSON fences like (```json)."
])

def generate_sample(prompt: str):
    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=os.environ["HUGGINGFACE_API_KEY"],
    )

    completion = client.chat.completions.create(
        model="meta-llama/Llama-3.1-8B-Instruct:novita",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=1,
    )

    return completion.choices[0].message.content

if __name__ == "__main__":
    with open("trainset.jsonl", "a", encoding="utf-8") as f:
        for i in range(100):
            sample = generate_sample(prompt)

            try:
                write_data = json.loads(sample)
            except json.JSONDecodeError:
                print(f"Invalid JSON: {sample}")
                continue

            f.write(json.dumps(write_data, ensure_ascii=False) + "\n")
            print(f"Generated sample {i + 1}: {sample}")