# Architecture

RadCrew Unveiled is a monorepo with three independent parts. The frontend and
backend run together in development and ship to production; the training package
is an offline tool that is not part of the runtime.

```
┌──────────────┐   POST /chat (SSE)   ┌──────────────────────────────┐
│  frontend    │ ───────────────────▶ │  backend (FastAPI / Uvicorn) │
│  Vite + React│                      │                              │
│              │ ◀─────────────────── │  LangGraph:                  │
└──────────────┘  streamed answer     │   guardrail → route          │
                                      │     ├── feedback → submit    │
                                      │     └── rag → retrieve →     │
                                      │            answer → rails    │
                                      └──────────────┬───────────────┘
                                                     │
                                         app/chatbot/llm.py
                                    ┌────────────────┴────────────────┐
                                    │                                 │
                             OpenRouter                        Hugging Face
                        (if OPENROUTER_API_KEY)              (if HF_TOKEN only)

  Embeddings are always Hugging Face (OpenRouter has no embeddings endpoint).
  training/  ──▶  QLoRA adapter (offline; informs the feedback-routing model)
```

## Components

### `frontend/` — Vite + React site

The public-facing site, including the chatbot UI. It calls the backend at
`VITE_CHATBOT_API_BASE_URL` (default `http://localhost:8787`). Built with Vite
and deployed as static output (`frontend/dist`) via Vercel — see
[`vercel.json`](../vercel.json). Source layout under `frontend/src`: `components`,
`pages`, `hooks`, `lib`, `assets`, `test`.

### `backend/` — FastAPI chat API

The chatbot API. `app/main.py` mounts the `health` and `chat` routers plus shared
middleware (CORS, rate limiting) configured via `app/core/settings.py`. The
`chat` flow runs a LangGraph: input guardrails, then intent routing to either
feedback submission or the RAG path, which retrieves snippets from static site
copy and optional GitHub Markdown, streams a grounded answer from the configured
provider, and applies output rails (groundedness, PII scrubbing). Weak retrieval
falls back to safe contact guidance.

App layout under `backend/app`: `api` (routers), `chatbot` (graph, retrieval,
providers, guardrails), `core` (settings, HTTP app, lifespan, logging),
`schemas.py` (request/response models), `tests`. Deeper write-ups live in
[`backend/docs/`](../backend/docs/) and [`backend/README.md`](../backend/README.md).

### `training/` — QLoRA feedback router

An **offline** SFT pipeline that trains a small `message` → `is_feedback`
classifier. It is not imported by the backend at runtime; it produces an adapter
that informs feedback routing. Requires an NVIDIA GPU (Linux/WSL recommended).
See [`training/README.md`](../training/README.md).

## Request flow (chat)

1. Browser sends `POST /chat` to the backend URL and reads a Server-Sent Events
   stream: `{"type":"chunk","content":...}` events, then `{"type":"done"}`.
2. Input guardrails run; a block ends the turn immediately.
3. The router classifies the message as feedback or a question. Feedback is
   confirmed and forwarded by email; questions continue to RAG.
4. Retrieval pulls relevant snippets. Below the similarity thresholds it falls
   back first to lexical matching, then optionally to a web search.
5. The configured provider (OpenRouter or Hugging Face) streams the answer, which
   passes through the output rails before reaching the browser.
6. Weak retrieval with no prior conversation history returns a safe fallback with
   contact guidance.

## Deployment

- **Frontend** — static build (`frontend/dist`) served by Vercel; SPA rewrites
  route all paths to `index.html`.
- **Backend** — Uvicorn (see [`backend/README.md`](../backend/README.md#production)
  and `backend/vercel.json`).
