import { afterEach, describe, expect, it, vi } from "vitest";
import { streamChatMessage } from "./chatbot-api";

/** Build a fetch Response whose body streams the given SSE text in arbitrary slices. */
function sseResponse(sse: string, slices = 1, ok = true): Response {
  const bytes = new TextEncoder().encode(sse);
  const chunkSize = Math.ceil(bytes.length / slices) || bytes.length;
  let offset = 0;

  const body = new ReadableStream<Uint8Array>({
    pull(controller) {
      if (offset >= bytes.length) {
        controller.close();
        return;
      }
      controller.enqueue(bytes.slice(offset, offset + chunkSize));
      offset += chunkSize;
    },
  });

  return new Response(body, { status: ok ? 200 : 500 });
}

function event(obj: Record<string, unknown>): string {
  return `data: ${JSON.stringify(obj)}\n\n`;
}

afterEach(() => {
  vi.restoreAllMocks();
});

describe("streamChatMessage", () => {
  it("emits each chunk to onChunk in order", async () => {
    const sse =
      event({ type: "chunk", content: "Hello" }) +
      event({ type: "chunk", content: " world" }) +
      event({ type: "done" });
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(sseResponse(sse)));

    const chunks: string[] = [];
    await streamChatMessage("hi", { onChunk: (c) => chunks.push(c) });

    expect(chunks).toEqual(["Hello", " world"]);
  });

  it("reassembles events split across stream reads", async () => {
    const sse =
      event({ type: "chunk", content: "split" }) + event({ type: "done" });
    // Force the bytes to arrive in many small slices.
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(sseResponse(sse, 8)));

    const chunks: string[] = [];
    await streamChatMessage("hi", { onChunk: (c) => chunks.push(c) });

    expect(chunks).toEqual(["split"]);
  });

  it("sends message and history in the request body", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue(sseResponse(event({ type: "done" })));
    vi.stubGlobal("fetch", fetchMock);

    const history = [{ role: "user" as const, content: "earlier" }];
    await streamChatMessage("now", { onChunk: () => {} }, history);

    const [, init] = fetchMock.mock.calls[0];
    expect(JSON.parse(init.body)).toEqual({ message: "now", history });
  });

  it("omits history key when none is provided", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue(sseResponse(event({ type: "done" })));
    vi.stubGlobal("fetch", fetchMock);

    await streamChatMessage("solo", { onChunk: () => {} });

    expect(JSON.parse(fetchMock.mock.calls[0][1].body)).toEqual({ message: "solo" });
  });

  it("throws the server error message on a non-ok response", async () => {
    const res = new Response(JSON.stringify({ error: "rate limited" }), {
      status: 500,
    });
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(res));

    await expect(
      streamChatMessage("hi", { onChunk: () => {} }),
    ).rejects.toThrow("rate limited");
  });

  it("throws on an in-stream error event", async () => {
    const sse =
      event({ type: "chunk", content: "partial" }) +
      event({ type: "error", error: "model exploded" });
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(sseResponse(sse)));

    await expect(
      streamChatMessage("hi", { onChunk: () => {} }),
    ).rejects.toThrow("model exploded");
  });
});
