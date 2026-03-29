import { useEffect, useRef, useState, type FormEvent } from "react";
import { streamChatMessage } from "@/lib/chatbot-api";
import { ChatFloatingButton } from "./ChatFloatingButton";
import { ChatPanel } from "./ChatPanel";
import { WELCOME_MESSAGE, type ChatMessage } from "./types";

export function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME_MESSAGE]);
  const [draft, setDraft] = useState("");
  const [pending, setPending] = useState(false);
  const [streamStarted, setStreamStarted] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const scrollAnchorRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollAnchorRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, pending, open]);

  const canSend = draft.trim().length >= 2 && !pending;

  const sendMessage = async () => {
    const text = draft.trim();
    if (text.length < 2 || pending) return;

    const userMsg: ChatMessage = {
      id: `u-${Date.now()}`,
      role: "user",
      content: text,
    };
    const assistantId = `a-${Date.now()}`;
    setMessages((m) => [
      ...m,
      userMsg,
      {
        id: assistantId,
        role: "assistant",
        content: "",
      },
    ]);
    setDraft("");
    setError(null);
    setPending(true);
    setStreamStarted(false);

    try {
      await streamChatMessage(text, {
        onChunk: (chunk) => {
          setStreamStarted(true);
          setMessages((existing) =>
            existing.map((msg) =>
              msg.id === assistantId ? { ...msg, content: `${msg.content}${chunk}` } : msg,
            ),
          );
        },
      });
    } catch (err) {
      setMessages((existing) =>
        existing.filter((msg) => !(msg.id === assistantId && msg.content.trim().length === 0)),
      );
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setPending(false);
      setStreamStarted(false);
    }
  };

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    void sendMessage();
  };

  return (
    <>
      <ChatFloatingButton onOpen={() => setOpen(true)} />
      <ChatPanel
        open={open}
        onOpenChange={setOpen}
        messages={messages}
        pending={pending}
        showLoading={pending && !streamStarted}
        error={error}
        draft={draft}
        onDraftChange={setDraft}
        canSend={canSend}
        onSubmit={onSubmit}
        onSend={sendMessage}
        scrollAnchorRef={scrollAnchorRef}
      />
    </>
  );
}
