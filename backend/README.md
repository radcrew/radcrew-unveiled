# RadCrew Unveiled — Backend (FAQ chatbot API)

FastAPI service served with Uvicorn. It powers chat completion, retrieval (static copy, optional Contentful, optional GitHub Markdown), and related endpoints.

## Prerequisites

- **Python 3.11+**

## Install

From the repository root:

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
```

## Configuration

Copy [`.env.example`](.env.example) to `.env` and set values as needed (Hugging Face token, optional GitHub / Contentful, etc.).

### Environment variables

- `HUGGINGFACE_API_KEY`: Hugging Face access token ([hf.co/settings/tokens](https://huggingface.co/settings/tokens)); you can use `HF_TOKEN` instead if you already have that set
- `HUGGINGFACE_MODEL`: Hub model id for chat (default `Qwen/Qwen2.5-1.5B-Instruct`)
- `HUGGINGFACE_PROVIDER`: which [Inference Provider](https://huggingface.co/docs/inference-providers) to use (default `hf-inference`; try `auto` if you see HTTP 400 from the router)
- `HUGGINGFACE_EMBEDDING_MODEL`: Hub model id for semantic retrieval embeddings (default `sentence-transformers/all-MiniLM-L6-v2`)
- `HUGGINGFACE_EMBEDDING_PROVIDER`: provider for embedding inference (default `hf-inference`)
- `FRONTEND_ORIGIN`: frontend origin (default `http://localhost:8080`)
- `GITHUB_KB_REPO_URL`: optional GitHub repo URL used for startup-time Markdown ingestion (example: `https://github.com/acme/private-knowledge`)
- `GITHUB_KB_TOKEN`: optional GitHub PAT used for GitHub API requests (required when `GITHUB_KB_PRIVATE_REPO=true`)
- `GITHUB_KB_BRANCH`: branch or ref for the Git tree API (required when `GITHUB_KB_REPO_URL` is set; example: `main`)
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
3. Set `GITHUB_KB_BRANCH` (e.g. `main`) and optionally `GITHUB_KB_PATH` if Markdown lives under a subdirectory.
4. Restart the backend (`npm run dev:backend` or `npm run dev` from the repo root) so startup ingestion reloads from GitHub.

## Development

From the **repository root** (uses the monorepo script):

```bash
npm run dev:backend
```

This runs Uvicorn with reload on `backend` (see root `package.json`).

With the virtual environment activated and dependencies installed, you can also run Uvicorn from this directory:

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8787 --reload --reload-dir app
```

## How the chatbot API fits in

- The browser calls `POST /chat` on the backend URL (`VITE_CHATBOT_API_BASE_URL` in the frontend, default `http://localhost:8787`).
- The API retrieves snippets from static site copy, optional Contentful entries, and optional GitHub Markdown.
- Hugging Face chat completion (with text-generation fallback) produces grounded answers.
- Weak retrieval (with no prior conversation history) returns a safe fallback with contact guidance.

## Tests

From the repository root:

```bash
npm run test:backend
```

Or from `backend` with the venv active:

```bash
cd backend
python -m pytest
```

## Production

There is no separate compile step beyond installing dependencies. Run Uvicorn (or your process manager) against `app.main:app` with working directory `backend`:

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8787
```

From the repo root, `npm run build:backend` runs `compileall` on `backend/app` as a quick syntax check only.
