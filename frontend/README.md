# RadCrew Unveiled — Frontend

Vite + React site. It consumes Contentful for content and talks to the FAQ chatbot API for chat.

## Prerequisites

- **Node.js** 22 (the repo uses Yarn 1 workspaces — install dependencies from the repository root)

## Install

From the **repository root** (installs workspace dependencies, including this package):

```bash
yarn install
```

## Configuration

Copy [`.env.example`](.env.example) to `.env` in this directory and set values as needed.

### Environment variables (`VITE_*`)

These are embedded in the browser bundle at build time. Do not put secrets you must hide from users in `VITE_*` variables.

- `VITE_CONTENTFUL_SPACE_ID`: Contentful space id (Content Delivery API)
- `VITE_CONTENTFUL_DELIVERY_TOKEN`: Content Delivery API token ([Contentful](https://www.contentful.com/) → Space → Settings → API keys → Content delivery / preview tokens)
- `VITE_CONTENTFUL_ENVIRONMENT`: environment name (optional; default in the SDK is often `master`)
- `VITE_CHATBOT_API_BASE_URL`: base URL for the chat API (default `http://localhost:8787`)

Contentful is used by the frontend only. The backend builds its knowledge base from static site copy and optional GitHub Markdown, and has no Contentful integration.

## Development

From the **repository root**:

```bash
yarn dev:frontend
```

This runs the Vite dev server (see root `package.json`). Default dev URL is **http://localhost:8080** (see [`vite.config.ts`](vite.config.ts)).

With dependencies installed, you can also run from this directory:

```bash
cd frontend
yarn dev
```

## Build and preview

From the repository root:

```bash
yarn build
yarn preview
```

Or from `frontend`:

```bash
cd frontend
yarn build
yarn preview
```

`yarn build:dev` (root) runs a development-mode Vite build for the frontend workspace.

## Tests

From the repository root:

```bash
yarn test
```

Watch mode:

```bash
yarn test:watch
```

Or from `frontend`:

```bash
cd frontend
yarn test
yarn test:watch
```

The suite uses Vitest (`vitest run` / `vitest`). End-to-end smoke tests use Playwright: `yarn test:e2e` from the root (run `yarn playwright install chromium` once first).

## Lint

ESLint is configured at the monorepo root and targets `frontend/src`. From the repository root:

```bash
yarn lint
```

## Chatbot from the browser

The app calls `POST /chat` on `VITE_CHATBOT_API_BASE_URL` (default `http://localhost:8787`). Ensure the backend is running and CORS matches your site origin (`FRONTEND_ORIGIN` or `FRONTEND_ORIGINS` on the backend) — see [backend/README.md](../backend/README.md).
