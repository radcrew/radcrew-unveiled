# RadCrew Unveiled

Monorepo: Vite React site (`frontend`) and FAQ chatbot API (`backend`, FastAPI + Uvicorn).

## Prerequisites

- **Node.js** (for the frontend; npm workspaces)
- **Python 3.11+** (for the chat API)

## Install

From the repository root:

```bash
npm install
```

Create a virtual environment for the API (recommended), then install Python dependencies:

```bash
cd backend
python -m venv .venv
```

Activate the venv — on Windows (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

Then:

```bash
pip install -r requirements.txt
cd ..
```

## Dev (frontend + API)

From the repo root, one command starts both the Vite app and the chat API:

```bash
npm run dev
```

- **Frontend only:** `npm run dev:frontend`
- **API only:** `npm run dev:backend` (runs Uvicorn with reload on `backend`)

- Env: copy [`frontend/.env.example`](frontend/.env.example) to `frontend/.env` and set chat API URL as needed.
- Env: copy [`backend/.env.example`](backend/.env.example) to `backend/.env` for the API (Hugging Face token, etc.).

### API env vars

- `HUGGINGFACE_API_KEY`: Hugging Face access token ([hf.co/settings/tokens](https://huggingface.co/settings/tokens)); you can use `HF_TOKEN` instead if you already have that set
- `HUGGINGFACE_MODEL`: Hub model id for chat (default `Qwen/Qwen2.5-1.5B-Instruct`)
- `HUGGINGFACE_PROVIDER`: which [Inference Provider](https://huggingface.co/docs/inference-providers) to use (default `hf-inference`; try `auto` if you see HTTP 400 from the router)
- `HUGGINGFACE_EMBEDDING_MODEL`: Hub model id for semantic retrieval embeddings (default `sentence-transformers/all-MiniLM-L6-v2`)
- `HUGGINGFACE_EMBEDDING_PROVIDER`: provider for embedding inference (default `hf-inference`)
- `FRONTEND_ORIGIN`: frontend origin (default `http://localhost:8080`)
- `GITHUB_KB_REPO_URL`: optional GitHub repo URL used for startup-time Markdown ingestion (example: `https://github.com/acme/private-knowledge`)
- `GITHUB_KB_TOKEN`: optional GitHub PAT used for GitHub API requests (required when `GITHUB_KB_PRIVATE_REPO=true`)
- `GITHUB_KB_BRANCH`: optional branch or ref to ingest (defaults to repository default branch)
- `GITHUB_KB_PATH`: optional repo subdirectory prefix to ingest (example: `docs/knowledge`)
- `GITHUB_KB_PRIVATE_REPO`: set to `true` to enforce token usage for private repository ingestion
- `CONTENTFUL_SPACE_ID`, `CONTENTFUL_DELIVERY_TOKEN`, `CONTENTFUL_ENVIRONMENT`: Content Delivery API credentials (mirror the frontend `VITE_CONTENTFUL_*` values in `backend/.env` so the API can ingest entries at startup)
- `CONTENTFUL_RAG_CONTENT_TYPES`: comma-separated Contentful content type ids to include in RAG (default `engineers`)

### Private GitHub repo knowledge setup

1. Generate a GitHub personal access token (classic or fine-grained) that can read repository contents.
2. In `backend/.env`, set:
   - `GITHUB_KB_REPO_URL=https://github.com/<owner>/<repo>`
   - `GITHUB_KB_PRIVATE_REPO=true`
   - `GITHUB_KB_TOKEN=<your_token>`
3. Optionally set `GITHUB_KB_BRANCH` and/or `GITHUB_KB_PATH` if your Markdown docs live outside default branch root.
4. Restart the backend (`npm run dev:backend` or `npm run dev`) so startup ingestion reloads from GitHub.

## Chatbot flow

- Browser calls `POST /chat` on the backend URL (`VITE_CHATBOT_API_BASE_URL`, default `http://localhost:8787`)
- The API retrieves snippets from static site copy, optional Contentful entries, and optional GitHub Markdown
- Hugging Face chat completion (with text-generation fallback) produces grounded answers
- Low retrieval confidence returns a safe fallback with contact guidance

## Tests

```bash
npm test
npm run test:backend
```

The Python suite runs from `backend` (pytest).

## Lint

Run from the repository root:

```bash
npm run lint
```

## Production API

There is no separate compile step for the Python service beyond installing dependencies. Run Uvicorn (or your process manager) against `app.main:app` with working directory `backend`, for example:

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8787
```

`npm run build:backend` runs `compileall` on `backend/app` as a quick syntax check only.
