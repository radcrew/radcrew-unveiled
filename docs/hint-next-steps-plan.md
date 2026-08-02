# Plan: hint next steps in the chatbot

Implementation plan for showing follow-up question hints after each assistant answer in the chat widget.

## Assumptions

You asked for a plan without a round of questions, so these are the readings I picked. Each one is cheap to change, and the section that would change is named.

1. "Hint next steps" means up to 3 short follow-up questions rendered as tappable chips under the assistant's answer. Clicking one sends it as the next user message. This is the same interaction as the existing `SUGGESTIONS` block in `frontend/src/components/chat-widget/index.tsx:10`, except contextual and shown after every answer instead of only before the first one.
2. Hints are produced deterministically from the retrieved knowledge documents, not by a second LLM call. Rationale in [Why not an LLM call](#why-not-an-llm-call). If you want model-generated hints instead, only `hints.py` changes, everything else in this plan stands.
3. Hints are shown under the most recent assistant message only. Older messages keep their hints in state but do not render chips, so the transcript does not fill with stale chips.
4. No hints for guardrail-blocked replies or feedback confirmation replies. Those turns are asking the user for something specific and follow-up chips would compete with them.
5. No new environment variable. The repo prefers no unrequested configurability, and the feature has no cost or credential to gate. If you want a kill switch later, `Settings` already has the pattern.

## Design decisions

### Where hints come from

A curated catalog keyed by knowledge document id (`hero`, `services`, `how-we-work`, `stats`, `portfolio`, `tech-stack`, `testimonial`, `faq`, `contact`, `social-links`, the ids in `backend/app/chatbot/knowledge/site_content.py`). The RAG node already computes the top retrieved documents and a confidence score at `backend/app/chatbot/graph/nodes/rag_answer/answer.py:54`, so hint selection is a dictionary lookup over data that already exists. Cost is zero inference calls and no measurable latency.

Documents with no catalog entry contribute nothing. Ids from the GitHub loader are `github:<path>` (`backend/app/chatbot/knowledge/github_loader/loader.py:81`) and their titles are derived from Markdown, so interpolating a title into a hint would produce broken text like "What has Selected work and portfolio built?". Those documents are skipped rather than templated.

When fewer than 3 catalog hints come back, top up from a small default list so every answer gets a usable set.

**Trap worth knowing before you write the code.** `answer.py:66` sets `context_documents = list(knowledge_documents)`, the whole corpus, and passes that to the prompt. Only `retrieved_documents` reflects the actual query. Build hints from `retrieved_documents`. Using `context_documents` would give every answer in every conversation the same three hints, and it would look like it worked.

### Why not an LLM call

A generated-hints call is a fourth inference round-trip on a request that can already make three (router, harmful-input rail, groundedness rail, per `CLAUDE.md`). It would also have to run after generation completes to see the answer, which means the user waits again after the answer finishes streaming, or the hints arrive seconds late. Curated hints answer the same UX need at zero cost.

If you later want generated hints, the swap point is `build_hints()`. It would additionally need its own cache entry, because `stream_answer_with_cache` caches the answer text only.

### Why hints skip the output rails

Hints are fixed strings written by us, never model output, so PII scrubbing and groundedness checks have nothing to act on. A catalog test asserting no URLs and no `*` bullets keeps them inside the same output contract the rails enforce for answers.

### Wire contract

`AGENTS.md` requires the SSE contract to stay in sync across `backend/app/api/chat.py`, `frontend/src/lib/chatbot-api.ts`, and `frontend/src/components/chat-widget/`. The new shape:

```
data: {"type":"chunk","content":"..."}          0..n
data: {"type":"hints","hints":["...","..."]}    0..1, always after the chunks, always before done
data: {"type":"done"}
```

The hints event is omitted entirely when there are no hints, and omitted on the stream-failure path (the answer is already an apology, chips would be noise).

Both mixed-version directions are safe, which matters because opening a PR deploys the two Vercel projects independently:

- Old frontend, new backend: `parseSseEvent` branches only on `chunk` and `error`, so an unknown type falls through and is ignored.
- New frontend, old backend: no hints event ever arrives, `onHints` never fires, chips never render.

## Steps

Each step has one verification command. Run only the command listed, not both suites.

### 1. Hint generation (backend, no wire change)

New file `backend/app/chatbot/graph/nodes/rag_answer/hints.py`:

```python
MAX_HINTS = 3
HINT_CATALOG: dict[str, tuple[str, ...]]   # document id -> candidate follow-ups
DEFAULT_HINTS: tuple[str, ...]             # top-up when the catalog yields too few

def build_hints(
    retrieved_documents: list[KnowledgeDocument],
    message: str,
    history: list[ChatHistoryMessage],
) -> tuple[str, ...]:
    ...
```

Behavior:

- Walk `retrieved_documents` in rank order, take catalog entries for each id, preserve order, deduplicate.
- Drop any hint the user effectively already asked, comparing case-folded and punctuation-stripped text against `message` and the user turns in `history`.
- Top up from `DEFAULT_HINTS` until `MAX_HINTS`, then truncate.
- Return a tuple so it can sit in graph state without aliasing.

Catalog content stays short enough to fit a 360px panel, roughly 50 characters, phrased as questions a visitor would actually ask. Example for `services`: "How do you scope a new project?", "What does a typical timeline look like?".

New file `backend/app/tests/test_hints.py`: catalog lookup by id, order preservation, dedupe, history suppression, top-up to exactly 3, unknown ids ignored, no hint contains a URL or a `*` bullet, every hint under the length cap.

Verify: `cd backend && python -m pytest app/tests/test_hints.py`

### 2. Plumb hints through the graph and the endpoint

`backend/app/chatbot/graph/state.py`: add `hints: tuple[str, ...]` to `ChatState`. Nodes that do not set it leave it absent, which is what makes the guardrail and feedback paths hint-free without any extra branching.

`backend/app/chatbot/graph/nodes/rag_answer/answer.py`: return hints from the three exits of `rag_answer_node`.

| Exit | Hints |
|---|---|
| small talk (`answer.py:45`) | `DEFAULT_HINTS`, so a greeting gets starter questions |
| low-context fallback (`answer.py:70`) | `DEFAULT_HINTS`, giving the user somewhere to go besides email |
| normal answer | `build_hints(retrieved_documents, message, history)` |

`_stream_prompt` currently returns `{"output_stream": ...}`; give it a `hints` parameter and include the key in what it returns. Cache hits keep their hints, since hints are recomputed per request and never cached.

`backend/app/chatbot/chat.py`: `generate_chat_stream` returns a small frozen dataclass instead of a bare iterator.

```python
@dataclass(frozen=True)
class ChatStream:
    chunks: Iterator[str]
    hints: tuple[str, ...] = ()
```

The `llm_provider() == "none"` early return becomes `ChatStream(iter([MSG_AI_UNAVAILABLE]))`. The graph result reads `result.get("hints", ())`.

`backend/app/api/chat.py`: iterate `answer_stream.chunks`, and after the loop completes without raising, emit the hints event when `answer_stream.hints` is non-empty, then `done`. Keep the existing `try/except` exactly as it is; the except branch yields the fallback chunk and falls through to `done` with no hints event. The `except` around `chatbot.generate_chat_stream` builds `ChatStream(iter([MSG_AI_UNAVAILABLE]))`.

This signature change breaks two existing tests that patch `generate_chat_stream` (`backend/app/tests/test_chat.py:54` and `:76`); update both to the new return type. Add: a normal stream emits `hints` after the last chunk and before `done`, a stream that raises mid-flight emits no hints event, and a guardrail-blocked reply emits no hints event.

Verify: `cd backend && python -m pytest app/tests/test_chat.py app/tests/test_hints.py`

### 3. Parse the hints event (frontend)

`frontend/src/lib/chatbot-api.ts`:

- Extend `ChatStreamEvent` with `{ type: "hints"; hints: string[] }`.
- Add `onHints?: (hints: string[]) => void` to `StreamChatHandlers`.
- In the event loop, handle `hints` defensively before calling back: require `Array.isArray`, keep only non-empty strings, trim, cap at 3. A malformed hints event is dropped, never thrown, because it must not kill a stream whose answer already arrived intact.

`frontend/src/lib/chatbot-api.test.ts`: a well-formed hints event calls `onHints`, a malformed one does not throw and does not call it, an unknown event type is still ignored, and chunks around a hints event still arrive in order.

Verify: `yarn workspace frontend test src/lib/chatbot-api.test.ts`

### 4. Render the chips (frontend)

`frontend/src/components/chat-widget/types.ts`: add `hints?: string[]` to `ChatMessage`.

`frontend/src/components/chat-widget/index.tsx`:

- Pass `onHints` into `streamChatMessage`, attaching the hints to the assistant message being streamed (same `assistantId` update pattern as `onChunk`).
- Extract the existing chip markup at `index.tsx:282-300` into a local `SuggestionChips({ items, onPick, disabled })` and use it for both the starter `SUGGESTIONS` and the per-message hints. This is reuse of markup that already exists, not a new abstraction.
- Render hints under a message only when it is the last message, its role is `assistant`, `pending` is false, and `hints` is non-empty. Clicking calls `sendMessage(hint)`, which appends a user turn, so the chips stop rendering on the next tick without extra state.
- Wrap the chips in `role="group"` with `aria-label="Suggested follow-up questions"`.

`frontend/src/components/chat-widget/index.test.tsx`: chips appear after an answer that carried hints, clicking one calls `streamChatMessage` with that text, chips do not render while pending, and only the latest assistant message shows them.

Verify: `yarn workspace frontend test src/components/chat-widget/index.test.tsx`

## Not doing

- Appending hints to the answer text with a delimiter. It puts marker text into a token stream that the sanitizer, PII scrubber, and groundedness rail all read, and the markers flicker in the UI mid-stream.
- A separate `GET /hints` request. It doubles the request count for data the answer request already has.
- Persisting hints across a page reload. The transcript itself does not persist.
- Touching `frontend/e2e/chat-widget.spec.ts`. The Playwright specs cover opening and sending; hint rendering is covered at the component level where a stubbed stream can drive it.

## Files touched

| File | Change |
|---|---|
| `backend/app/chatbot/graph/nodes/rag_answer/hints.py` | new, catalog and `build_hints` |
| `backend/app/chatbot/graph/nodes/rag_answer/answer.py` | return hints from all three exits |
| `backend/app/chatbot/graph/state.py` | `hints` key |
| `backend/app/chatbot/chat.py` | `ChatStream` return type |
| `backend/app/api/chat.py` | emit the hints event before `done` |
| `backend/app/tests/test_hints.py` | new |
| `backend/app/tests/test_chat.py` | fix two mocks, add three contract tests |
| `frontend/src/lib/chatbot-api.ts` | parse hints, `onHints` |
| `frontend/src/lib/chatbot-api.test.ts` | parsing tests |
| `frontend/src/components/chat-widget/types.ts` | `hints` on `ChatMessage` |
| `frontend/src/components/chat-widget/index.tsx` | `SuggestionChips`, render under last answer |
| `frontend/src/components/chat-widget/index.test.tsx` | rendering tests |

Docs to update in the same PR: the request-flow section of `CLAUDE.md` and `docs/architecture.md`, both of which state the SSE contract as chunks followed by done.

Estimated size: about 120 lines of backend source, about 60 lines of frontend source, plus tests. Steps 1 and 2 are independently shippable, since the endpoint stays backward compatible after step 2 whether or not the frontend ever reads the event.
