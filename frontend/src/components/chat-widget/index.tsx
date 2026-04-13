import { useEffect, useLayoutEffect, useRef, useState, type FormEvent } from "react";
import { useLocation } from "react-router-dom";
import { streamChatMessage } from "@/lib/chatbot-api";
import { ChatFloatingButton } from "./ChatFloatingButton";
import { ChatPanel } from "./ChatPanel";
import { WELCOME_MESSAGE, type ChatMessage } from "./types";

/** Matches `h-12` on the floating chat control. */
const CHAT_FLOAT_BUTTON_PX = 48;

export const ChatWidget = () => {
  const location = useLocation();
  const [fixedBottomPx, setFixedBottomPx] = useState(24);
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME_MESSAGE]);
  const [draft, setDraft] = useState("");
  const [pending, setPending] = useState(false);
  const [streamStarted, setStreamStarted] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const scrollAnchorRef = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    if (location.pathname !== "/") {
      setFixedBottomPx(24);
      return;
    }
    const footer = document.getElementById("footer");
    if (!footer) {
      setFixedBottomPx(24);
      return;
    }
    const update = () => {
      const h = footer.offsetHeight;
      setFixedBottomPx(Math.max(8, h / 2 - CHAT_FLOAT_BUTTON_PX / 2));
    };
    update();
    const ro = new ResizeObserver(update);
    ro.observe(footer);
    return () => ro.disconnect();
  }, [location.pathname]);

  useEffect(() => {
    scrollAnchorRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, pending, open]);

  const canSend = draft.trim().length >= 2 && !pending;

  const sendMessage = async () => {
    const text = draft.trim();
    if (text.length < 2 || pending) return;

    // Send previous turns so the backend can treat this as a follow-up question.
    // Backend constraints: max 12 history messages, and each message content max 2000 chars.
    const history = messages
      .filter((m) => m.id !== "welcome")
      .slice(-12)
      .map((m) => ({
        role: m.role,
        content: m.content.slice(0, 2000),
      }));

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
      await streamChatMessage(
        text,
        {
          onChunk: (chunk) => {
            setStreamStarted(true);
            setMessages((existing) =>
              existing.map((msg) =>
                msg.id === assistantId ? { ...msg, content: `${msg.content}${chunk}` } : msg,
              ),
            );
          },
        },
        history,
      );
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
      <ChatFloatingButton onOpen={() => setOpen(true)} fixedBottomPx={fixedBottomPx} />
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
};
