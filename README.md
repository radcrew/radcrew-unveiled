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
- `FRONTEND_ORIGIN`: frontend origin (default `http://localhost:8080`)

## Chatbot flow

- Browser calls `POST /chat` on the backend URL (`VITE_CHATBOT_API_BASE_URL`, default `http://localhost:8787`)
- The API retrieves snippets from static site copy
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
