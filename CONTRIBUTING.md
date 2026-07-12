# Contributing to RadCrew Unveiled

Thanks for your interest in contributing! This is a monorepo with a Vite/React
frontend and a FastAPI backend. This guide covers the workflow for external
contributors.

By participating in this project, you agree to abide by the
[Code of Conduct](CODE_OF_CONDUCT.md).

## Getting started

1. Fork the repository and clone your fork.
2. Follow the setup steps in [README.md](README.md) to install the frontend
   (`yarn install`) and backend (Python venv + `pip install -r requirements.txt`)
   dependencies.
3. Copy `.env.example` to `.env` in `frontend/` and `backend/` and fill in any
   values you need locally (see each package's README for details).
4. Create a branch off `main` for your change:

   ```bash
   git checkout -b your-name/short-description
   ```

## Making changes

- Keep pull requests focused — one logical change per PR is easier to review
  and merge.
- Match the existing code style in the file/package you're editing.
- Add or update tests for behavior you change.

Before opening a PR, run the checks relevant to what you touched:

```bash
yarn lint            # ESLint (frontend/src)
yarn test            # Frontend tests (Vitest)
yarn test:backend    # Backend tests (pytest)
yarn build           # Frontend build
```

## Commit messages

Use clear, descriptive commit messages. Conventional prefixes
(`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`) are appreciated but
not required.

## Submitting a pull request

1. Push your branch to your fork and open a PR against `radcrew/radcrew-unveiled:main`.
2. Fill out the PR template, including what changed and how you tested it.
3. Link any related issue.
4. Make sure CI (frontend/backend workflows) passes.
5. Be responsive to review feedback — a maintainer will merge once the PR is
   approved and checks are green.

## Reporting bugs / requesting features

Please use the issue templates when opening an issue — they help us get the
context we need to respond quickly.

## Security issues

Do not open a public issue for security vulnerabilities. See
[SECURITY.md](SECURITY.md) for how to report them privately.

## Questions

If anything here is unclear, open a discussion/issue or email
code@radcrew.org.
