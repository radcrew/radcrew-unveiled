# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

@AGENTS.md

The import above pulls in the cross-tool non-negotiables and command baseline from [AGENTS.md](./AGENTS.md), shared with other coding agents (Cursor, Codex, etc.). Everything below is Claude Code specific.

## What this is

`radcrew-unveiled` is the RadCrew marketing site plus the FAQ chatbot that answers questions about the agency. Two runtime parts: a Vite/React frontend (`frontend/`) and a FastAPI chat API (`backend/`), plus an offline QLoRA training pipeline (`training/`) that is not part of the runtime. Both runtime parts deploy to Vercel as separate projects. Live site: https://radcrew.org.

## Working Guidelines

**Think before coding.** State assumptions explicitly rather than silently picking between interpretations. If a request is ambiguous, or a simpler approach exists than the one implied, say so before implementing, especially around the chatbot's grounding rules and the SSE contract, where a wrong guess ships a silently broken chat.

**Simplicity first.** No speculative abstractions, no unrequested configurability, no error handling for scenarios that can't occur at the call site. If a change could be half the size, make it that size.

**Surgical changes.** Touch only what the task requires; match each file's existing style even where you'd choose differently. When your edit makes an import, variable, or function unused, remove it, but leave pre-existing dead code alone and just flag it.

**Goal-driven execution.** For multi-step work, state a short plan with a verification step per item, for example "add the retrieval threshold guard, then verify with `python -m pytest app/tests/test_retrieval.py`". Use the smallest command from the table below that actually exercises the change, not both suites, unless the change spans them.

**Loops and autonomy.** "Done" means the relevant command from the table below passes, not "looks right." Work on a branch so changes are easy to revert. Autonomous or `/loop`-driven runs need an explicit stop condition (a passing test, a clean lint run) and an iteration cap; don't loop indefinitely on judgment calls like prompt tone or visual design, those are a human call. If you hit the cap or get stuck, stop and report what you tried and what's blocking, rather than thrashing or guessing further.

**Text.** In commit messages, PR descriptions, and docs written for this repo: no em-dashes, no filler ("it's worth noting," "essentially"), no LLM tells ("it's not just X, it's Y," "delve"). Reread before finishing and cut anything that doesn't earn its place.

**Commit messages.** After *every* response in which you change one or more files, not just at the end of a multi-step task and not just when asked, automatically draft and show a Conventional Commits message in a copyable code block. Match this repo's history: lowercase `feat:`/`fix:`/`chore:`/`docs:` prefix, imperative mood, no scope in most commits. This applies even to small incremental edits (a single CSS tweak, a one-line fix) made in response to iterative follow-up requests. Scope it to the actual uncommitted change set (check `git status`) and call out any unrelated modified files so they can be excluded. Do not run `git commit` yourself; the user commits manually unless they explicitly ask you to.

**Pull requests.** Follow [.github/PULL_REQUEST_TEMPLATE.md](./.github/PULL_REQUEST_TEMPLATE.md) and keep to its sections. Do not tick the test checkbox unless you actually ran the suites and saw them pass. Remember that opening the PR triggers a Vercel preview deploy on both projects.

## Commands

Package manager is **Yarn 1 classic**, pinned to `yarn@1.22.22` by the root `package.json` `packageManager` field. The backend is a separate Python venv, not managed by yarn. CI uses Node 22 and Python 3.11.

### Install / dev

```bash
yarn install                 # root, installs the frontend workspace
yarn dev                     # frontend + API concurrently
yarn dev:frontend            # Vite dev server, http://localhost:8080
yarn dev:backend             # Uvicorn reload on backend, http://localhost:8787
```

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1     # Windows; macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

> Every root script delegates through `yarn workspace frontend <script>`, and CI runs the root scripts rather than reaching into `frontend/`. One command shape everywhere, no `npm run -w` wrapper, no `working-directory` juggling in the workflow.

### Lint / test / build

| Side | lint | test | build | single test |
|---|---|---|---|---|
| `frontend` | `yarn lint` (root ESLint over `frontend/src`) | `yarn test` (Vitest) | `yarn build` (`vite build`) | `yarn workspace frontend test <path>` or `-t "<name>"` |
| `frontend` E2E | n/a | `yarn test:e2e` (Playwright, chromium) | n/a | `yarn workspace frontend test:e2e <path>` |
| `backend` | *(none)* | `cd backend && python -m pytest` | `python -m compileall -q app` (syntax check only) | `python -m pytest app/tests/test_retrieval.py -k "name"` |
| `training` | *(none)* | *(no suite)* | n/a | n/a |

