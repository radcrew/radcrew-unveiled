# Architecture

RadCrew Unveiled is a monorepo with three independent parts. The frontend and
backend run together in development and ship to production; the training package
is an offline tool that is not part of the runtime.

```
┌──────────────┐      POST /chat      ┌──────────────────────────────┐
│  frontend    │  ───────────────────▶ │  backend (FastAPI / Uvicorn) │
│  Vite + React│                       │                              │
│              │  ◀─────────────────── │  retrieval → grounded answer │
└──────────────┘   grounded answer     └──────────────┬───────────────┘
                                                       │
                                              Hugging Face inference
                                       (chat completion, text-gen fallback)

  training/  ──▶  QLoRA adapter (offline; informs the feedback-routing model)
```

## Components

### `frontend/` — Vite + React site

The public-facing site, including the chatbot UI. It calls the backend at
`VITE_CHATBOT_API_BASE_URL` (default `http://localhost:8787`). Built with Vite
and deployed as static output (`frontend/dist`) via Vercel — see
[`vercel.json`](../vercel.json). Source layout under `frontend/src`: `components`,
`pages`, `hooks`, `lib`, `data`, `assets`.

### `backend/` — FastAPI chat API

The chatbot API. `app/main.py` mounts the `health` and `chat` routers plus shared
middleware (CORS, rate limiting) configured via `app/core/settings.py`. The
`chat` flow retrieves snippets from static site copy and optional GitHub Markdown,
then asks Hugging Face for a grounded answer (with a text-generation fallback and
a safe contact-guidance fallback on weak retrieval).

App layout under `backend/app`: `api` (routers), `chatbot` (retrieval + answer
logic), `core` (settings, HTTP app, logging), `schemas.py` (request/response
models), `tests`. Deeper write-ups live in [`backend/docs/`](../backend/docs/).

### `training/` — QLoRA feedback router

An **offline** SFT pipeline that trains a small `message` → `is_feedback`
classifier. It is not imported by the backend at runtime; it produces an adapter
that informs feedback routing. Requires an NVIDIA GPU (Linux/WSL recommended).
See [`training/README.md`](../training/README.md).

## Request flow (chat)

1. Browser sends `POST /chat` to the backend URL.
2. The API retrieves relevant snippets from static site copy and optional GitHub
   Markdown.
3. Hugging Face chat completion (with text-generation fallback) produces a
   grounded answer.
4. Weak retrieval with no prior conversation history returns a safe fallback with
   contact guidance.

## Deployment

- **Frontend** — static build (`frontend/dist`) served by Vercel; SPA rewrites
  route all paths to `index.html`.
- **Backend** — Uvicorn (see [`backend/README.md`](../backend/README.md#production)
  and `backend/vercel.json`).
