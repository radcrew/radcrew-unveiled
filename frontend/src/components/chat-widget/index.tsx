import { useEffect, useRef, useState, type FormEvent } from "react";
import { sendChatMessage } from "@/lib/chatbot-api";
import { ChatFloatingButton } from "./ChatFloatingButton";
import { ChatPanel } from "./ChatPanel";
import { WELCOME_MESSAGE, type ChatMessage } from "./types";

export function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME_MESSAGE]);
  const [draft, setDraft] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const scrollAnchorRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollAnchorRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, pending, open]);

  const canSend = draft.trim().length >= 2 && !pending;

  async function sendMessage() {
    const text = draft.trim();
    if (text.length < 2 || pending) return;

    const userMsg: ChatMessage = {
      id: `u-${Date.now()}`,
      role: "user",
      content: text,
    };
    setMessages((m) => [...m, userMsg]);
    setDraft("");
    setError(null);
    setPending(true);

    try {
      const res = await sendChatMessage(text);
      setMessages((m) => [
        ...m,
        {
          id: `a-${Date.now()}`,
          role: "assistant",
          content: res.answer,
          sources: res.sources,
        },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setPending(false);
    }
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    void sendMessage();
  }

  return (
    <>
      <ChatFloatingButton onOpen={() => setOpen(true)} />
      <ChatPanel
        open={open}
        onOpenChange={setOpen}
        messages={messages}
        pending={pending}
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