Current baseline: frontend 33 Vitest tests, 6 Playwright tests, backend 281 pytest tests (plus 1 skipped without `DATABASE_URL` and 16 deselected `quality` cases), ESLint 0 errors with 9 pre-existing `react-refresh/only-export-components` warnings in `components/ui/`. `yarn lint` has no `--max-warnings 0`, so those warnings do not fail CI.

Do not run a hoisted binary straight from the root (`yarn vitest run <path>`). It resolves, because Yarn 1 hoists everything into the root `node_modules/.bin`, but it runs with the root as CWD and never loads `frontend/vitest.config.ts`, so there is no jsdom environment and no setup file. Pure-function tests still pass, which is what makes it dangerous. Always go through `yarn workspace frontend ...`.

Backend `pytest.ini` sets `testpaths = app/tests` and `asyncio_mode = auto`, so `python -m pytest` from `backend/` needs no arguments.

Two backend suites are excluded from that default run, both because they need something the runner does not have:

- `python -m pytest -m quality` is the retrieval golden set (`test_retrieval_quality.py`). It makes real embedding calls, about seventeen per run, and skips when no provider is configured. It is deselected by `addopts = -m "not quality"` so an ordinary test run costs nothing. Run it after changing chunking, the embedding model, or retrieval ranking; it is the only check that says whether the right document comes back rather than whether the plumbing works.
- The vector-store round trip in `test_vector_store.py` skips unless `DATABASE_URL` is set, and CI does not set it, so the SQL is only ever exercised by a local run against a real database. Run it after touching `vector_store.py`: the other tests there use a fake connection, which accepts a syntax error without complaint. Do not export `DATABASE_URL` for the whole suite: it flips every retrieval test onto the store path.

## Architecture

### Component map

| Component | Stack | Role |
|---|---|---|
| `frontend` | React 18, Vite 5, Tailwind, shadcn/ui, framer-motion, TanStack Query | Marketing site plus the chat widget |
| `backend` | FastAPI, Uvicorn, LangGraph, NeMo Guardrails, huggingface_hub | `POST /chat` (SSE) and `/health` |
| `training` | Python, QLoRA/TRL | Offline `message` to `is_feedback` classifier, not imported at runtime |

Frontend content is all hardcoded, across two shared files plus per-section constants. `frontend/src/components/home/static-data.ts` holds real copy shared between sections (`featuredProjects`, `faqs`); `frontend/src/components/home/placeholder-content.ts` holds invented placeholder copy (clients, testimonials, case-study metrics, journal posts) and is the file to replace when real content arrives.

Content used by exactly one section stays in that section instead: `capabilityCards` in `Capabilities.tsx`, `phases` in `Process.tsx`, `trackRecord` in `Hero.tsx`, `navLinks` in `Nav.tsx`, `footerLinks` in `Footer.tsx`, `techIcons` in `TechStack.tsx`. Grep for the copy you want to change rather than assuming the two shared files hold all of it. Contact and newsletter forms submit through Web3Forms.

Contentful was removed when the team section was dropped: it backed team member profiles only, and the section that rendered them is gone. There is no CMS in this project now.

### Request flow (`POST /chat`)

```
Browser (chat-widget) -> POST /chat (SSE) -> chat.generate_chat_stream
  -> LangGraph: guardrail_input -> route -> feedback | rag -> END
```

`GET /health` reports `{"ok", "chunks", "provider", "embeddings"}`. It is the fastest way to tell a deployed instance that cannot generate (`provider: "none"`) from one whose retrieval has quietly degraded (`embeddings: false`), both of which otherwise look identical from outside. It is public, so it must never gain a field carrying a credential, model id, or origin list.

`app/api/chat.py` wraps the generator in a `StreamingResponse` and emits `data: {"type":"chunk","content":...}` per token, then an optional `data: {"type":"hints","hints":[...]}`, then `data: {"type":"done"}`. Any exception raised while building the stream is caught and replaced with `MSG_AI_UNAVAILABLE`, so the endpoint never 500s. Request shape is `app/schemas.py`: `message` is 2 to 1500 chars, `history` is capped at 12 messages.

`chat.generate_chat_stream` returns a `ChatStream` (the chunk iterator plus the hints), not a bare iterator. The hints are the follow-up questions the widget renders as chips under the answer; `graph/nodes/rag_answer/hints.py` picks them from a curated catalog keyed by knowledge-document id, so they cost no inference call. Below `RETRIEVAL_FALLBACK_SIMILARITY_THRESHOLD` the matches came from lexical fallback and the node offers generic starters instead: answers tolerate weak retrieval because the prompt sees the whole corpus, but hints see only the retrieved list, so a contact question can otherwise surface portfolio chips. They are emitted only when the stream finished cleanly, and only the RAG node produces them: guardrail blocks and feedback replies leave `ChatState["hints"]` absent, so those turns carry no hints event. Unknown SSE event types are ignored by the client, which is what lets the two Vercel projects deploy independently.

