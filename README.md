# RadCrew Unveiled

Monorepo: Vite React site (`frontend`) and FAQ chatbot API (`backend`, FastAPI + Uvicorn).

## Prerequisites

- **Node.js** — see [frontend/README.md](frontend/README.md)
- **Python 3.11+** — see [backend/README.md](backend/README.md)

## Install

From the repository root:

```bash
npm install
```

- **Frontend** (Vite, env vars, build, tests, lint): **[frontend/README.md](frontend/README.md)**
- **Backend** (Python venv, `pip install`, API env): **[backend/README.md](backend/README.md)**

## Dev (frontend + API)

From the repo root, one command starts both the Vite app and the chat API:

```bash
npm run dev
```

- **Frontend only:** `npm run dev:frontend`
- **API only:** `npm run dev:backend` (runs Uvicorn with reload on `backend`)

Environment files live in `frontend/.env` and `backend/.env` (copy from each package’s `.env.example`). Details: [frontend/README.md](frontend/README.md#configuration), [backend/README.md](backend/README.md#configuration).

## Chatbot flow

- Browser calls `POST /chat` on the backend URL (`VITE_CHATBOT_API_BASE_URL`, default `http://localhost:8787`)
- The API retrieves snippets from static site copy and optional GitHub Markdown
- Hugging Face chat completion (with text-generation fallback) produces grounded answers
- Weak retrieval (with no prior conversation history) returns a safe fallback with contact guidance

## Tests

```bash
npm test
npm run test:backend
```

- Frontend (Vitest): [frontend/README.md](frontend/README.md#tests)
- Backend (pytest): [backend/README.md](backend/README.md#tests)

## Lint

```bash
npm run lint
```

See [frontend/README.md](frontend/README.md#lint).

## Production

- **Frontend build / preview:** [frontend/README.md](frontend/README.md#build-and-preview)
- **API (Uvicorn):** [backend/README.md](backend/README.md#production)

`npm run build:backend` runs `compileall` on `backend/app` as a quick syntax check only.
