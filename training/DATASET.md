# SFT dataset (JSONL) for RadCrew QLoRA

Training examples should match **production inference**: one `user` message whose `content` is **byte-for-byte identical** to what `build_chat_prompt` would return for the same `question`, `context_chunks`, and `history`. The assistant target is the desired answer (Markdown following the same style rules embedded in that prompt).

Reference implementation: `backend/app/chat/rag/prompt.py` → `build_chat_prompt`.

## JSONL file format

- **One JSON object per line** (`.jsonl`). UTF-8. No multi-line JSON blobs unless you escape newlines inside strings (standard JSON).
- **Recommended primary schema:** `messages` (chat format). Each line is one training example.

### Primary schema: `messages`

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `messages` | array | yes | Exactly two entries: `[user_turn, assistant_turn]`. |
| `messages[0].role` | string | yes | Must be `"user"`. |
| `messages[0].content` | string | yes | Full prompt text (see [Parity with `build_chat_prompt`](#parity-with-build_chat_prompt)). |
| `messages[1].role` | string | yes | Must be `"assistant"`. |
| `messages[1].content` | string | yes | Target answer for SFT. |
| `meta` | object | no | Provenance / debugging only; trainers may ignore it. |

### Alternative schema: `prompt` / `completion`

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `prompt` | string | yes | Same string as `messages[0].content` (the full `build_chat_prompt` output). |
| `completion` | string | yes | Same as `messages[1].content`. |

Map these to `messages` in training code if your trainer expects chat tuples.

### Optional structured fields (for export parity checks)

You may attach **metadata** that records how the user string was built. These fields are **not** sent to the model at training time unless you concatenate them yourself; they exist so you can re-run `build_chat_prompt` and diff against `messages[0].content`.

| Field | Type | Description |
| --- | --- | --- |
| `question` | string | The user’s latest question (same as `question` argument to `build_chat_prompt`). |
| `history` | array | Ordered prior turns: `{ "role": "user" \| "assistant", "content": string }[]`. |
| `context_chunks` | array | Retrieved chunks in **the same order** as in production: `{ "title": string, "text": string }[]` (other keys like `id` are fine but only `title` and `text` affect the prompt). |

If present, `messages[0].content` **must** equal `build_chat_prompt(question, context_chunks_as_KnowledgeChunk, history_as_ChatHistoryMessage)`.

## Parity with `build_chat_prompt`

Production builds a **single string** (then sends it as one `user` message). Replicate that string in each row’s user content.

### 1. Context block (`context_chunks`)

- Join chunks with newlines. For chunk at zero-based index `index`:

 `Source {index + 1} ({chunk.title}): {chunk.text}`

- If there are no chunks, the context section still exists; the placeholder line is: `No context found.`

Chunk type in code: `KnowledgeChunk` (`backend/app/knowledge/models.py`). Only `title` and `text` appear in the prompt.

### 2. Conversation history

- Take `history` (or treat `null`/missing as `[]`).
- **Truncate to the last `MAX_HISTORY_MESSAGES` turns**, where `MAX_HISTORY_MESSAGES = 10` in `prompt.py` (not the API’s `max_length=12` on the request—training data should reflect what the **prompt builder** actually uses after truncation).
- Join into lines:

  - `User: {content}` for `role == "user"`
  - `Assistant: {content}` for `role == "assistant"`

- If there are no history lines after processing, the history section’s body is exactly: `No prior conversation.`

### 3. Full template (fixed preamble + sections)

The final string is the following pieces joined with **`\n`** (single newlines), in order:

1. Fixed instruction lines (through `"Never contradict yourself."`), including the empty line after that sentence.
2. The literal line `Conversation history:`
3. `history_section` (from step 2)
4. Empty line
5. The literal line `Context sources:`
6. `context` string from step 1, or `No context found.`
7. Empty line
8. `Question: {question}` where `{question}` is the raw question string passed in
9. Empty line
10. Fixed formatting rules (Markdown, bullets with `-`, no `*` bullets, no URLs/links, etc.—see `prompt.py` for the exact trailing lines)

There is **no** separate system message in production (`chat_completion` uses `messages=[{"role":"user","content": prompt}]`); do not split the instructions into a `system` role for training if you want distribution match, unless you change production to match.

### 4. Example (illustrative)

For `question = "Who maintains X?"`, one chunk titled `Guide` with text `Team A owns X.`, and empty history, the user `content` begins:

```text
You are RadCrew's website assistant.
Answer only using the conversation history and provided context sources.
...
Never contradict yourself.

Conversation history:
No prior conversation.

Context sources:
Source 1 (Guide): Team A owns X.

Question: Who maintains X?

Format the answer in simple Markdown for readability (use bold labels and short bullet lists when helpful).
...
```

The assistant `content` would be your gold answer (e.g. short Markdown, `-` bullets only, no links).

## Example JSONL rows

**Minimal (what the trainer consumes):**

```json
{"messages":[{"role":"user","content":"You are RadCrew's website assistant.\n..."},{"role":"assistant","content":"Team A maintains X."}]}
```

**With optional metadata for parity audits:**

```json
{"question":"Who maintains X?","history":[],"context_chunks":[{"title":"Guide","text":"Team A owns X."}],"messages":[{"role":"user","content":"..."},{"role":"assistant","content":"Team A maintains X."}],"meta":{"source":"synthetic-v1"}}
```

## Dataset hygiene

- **Same chunk set as production:** If you build examples from logs, rebuild the user prompt with the **exact** retrieved chunks (and order) the user saw. Otherwise the model learns the wrong conditional distribution.
- **Redaction:** Do not commit secrets or PII; follow your export/redaction policy.
- **Quality:** Assistant answers should obey the formatting rules already repeated in the user prompt (no URL/link markdown, `-` bullets, etc.).

## Machine-readable schema

See `training/schemas/dataset-row.schema.json` for a JSON Schema describing the recommended `messages` row shape.
