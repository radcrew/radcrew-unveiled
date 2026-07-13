# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in RadCrew Unveiled, please report
it privately — **do not open a public GitHub issue**.

Email **code@radcrew.org** with:

- A description of the vulnerability and its potential impact
- Steps to reproduce (proof-of-concept code or requests are welcome)
- The affected component (`frontend` or `backend`) and, if known, the
  affected file(s) or endpoint(s)

We aim to acknowledge new reports within **3 business days** and to provide
a status update at least every **7 days** while the report is triaged and
fixed.

Please give us a reasonable amount of time to investigate and address a
report before disclosing it publicly. We'll credit reporters (if desired)
once a fix has shipped.

## Supported Versions

This project is deployed continuously from `main`; only the latest deployed
version is supported. There are no maintained release branches.

## Scope

In scope:

- The `frontend` app (Vite/React site) and its build/deploy pipeline
- The `backend` API (FastAPI chatbot service) and its endpoints
- Misconfiguration that exposes secrets, private knowledge-base content, or
  allows abuse of the chat/deep-search endpoints

Out of scope:

- Vulnerabilities in third-party dependencies with no demonstrated impact on
  this project (report those upstream instead)
- Denial-of-service reports that rely on brute-force volume rather than a
  logic flaw
- Findings that require access to another user's device, credentials, or
  environment variables