### The graph

`app/chatbot/graph/build.py` compiles four nodes:

1. `guardrail_input` runs input rails; a block short-circuits straight to `END`.
2. `route` (`feedback_router/router.py`) attempts structured feedback classification via an HF tool-call/JSON-schema request. On failure or no match it routes to RAG, so a router outage degrades to normal answering rather than erroring.
3. `feedback` (`feedback_handler/`) submits the feedback and confirms.
4. `rag` (`rag_answer/`) retrieves, builds the prompt, streams the answer.

The router has several pre-LLM stages (`pregate.py`, `fuzzy.py`, `parse.py`, `confirm.py`) before it spends an inference call. Read those before adding another LLM round-trip to the hot path.

### Knowledge and retrieval

`app/core/lifespan.py` loads the corpus once at startup: static site copy (`knowledge/site_content.py`) plus optional GitHub Markdown (`knowledge/github_loader/`, gated on `GITHUB_*` env vars). It then indexes it, one of two ways depending on `DATABASE_URL`.

`knowledge/embeddings.py` keeps L2-normalized vectors in memory keyed by document id, so a request only embeds the short query and similarity is a local dot product. Everything degrades to zeros (and therefore to lexical matching) when `HF_TOKEN` or the embedding model is unset, rather than failing. Two thresholds gate the fallbacks, both in `settings.py`:

- Below `RETRIEVAL_FALLBACK_SIMILARITY_THRESHOLD` (0.25), retrieval switches from semantic to lexical keyword matching.
- Below `DEEP_SEARCH_SIMILARITY_THRESHOLD` (0.30), the web-search fallback runs.

### Vector store (optional)

With `DATABASE_URL` set, embeddings live in Postgres (`knowledge/vector_store.py`) instead of process memory. The in-memory path re-embeds the whole corpus on every process start, which on Vercel is every cold start, spending embedding calls on unchanged content. It is not a latency win: a pgvector query adds a network round trip that an in-memory dot product over ten documents does not need.

`knowledge/indexing.py` is the write path, at startup and via `python -m app.chatbot.knowledge.indexing [--force]`. A boot reads stored fingerprints and embeds only the chunks whose text *or embedding model* differs, so a normal boot writes nothing. The model belongs in that key because a content hash alone says "the text is unchanged", not "the vector is still valid": swap `HUGGINGFACE_EMBEDDING_MODEL` and every hash still matches while every vector is stale.

Rows are chunks, not documents (`knowledge/chunking.py`), because `all-MiniLM-L6-v2` truncates past 256 word pieces without saying so, which made everything after roughly the first thousand characters of a GitHub Markdown file invisible. Every static site document is well inside that limit and stays a single chunk whose embedded text is byte-for-byte what the in-memory path produced, so their scores do not move. `search` returns document ids, collapsing to each document's best chunk, which is what keeps hints and the confidence gate document-shaped.

Two safeguards exist because the store holds the only copy of the vectors: `delete_missing` refuses to run on an empty corpus (`document_id <> ALL('{}')` matches every row, and an empty corpus is a failed load far more often than an emptied knowledge base), and a failed embedding run keeps what is already stored rather than half-applying. Every store entry point fails open, so an unreachable database degrades to lexical matching exactly as a missing `HF_TOKEN` does.

`vector({384})` is fixed at table creation, so `DATABASE_URL` and `HUGGINGFACE_EMBEDDING_MODEL` are one decision. `/health` reports `vector_store` from the last indexing outcome rather than probing the database, keeping that public endpoint query-free.

### Deep search

`chatbot/deepsearch/web_search.py` is a Tavily-backed web fallback used only when the knowledge base can't confidently answer. It is inert unless `WEB_SEARCH_API_KEY` is set, so default behavior is knowledge-base-only. Its answers are less controlled than KB answers; facts that must be reliable belong in `site_content.py` or the GitHub Markdown KB, not in deep search.

### Guardrails

`chatbot/guardrails/` wraps NeMo Guardrails around the chat. Four independent toggles in `settings.py`, all defaulting on:

