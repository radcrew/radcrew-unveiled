# Chatbot Improvement Plan

Analysis of why the RadCrew chat assistant does not answer all customer
questions, scoped to the current stack (FastAPI + LangGraph + small
HuggingFace models). Two confirmed problems, with file-referenced causes
and fixes.

## Current architecture

- `POST /chat` (`app/api/chat.py`) streams an SSE response.
- LangGraph (`app/chatbot/graph/build.py`):
  - **route** node classifies feedback-submission vs. question.
  - → **feedback handler** or **rag answer**.
- RAG (`app/chatbot/graph/nodes/rag_answer/`): embed the question with
  `all-MiniLM-L6-v2`, retrieve top-5 chunks above 0.35 similarity, build a
  grounded prompt, stream from `Qwen/Qwen2.5-1.5B-Instruct`.
- Knowledge base = RadCrew team-member profiles only (GitHub loader + site
  content).
- Generation is **deterministic**: `temperature=0`, `top_p=1`,
  `do_sample=False`, fixed `seed=42`
  (`huggingface/chat_completion.py`, `huggingface/text_generation.py`).

---

## Problem 1 — Bails to the email fallback on in-scope questions

The bot returns `MSG_FALLBACK_LOW_CONTEXT` ("email code@radcrew.org") even
when relevant information exists.

### Causes

1. **Retrieval threshold too strict** — `retrieval.py:15,58`.
   `RETRIEVAL_FALLBACK_SIMILARITY_THRESHOLD = 0.35` on MiniLM cosine is
   high. Questions phrased differently from the profile text score below it
   and return `[]`.
2. **Embeddings miss name-based questions** — questions like "who built X"
   are not rescued by any lexical match; profile titles contain the names
   but are never matched directly.
3. **The prompt offers an escape hatch** — `prompt.py:35`:
   *"If both history and context sources are insufficient, say you do not
   have enough information and suggest emailing code@radcrew.org."*
   A 1.5B model, given marginally-relevant chunks, over-uses this exit
   instead of attempting an answer.

### Fixes

- [x] Lower the threshold to ~0.25 and raise top-k from 5 → 8
      (`retrieval.py`, `answer.py`).
- [x] Add a lexical / keyword (or BM25) fallback alongside embeddings so
      name-based questions match on profile titles (`retrieval.py`).
- [x] Soften the escape-hatch wording: answer from whatever relevant
      sources exist first; only suggest email when nothing matches
      (`prompt.py`).

---

## Problem 2 — Inconsistent tone

The assistant varies tone / register / format between turns. Because
decoding is already deterministic, this is **structural**, not randomness.

### Causes

1. **No system role** — `chat_completion.py:35` sends everything as a single
   `user` message: `messages=[{"role": "user", "content": prompt}]`.
   Small instruction-tuned models (Qwen included) follow a dedicated
   `system` message far more reliably than instructions buried in a user
   turn mixed with context and the question.
2. **Competing directives** in `prompt.py`: "concise, helpful, accurate"
   vs. "as briefly as possible," "do not add extra details," "direct
   sentence only." Different questions tip the model into different
   registers.

### Fixes

- [x] Split the prompt into a stable `system` message (persona + tone +
      format rules, identical every call) and a `user` message (context +
      question, varies). Highest-leverage tone fix.
- [x] Collapse the contradictory length rules into one coherent tone spec.
- [x] Add a deterministic output guardrail (post-processing) to enforce
      format rules the model drifts on: convert `*` bullets to `-`, strip
      URLs / markdown links — rather than relying on the model
      (`sanitize.py`).

---

## The three proposed concepts, evaluated for this stack

| Concept | Verdict |
|---|---|
| **Tool calls** | Skip for now. Structured JSON routing already exists (`feedback_router/router.py`); reliable function-calling on a 1.5B model is unlikely and would not fix coverage. |
| **Guardrails** | Adopt — as deterministic *code* (input scope check + output format validator), not model-enforced. This is the real fix for tone/format consistency. |
| **Skills** | Anthropic Agent Skills target Claude models and do not apply to an HF backend. The equivalent here is a reusable **system-prompt module** (Problem 2, fix 1). |

---

## Suggested order of work

1. **System/user prompt split + threshold and top-k tuning** — smallest
   diff, addresses both problems.
2. **Lexical retrieval fallback** — recovers name-based questions.
3. **Deterministic output guardrail** — locks in format consistency.

## Out of scope (deliberately)

- Switching to a larger model or a non-HF API (single biggest quality jump,
  but excluded by current constraints).
- Expanding the knowledge base beyond team profiles (separate content task).
