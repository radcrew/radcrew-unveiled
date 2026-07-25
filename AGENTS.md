# AGENTS.md

Root coordination contract for AI and human contributors in this repo. Detailed architecture and working guidelines live in [CLAUDE.md](./CLAUDE.md); this file states the non-negotiables and where to look.

## Scope

- Applies to the whole monorepo: `frontend/`, `backend/`, `training/`, `docs/`.
- No nested `AGENTS.md` files exist yet. If one is added under a package, it may tighten rules for that subtree but must not relax the rules here.
- `.cursor/skills/radcrew-chatbot/SKILL.md` is a Cursor-specific companion covering the chatbot subsystem. Its path map and behavioral rules are current and worth reading before touching `backend/app/chatbot/`, but it is not loaded at runtime and is not authoritative over this file.

Normative language: `MUST`/`MUST NOT` are mandatory. `SHOULD`/`SHOULD NOT` are expected by default; deviations should be explained in the PR. `MAY` is optional.

## Non-Negotiables

- `MUST` use **Yarn 1 classic** for the Node side, pinned by `"packageManager": "yarn@1.22.22"` in the root `package.json`. `yarn.lock` is the only lockfile; CI and the Vercel frontend deploy both run `yarn install --frozen-lockfile`. `MUST NOT` run `npm install` or `pnpm install` at the root, and `MUST NOT` commit a `package-lock.json` or `pnpm-lock.yaml`. pnpm was removed deliberately: the only JavaScript package here is `frontend/`, since the backend is Python, so a workspace-oriented package manager bought nothing.
- `MUST` declare peer dependencies explicitly. Yarn 1 does not auto-install peers the way the previous pnpm setup did (`autoInstallPeers`), so a package that is only ever reached as someone else's peer will be missing at runtime. `@testing-library/dom` is in `frontend` devDependencies for exactly this reason; do not remove it because "nothing imports it directly".
- `MUST` treat `backend/app/core/settings.py` as the source of truth for backend configuration. The environment table in `backend/README.md` has drifted on at least three defaults (see CLAUDE.md's Stale docs section) and `MUST NOT` be cited to justify a value.
- `MUST` route all chat inference through `app/chatbot/llm.py`, never by constructing a provider client inline. It selects Hugging Face or OpenRouter from whichever credential is configured, and a direct client call silently ignores that choice. Embeddings are the one deliberate exception: OpenRouter has no embeddings endpoint, so `knowledge/embeddings.py` always uses Hugging Face and degrades to lexical retrieval without `HF_TOKEN`.
- `MUST NOT` weaken the chatbot's grounding contract when editing prompts, retrieval, or the graph: answers stay grounded in conversation history plus retrieved context only, insufficient context points the user at `code@radcrew.org`, replies carry no URLs, and bullets use `-` rather than `*`. These are enforced by `backend/app/tests/` and by the prompt text in `graph/nodes/rag_answer/prompt.py`.
- `MUST` keep the SSE wire contract in sync across all three sides when changing it. `backend/app/api/chat.py` emits `{"type":"chunk","content":...}` events followed by a final `{"type":"done"}`, consumed by `frontend/src/lib/chatbot-api.ts` and `frontend/src/components/chat-widget/`. Changing one side alone breaks chat silently, with no error surfaced anywhere.
- `MUST NOT` commit secrets. `.env` is gitignored. `HF_TOKEN`, `GITHUB_TOKEN`, `WEB_SEARCH_API_KEY`, and `WEB3FORMS_ACCESS_KEY` are real credentials belonging in `backend/.env` locally and in Vercel project settings for deploys, never in CI config or source.
- `MUST NOT` treat `training/` as runtime code. It is an offline QLoRA pipeline producing an adapter; nothing under `backend/app/` imports it.
- `MUST` remember that **opening a pull request deploys**. Both `.github/workflows/frontend.yml` and `backend.yml` run their Vercel deploy job on `pull_request`, so opening a PR is an outward-facing action, not just a CI run.
- `MUST` run the smallest scoped lint/test command for the side you touched (see Command Baseline), not both suites, unless the change spans them.
- `SHOULD NOT` trust the root `README.md`, `frontend/README.md`, `backend/README.md`, or `docs/architecture.md` at face value on commands, environment defaults, or module layout. Several have drifted; CLAUDE.md's Stale docs section lists what is actually current.

## Command Baseline

Node, from repo root:

- Install: `yarn install`
- Dev: `yarn dev` (frontend and API together), or `yarn dev:frontend` / `yarn dev:backend`
- Lint: `yarn lint` (ESLint over `frontend/src` only; there is no backend linter)
- Test: `yarn test` (frontend Vitest), `yarn test:e2e` (Playwright)
- Build: `yarn build` (frontend Vite build)

Python, from `backend/` with the venv active:

- Install: `python -m venv .venv`, activate, then `pip install -r requirements.txt`
- Test: `python -m pytest` (183 tests; `pytest.ini` pins `testpaths = app/tests`)
- Syntax check: `python -m compileall -q app`, which is all `yarn build:backend` does

Full per-package matrix, E2E, and single-test syntax: see [CLAUDE.md](./CLAUDE.md#commands).

## Where To Look

- Behavioral guidelines and full architecture: [CLAUDE.md](./CLAUDE.md)
- Chatbot subsystem path map and behavioral rules: [.cursor/skills/radcrew-chatbot/SKILL.md](./.cursor/skills/radcrew-chatbot/SKILL.md)
- Cross-cutting architecture: [docs/architecture.md](./docs/architecture.md), partially stale, see CLAUDE.md
- Chatbot request walkthrough: [backend/docs/chatbot-flow.md](./backend/docs/chatbot-flow.md)
- Tuning notes: [backend/docs/chatbot-improvements.md](./backend/docs/chatbot-improvements.md)
- Training pipeline: [training/README.md](./training/README.md)
- Contribution workflow: [CONTRIBUTING.md](./CONTRIBUTING.md)
- PR template: [.github/PULL_REQUEST_TEMPLATE.md](./.github/PULL_REQUEST_TEMPLATE.md)
- Reporting vulnerabilities: [SECURITY.md](./SECURITY.md)

## Enforcement

Mechanical checks over prose, where they exist:

- ESLint at root over `frontend/src` (`yarn lint`). There is no backend linter, no formatter config, and no pre-commit hooks in this repo, so Python style is convention-only.
- Frontend Vitest (`frontend/src/**/*.test.ts[x]`), Playwright E2E (`frontend/e2e/`), and backend pytest (`backend/app/tests/`). CI runs all three.
- **CI path filters mean a change can be green without being tested.** `frontend.yml` triggers only on `frontend/**`, `package.json`, `yarn.lock`, `vercel.json`, and its own file; `backend.yml` only on `backend/**` and its own file. A root-only change (this file, `README.md`, `docs/`) runs neither workflow. Do not read an absent check as a passing one.
- There is no repo-wide `agents:check` or module-boundary lint. Rely on the per-package commands above.
