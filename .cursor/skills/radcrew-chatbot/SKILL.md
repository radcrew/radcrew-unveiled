---
name: radcrew-chatbot
description: >-
  RadCrew Unveiled FAQ chatbot — FastAPI LangGraph (feedback vs RAG), Hugging Face
  inference, knowledge ingestion, SSE /chat, frontend widget, and QLoRA feedback
  routing training. Use when changing backend/app/chatbot, POST /chat, RAG prompts,
  trainset.jsonl, training/train_qlora.py, chat-widget, or chatbot-related tests.
---

# RadCrew chatbot

Cursor agent skills do **not** run in the production chatbot. They guide edits to this subsystem only.

## Architecture

```
Browser (chat-widget) → POST /chat (SSE) → chat.generate_chat_stream
  → LangGraph: route → feedback | rag → END
```

| Piece | Path |
|-------|------|
| HTTP + SSE | `backend/app/api/chat.py` |
| Stream entry + KB state | `backend/app/chatbot/chat.py` |
| Graph compile | `backend/app/chatbot/graph/build.py` |
| Feedback routing (HF JSON schema) | `backend/app/chatbot/graph/nodes/feedback_router/` |
| Feedback submit | `backend/app/chatbot/graph/nodes/feedback_handler/` |
| RAG answer + prompt + cache | `backend/app/chatbot/graph/nodes/rag_answer/` |
| HF generate / embeddings | `backend/app/chatbot/huggingface/` |
| Static KB | `backend/app/chatbot/knowledge/site_content.py` |
| GitHub MD KB (startup) | `backend/app/chatbot/knowledge/github_loader/` |
| Lifespan loads chunks | `backend/app/core/lifespan.py` |
| Request models | `backend/app/schemas.py` (`ChatRequest`, history max 12) |
| User-facing copy | `backend/app/chatbot/messages.py` |
| Frontend client | `frontend/src/lib/chatbot-api.ts`, `frontend/src/components/chat-widget/` |

**Routing:** `feedback_router_node` tries structured feedback tool-call routing; on failure or no match → `rag_answer_node`.

**RAG:** Retrieves top chunks via embeddings (`rag_answer/retrieval.py`), builds prompt (`rag_answer/prompt.py`), streams via `generate_answer` with optional response cache.

## Do not break

- Answers must stay **grounded** in conversation history + retrieved context only (see `build_chat_prompt` rules).
- Insufficient context → suggest **code@radcrew.org** (see `MSG_FALLBACK_LOW_CONTEXT` / prompt text).
- Do not infer person names from source titles; names must appear in source body text.
- Final answers: simple Markdown, `-` bullets (not `*`), no URLs/links in replies.
- `POST /chat` contract: SSE events `{"type":"chunk","content":...}` then `{"type":"done"}`.
- Without `HF_TOKEN`, stream returns `MSG_AI_UNAVAILABLE` only.

## Dev commands

From repo root:

```bash
yarn dev              # frontend + API
yarn dev:backend      # Uvicorn reload on backend
yarn test:backend     # pytest app/tests
```

API default: `http://localhost:8787`. Frontend: `VITE_CHATBOT_API_BASE_URL`.

Full env and GitHub KB setup: `backend/README.md`. Monorepo overview: root `README.md`.

## QLoRA feedback-router training

- Dataset: `training/trainset.jsonl` — one JSON object per line: `message` (string), `is_feedback` (boolean). Example: `training/trainset_example.jsonl`.
- Train script: `training/train_qlora.py` → output `training/outputs/qlora-feedback-router/`.
- **Windows:** set `PYTHONUTF8=1` before starting Python (TRL import). Prefer `training/run_train.ps1` from repo root.
- Details: `training/README.md`.

## When changing behavior

1. **Prompt / tone / formatting** → `graph/nodes/rag_answer/prompt.py` (and keep parity intent with any TS references noted in file headers).
2. **Retrieval** → `rag_answer/retrieval.py`, embedding settings in `app/core/settings.py`.
3. **New user intent branch** → extend `graph/build.py` + new node; mirror feedback router pattern if structured routing is needed.
4. **More site facts** → `knowledge/site_content.py` or GitHub Markdown under configured `GITHUB_*` env vars.
5. **API shape** → `schemas.py`, `chat.py`, `frontend/src/lib/chatbot-api.ts`, widget types — keep in sync.
6. **Tests** → `backend/app/tests/test_chat.py`, `test_huggingface.py`, `test_github_loader.py`, `test_site_content.py`.

## Scope discipline

- Minimize diffs; do not refactor unrelated frontend or CI unless asked.
- Do not commit secrets (`.env`, `HF_TOKEN`, `GITHUB_TOKEN`).
- Cursor **agent skills** are not loaded at runtime; user-facing “skills” = knowledge docs + graph/prompt logic.
