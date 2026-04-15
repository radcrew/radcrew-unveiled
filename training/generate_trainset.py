from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
import json
from openai import OpenAI

_ENV_FILE = Path(__file__).resolve().parent / ".env"
load_dotenv(_ENV_FILE)

prompt = "\n".join([
    "You're visiting a company website and wanna ask about the company and team members."
    "Please generate 100 questions about the company and team members."
    "Try to make every question different from each other in terms of content and structure."
    "Each question should be a JSON object with the following fields: message (string), is_feedback (boolean) as shown below."
    '{"message": "", "is_feedback": false}'
    "The output mustn't have JSON fences like (```json) and just list down json objects. Don't include any other text."
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
        sample = generate_sample(prompt)

        try:
            write_data = [json.loads(item) for item in sample.split("\n")]
        except json.JSONDecodeError:
            print(f"Invalid JSON: {sample}")

        if write_data is None:
            print("No valid JSON found in the output")
            exit(1)

        for item in write_data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
        print(f"Generated {len(write_data)} samples")