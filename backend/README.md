# RadCrew Unveiled — Backend (FAQ chatbot API)

FastAPI service served with Uvicorn. It powers chat completion, retrieval (static site copy and optional GitHub Markdown), and related endpoints.

## Layout

- `app/main.py` — FastAPI app wiring (routers + middleware).
- `app/api/` — HTTP routers (`health`, `chat`).
- `app/chatbot/` — Assistant logic:
  - `chat.py` — knowledge state and the stream entry point
  - `llm.py` — provider-neutral inference entry point (see [Chat provider](#chat-provider))
  - `messages.py` — user-facing copy (fallbacks, confirmations)
  - `graph/` — the LangGraph: guardrail → route → feedback | RAG
  - `knowledge/` — static site copy, GitHub Markdown loader, cached embeddings
  - `guardrails/` — NeMo input/output rails
  - `huggingface/`, `openrouter/` — the two inference backends
  - `deepsearch/` — web-search fallback
  - `utils/` — stream helpers
- `app/core/` — `settings.py` (`Settings`, `get_settings`), `http.py` (CORS + rate limit), `lifespan.py` (startup knowledge load), `logger.py`.
- `app/schemas.py` — request/response models (`ChatRequest`, history capped at 12).
- `app/tests/` — Pytest suite (`pytest.ini` uses `testpaths = app/tests`).

## Endpoints

- `POST /chat` — Server-Sent Events. Emits `{"type":"chunk","content":...}` per token, then `{"type":"hints","hints":[...]}` when the answer completed and has follow-up suggestions, then `{"type":"done"}`. Request body is `ChatRequest` (`message` 2–1500 chars, `history` up to 12 turns).
- `GET /health` — readiness plus the two config facts that explain most outages:

  ```json
  { "ok": true, "chunks": 10, "provider": "openrouter", "embeddings": true }
  ```

  `provider` is `openrouter`, `huggingface`, or `none` (no credential set, so
  chat cannot answer). `embeddings` is false when `HF_TOKEN` is absent, meaning
  retrieval has dropped to lexical matching. Check this first when a deployed
  instance responds but chat does not work. The endpoint is public and reports
  names and booleans only, never credentials or model ids.

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

Copy [`.env.example`](.env.example) to `.env` and set values as needed.

`app/core/settings.py` is the source of truth for every value below. If this table
and that file ever disagree, the file wins.

### Chat provider

Chat inference runs through `app/chatbot/llm.py`, which picks a backend from
whichever credential is set. There is no provider switch to flip:

| Credential set | Provider used |
| --- | --- |
| `OPENROUTER_API_KEY` | OpenRouter (wins even if `HF_TOKEN` is also set) |
| `HF_TOKEN` only | Hugging Face Inference |
| neither | none; `/chat` replies that the assistant is unavailable |

OpenRouter wins the tie because it is the explicit opt-in, while `HF_TOKEN` may be
present purely to keep embeddings working.

**Embeddings are Hugging Face only.** OpenRouter has no embeddings endpoint, so
running OpenRouter-only is supported but leaves the corpus unembedded and drops
retrieval to lexical keyword matching. For semantic retrieval, set `HF_TOKEN`
alongside `OPENROUTER_API_KEY`.

**Model ids are not interchangeable.** `HUGGINGFACE_MODEL` takes Hub ids
(`Qwen/Qwen2.5-7B-Instruct`); `OPENROUTER_MODEL` takes OpenRouter slugs
(`qwen/qwen-2.5-7b-instruct`).

### Environment variables

**Server**

- `PORT`: listen port (default `8787`)
- `RATE_LIMIT`: per-client request budget, slowapi syntax (default `25/minute`)
- `FRONTEND_ORIGIN`: single allowed browser origin for CORS (default `https://radcrew.org`)
- `FRONTEND_ORIGINS`: optional comma-separated list (e.g. `https://radcrew.org,https://www.radcrew.org`). When set and non-empty, CORS uses this list instead of `FRONTEND_ORIGIN`. Set this on Vercel for production if the site and API are on different hosts. A rejected origin gets HTTP **400 "Disallowed CORS origin"**, which looks like a malformed request rather than a config error.

**Hugging Face**

- `HF_TOKEN`: access token ([hf.co/settings/tokens](https://huggingface.co/settings/tokens)). A depleted account returns HTTP 402 and the chat stream fails
- `HUGGINGFACE_MODEL`: Hub model id for chat (default `Qwen/Qwen2.5-7B-Instruct`)
- `HUGGINGFACE_PROVIDER`: which [Inference Provider](https://huggingface.co/docs/inference-providers) to use (default `auto`)
- `HUGGINGFACE_EMBEDDING_MODEL`: Hub model id for retrieval embeddings (default `sentence-transformers/all-MiniLM-L6-v2`)
- `HUGGINGFACE_EMBEDDING_PROVIDER`: provider for embedding inference (default `hf-inference`)

**OpenRouter**

- `OPENROUTER_API_KEY`: API key ([openrouter.ai/keys](https://openrouter.ai/keys)). Setting this selects OpenRouter for chat
- `OPENROUTER_MODEL`: OpenRouter model slug (default `qwen/qwen-2.5-7b-instruct`)
- `OPENROUTER_BASE_URL`: API base (default `https://openrouter.ai/api/v1`)

**Guardrails** (all default `true`)

- `GUARDRAIL_INPUT_PATTERNS_ENABLED`: Colang jailbreak/off-topic patterns. Regex only, no inference cost
- `GUARDRAIL_OUTPUT_PII_ENABLED`: redacts phone numbers from replies. Regex only, no inference cost
- `GUARDRAIL_INPUT_HARMFUL_ENABLED`: harmful-content classifier. **Costs one extra inference call**
- `GUARDRAIL_OUTPUT_GROUNDEDNESS_ENABLED`: checks the answer against retrieved context. **Costs one extra inference call**

With both LLM-backed rails on, a single `/chat` makes up to **three** inference
calls. That was cheap on a free tier; on a metered provider it is 3× per message,
and it triples the time a serverless function must stay alive. Turning the two
LLM-backed rails off leaves the regex rails working at no cost.

**Knowledge base (optional GitHub Markdown)**

- `GITHUB_REPO_URL`: repo URL for startup-time Markdown ingestion (example: `https://github.com/acme/private-knowledge`)
- `GITHUB_TOKEN`: GitHub PAT (required when `GITHUB_PRIVATE_REPO=true`)
- `GITHUB_BRANCH`: branch or ref for the Git tree API (required when `GITHUB_REPO_URL` is set; example: `main`)
- `GITHUB_PATH`: optional repo subdirectory prefix to ingest (example: `docs/knowledge`)
- `GITHUB_PRIVATE_REPO`: set to `true` to enforce token usage for private repository ingestion

**Feedback forwarding**

- `COMPANY_FEEDBACK_EMAIL`: where user feedback is sent (default `code@radcrew.org`)
- `WEB3FORMS_ACCESS_KEY`: [Web3Forms](https://web3forms.com) key used to deliver it

**Retrieval and deep search**

- `RETRIEVAL_FALLBACK_SIMILARITY_THRESHOLD`: below this best-match score, retrieval switches from semantic to lexical keyword matching (default `0.25`)
- `DEEP_SEARCH_SIMILARITY_THRESHOLD`: below this, the web fallback runs (default `0.30`)
- `DEEP_SEARCH_ENABLED`: enable the web-search fallback (default `true`; only active when `WEB_SEARCH_API_KEY` is set)
- `WEB_SEARCH_PROVIDER`: web-search provider (default `tavily`)
- `WEB_SEARCH_API_KEY`: API key for the search provider. Without it, deep search stays inert and the bot answers from the knowledge base only
- `WEB_SEARCH_MAX_RESULTS`: max results pulled per deep search (default `5`)

**Vector store**

- `DATABASE_URL`: Postgres with the `pgvector` extension, holding the corpus embeddings. Optional: without it the corpus is embedded into process memory at startup, so every cold start re-embeds it and spends embedding calls on unchanged content. On serverless use a pooled endpoint (Neon pooler, Supabase port 6543) and `?sslmode=require`
- `EMBEDDING_BATCH_SIZE`: texts per embedding call while indexing (default `64`)

> The embedding dimension is fixed in the table when it is created, so `DATABASE_URL` and `HUGGINGFACE_EMBEDDING_MODEL` are a single decision. Changing the model means altering the column and re-embedding the whole corpus; the stored model id is part of the freshness check, so a changed model re-embeds rather than silently comparing vectors from two different models.

### Deep search (web-search fallback)

When the static knowledge base can't confidently answer a question (best retrieval
similarity below `DEEP_SEARCH_SIMILARITY_THRESHOLD`), the chatbot can fall back to a
web search and answer from those results. It is **off unless `WEB_SEARCH_API_KEY` is
set**, so by default behavior is unchanged. To enable with [Tavily](https://tavily.com):

1. Get an API key from your search provider.
2. In `backend/.env`, set `WEB_SEARCH_API_KEY=<your_key>` (and optionally `WEB_SEARCH_PROVIDER`).
3. Restart the backend.

Note: deep search answers from external results, so they are less controlled than
knowledge-base answers. For facts you want answered reliably (e.g. official links),
prefer adding them to the knowledge base.

### Private GitHub repo knowledge setup

1. Generate a GitHub personal access token (classic or fine-grained) that can read repository contents.
2. In `backend/.env`, set:
   - `GITHUB_REPO_URL=https://github.com/<owner>/<repo>`
   - `GITHUB_PRIVATE_REPO=true`
   - `GITHUB_TOKEN=<your_token>`
3. Set `GITHUB_BRANCH` (e.g. `main`) and optionally `GITHUB_PATH` if Markdown lives under a subdirectory.
4. Restart the backend (`yarn dev:backend` or `yarn dev` from the repo root) so startup ingestion reloads from GitHub.

## Development

From the **repository root** (uses the monorepo script):

```bash
yarn dev:backend
```

This runs Uvicorn with reload on `backend` (see root `package.json`).

With the virtual environment activated and dependencies installed, you can also run Uvicorn from this directory:

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8787 --reload --reload-dir app
```

## How the chatbot API fits in

- The browser calls `POST /chat` on the backend URL (`VITE_CHATBOT_API_BASE_URL` in the frontend, default `http://localhost:8787`).
- The API retrieves snippets from static site copy and optional GitHub Markdown.
- The configured provider (OpenRouter or Hugging Face) streams a grounded answer back over SSE.
- Weak retrieval (with no prior conversation history) returns a safe fallback with contact guidance.

## Tests

From the repository root:

```bash
yarn test:backend
```

Or from `backend` with the venv active:

```bash
cd backend
python -m pytest app/tests
```

## Production

There is no separate compile step beyond installing dependencies. Run Uvicorn (or your process manager) against `app.main:app` with working directory `backend`:

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8787
```

From the repo root, `yarn build:backend` runs `compileall` on `backend/app` as a quick syntax check only.