| Setting | Cost |
|---|---|
| `GUARDRAIL_INPUT_PATTERNS_ENABLED` | regex/Colang only, no inference |
| `GUARDRAIL_OUTPUT_PII_ENABLED` | regex only, no inference |
| `GUARDRAIL_INPUT_HARMFUL_ENABLED` | one extra inference round-trip |
| `GUARDRAIL_OUTPUT_GROUNDEDNESS_ENABLED` | one extra inference round-trip |

The two LLM-backed checks mean a single `/chat` request can make up to three inference calls. Both fail open by design (`check_harmful_input` returns False, `check_groundedness` returns True on any exception), so a transient provider error never silences a legitimate answer. `SentinelLLM` in `hf_llm_adapter.py` is a stub whose `__RAIL_PASS__` return signals "no input rail matched"; it is not a real model.

PII scrubbing is line-buffered (`scrub_pii_stream`) so it works on a token stream without buffering the whole answer. Phone numbers never span newlines, which is what makes that safe.

### Inference: two interchangeable backends

`chatbot/llm.py` is the only entry point anything should call. It exposes `generate_answer` (streaming) and `complete_json` (schema-constrained), and picks a backend from `Settings.llm_provider()`:

| Credential set | Provider |
|---|---|
| `OPENROUTER_API_KEY` | `openrouter` (wins if both are set) |
| `HF_TOKEN` only | `huggingface` |
| neither | `none`, and `/chat` answers `MSG_AI_UNAVAILABLE` without calling out |

OpenRouter wins the tie because it is the explicit opt-in, while `HF_TOKEN` may be present purely to keep embeddings alive.

`chatbot/huggingface/` streams with two fallback layers: chat-completion across the configured providers, then plain text-generation. `providers_to_try` tries the configured provider then `auto`. Note the text-generation fallback is dead weight for chat-tuned models: `Qwen/Qwen2.5-7B-Instruct` only supports the `conversational` task, so that path always fails and only adds an error line to the log.

Chat-completion gets `CHAT_COMPLETION_ATTEMPTS` (3) tries per provider with a linear backoff, because that dead fallback means one transient router error would otherwise cost the whole answer. A failure *after* content has been yielded is never retried: those chunks are already on the wire to the browser, so another attempt would append a second answer to a partial one. The answer ends where it broke instead.

Only 429, 5xx, and statusless transport errors are retried. A 402 (HF account out of included credits), 401/403, or 404 answers the same however often you ask, so those fail fast and also skip the text-generation fallback entirely; otherwise its "not supported for task text-generation" reply lands last in the log and buries the real cause. The raised `RuntimeError` carries the upstream message, so a depleted account reads as one.

`chatbot/openrouter/` talks to the OpenAI-compatible REST API over stdlib `urllib`, matching the GitHub loader and web search rather than adding an SDK. There is no provider ladder and no text-generation fallback, because OpenRouter is uniformly chat-completions and does its own upstream routing. Its stream is SSE: `data:` lines of JSON ending at `data: [DONE]`, interleaved with `: OPENROUTER PROCESSING` keepalive comments that must be skipped.

Both share `DETERMINISTIC_DECODING` (`temperature=0`, `top_p=1`, `seed=42`), so switching providers does not change answer style. OpenRouter forwards `seed` upstream but honouring it is model-dependent; `temperature=0` is what actually holds answers stable.

**Model ids are not portable.** `HUGGINGFACE_MODEL` takes Hub ids (`Qwen/Qwen2.5-7B-Instruct`); `OPENROUTER_MODEL` takes OpenRouter slugs (`qwen/qwen-2.5-7b-instruct`). Copying one into the other fails at request time.

**Embeddings never move.** OpenRouter has no embeddings endpoint, so `knowledge/embeddings.py` always uses Hugging Face. Running OpenRouter-only is supported, but with no `HF_TOKEN` the corpus goes unembedded and retrieval silently degrades to lexical keyword matching. For semantic retrieval, keep `HF_TOKEN` set alongside `OPENROUTER_API_KEY`.

> A depleted HF account returns `402 Payment Required` ("You have depleted your monthly included credits"), which surfaces as `RuntimeError: No inference provider could stream model ...`. That is a billing state, not a code fault, and it is what switching to OpenRouter is for.

### Frontend chat widget

`frontend/src/components/chat-widget/` owns the panel and the launcher. It coordinates with the mobile nav sheet through `src/lib/overlay-events.ts`, a window CustomEvent bus, because the two overlays live in separate React trees (`App.tsx` vs `home/Landing.tsx`) and cannot share props or context. The widget also holds refs to the panel and launcher to detect outside clicks; any test that mocks `framer-motion` must forward refs or every click reads as "outside" and closes the panel.

