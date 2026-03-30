const baseUrl = (import.meta.env.VITE_CHATBOT_API_BASE_URL ?? "http://localhost:8787").replace(/\/$/, "");

type ChatStreamEvent =
  | { type: "chunk"; content: string }
  | { type: "done"; confidence: number }
  | { type: "error"; error: string };

interface StreamChatHandlers {
  onChunk: (chunk: string) => void;
  onDone?: (confidence: number) => void;
}

type ChatHistoryMessage = { role: "user" | "assistant"; content: string };

function extractErrorMessage(body: unknown): string {
  if (
    typeof body === "object" &&
    body !== null &&
    "error" in body &&
    typeof (body as { error: unknown }).error === "string"
  ) {
    return (body as { error: string }).error;
  }
  return "The chatbot service is currently unavailable.";
}

function parseSseEvent(rawEvent: string): ChatStreamEvent | null {
  const normalized = rawEvent.replace(/\r\n/g, "\n");
  const data = normalized
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.startsWith("data:"))
    .map((line) => line.slice(5).trim())
    .join("");

  if (!data) return null;

  try {
    return JSON.parse(data) as ChatStreamEvent;
  } catch {
    return null;
  }
}

export async function streamChatMessage(
  message: string,
  handlers: StreamChatHandlers,
  history?: ChatHistoryMessage[],
): Promise<void> {
  const response = await fetch(`${baseUrl}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message, ...(history ? { history } : {}) }),
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(extractErrorMessage(body));
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error("The chatbot service did not return a stream.");
  }

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split("\n\n");
    buffer = events.pop() ?? "";

    for (const rawEvent of events) {
      const event = parseSseEvent(rawEvent);
      if (!event) continue;

      if (event.type === "chunk" && event.content) {
        handlers.onChunk(event.content);
      } else if (event.type === "done") {
        handlers.onDone?.(event.confidence);
      } else if (event.type === "error") {
        throw new Error(event.error);
      }
    }
  }
}
