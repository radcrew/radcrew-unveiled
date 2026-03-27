# RadCrew Unveiled

Monorepo: Vite React site (`frontend`) and FAQ chatbot API (`backend`).

## Install

From the repository root:

```bash
npm install
```

## Frontend

```bash
npm run dev
```

- Env: copy [`frontend/.env.example`](frontend/.env.example) to `frontend/.env` and set Contentful and chat API URL as needed.

## Chatbot backend

```bash
npm run dev:backend
```

- Env: copy `backend/.env.example` to `backend/.env`.

### Backend env vars

- `HUGGINGFACE_API_KEY`: Hugging Face access token ([hf.co/settings/tokens](https://huggingface.co/settings/tokens)); you can use `HF_TOKEN` instead if you already have that set
- `HUGGINGFACE_MODEL`: Hub model id for chat (default `Qwen/Qwen2.5-1.5B-Instruct`)
- `FRONTEND_ORIGIN`: frontend origin (default `http://localhost:8080`)
- `CONTENTFUL_SPACE_ID` and `CONTENTFUL_DELIVERY_TOKEN` (optional; richer FAQ context)

## Chatbot flow

- Browser calls `POST /chat` on the backend URL (`VITE_CHATBOT_API_BASE_URL`, default `http://localhost:8787`)
- Backend retrieves snippets from static site copy + Contentful
- Hugging Face `chatCompletion` produces grounded answers
- Low retrieval confidence returns a safe fallback with contact guidance

## Tests

```bash
npm test
npm run test:backend
```

## Lint

Run from the repository root:

```bash
npm run lint
```