The newest answer's first hint is *armed* on the input: it becomes the placeholder, and Tab sends it. `activeHints` is derived once from the last message and feeds both the chips and the armed hint, so the placeholder can never disagree with the first chip. Tab is the key that moves focus out of an input, so the handler claims it only when nothing else could be meant (forward Tab, empty draft, hint present) and hands it back on Shift+Tab or the first typed character. The `kbd` badge and the `sr-only` `aria-describedby` text exist because a placeholder alone announces no key binding, and the placeholder is truncated at 38 characters since the panel is 360px wide.

Query the input by its `aria-label` ("Ask radcrew a question"), not by placeholder text, which is now variable. Only backend hints arm it; the three starter `SUGGESTIONS` deliberately do not, so a freshly opened panel keeps the default placeholder.

### Frontend component files

Pull a presentational piece out of a feature's `index.tsx` once it is self-contained: no props threaded from local state, no reads of the parent's closures. `chat-widget/TypingDots.tsx` is the shape to copy. `SuggestionChips` in `chat-widget/index.tsx` is the counter-example still inline, since both callers sit in that file.

Naming follows what the file exports, not the folder:

| Kind | Case | Examples |
|---|---|---|
| A React component | PascalCase, named after the component | `home/AnimatedCounter.tsx`, `home/Landing.tsx`, `chat-widget/TypingDots.tsx` |
| Anything else (types, data, hooks, helpers) | lowercase kebab | `chat-widget/types.ts`, `home/static-data.ts`, `home/motion.ts`, `lib/overlay-events.ts` |

`components/ui/` is vendored shadcn and stays kebab-case; do not rename it to match. A component file exports its component by name (`export const TypingDots`), not a default, so imports read the same everywhere and `react-refresh/only-export-components` stays quiet.

### Training

`training/` trains a small `message` to `is_feedback` classifier via QLoRA. Dataset is `trainset.jsonl` (one JSON object per line: `message` string, `is_feedback` boolean), example at `trainset_example.jsonl`, output under `training/outputs/`. Needs an NVIDIA GPU; on Windows set `PYTHONUTF8=1` before starting Python or the TRL import fails, and prefer `training/run_train.ps1`. Nothing under `backend/app/` imports any of this.

## Docs

`README.md`, `frontend/README.md`, `backend/README.md`, and `docs/architecture.md` were realigned with the source and are current as of the OpenRouter work. `backend/README.md` now carries the full environment table, the provider-selection rules, and the guardrail cost note.

`app/core/settings.py` remains authoritative for configuration. When you change a setting's name, default, or meaning, update `backend/README.md` and `backend/.env.example` in the same commit, or this section becomes the next thing to distrust.

`.cursor/skills/radcrew-chatbot/SKILL.md` was updated alongside them and is current; it stays the fastest orientation for the chatbot subsystem. `backend/docs/chatbot-improvements.md` is a tuning log rather than a spec, so treat it as history.

## Deployment and CI

Two Vercel projects, deployed by two workflows:

- `frontend.yml`: lint, test, Playwright E2E, build, then deploy from working directory `.`. The Vercel project's root directory must be the **repository root**, not `frontend/`, so install can see the lockfile.
- `backend.yml`: pytest, `compileall`, then deploy with Vercel root directory `./backend`.

Both deploy on `pull_request` (preview) and on push to `main` (production, via `--prod`). Runtime env vars are set in the Vercel project settings, not in CI; the workflows only carry `VERCEL_TOKEN`, `VERCEL_ORG_ID`, and the project ids.

> Root `vercel.json` drives the frontend deploy: `"installCommand": "yarn install --frozen-lockfile"`, `"buildCommand": "yarn workspace frontend build"`, output `frontend/dist`. `frontend/vercel.json` mirrors it for the case where the project root is set to `frontend/`, but the root config is the one in use.
>
> Two deploy failures came out of this file and are worth not repeating. It first declared `npm ci`, which cannot work because the repo has no `package-lock.json` (`Command "npm ci" exited with 1`). It then declared `pnpm install --frozen-lockfile` while Vercel's pnpm was older than the lockfile format, giving `WARN Ignoring not compatible lockfile` followed by `ERROR Headless installation requires a pnpm-lock.yaml file`. The lesson in both cases: the install command, the lockfile, and the `packageManager` pin have to name the same tool, and the fix is never to commit a second lockfile.

Path filters mean neither workflow runs for a root-only change. An absent check is not a passing check.

## Licensing

MIT throughout (root `LICENSE`, `"license": "MIT"` in `package.json`). No split licensing, no per-package exceptions.
