import { useEffect, useRef, useState, type FormEvent } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Send, Sparkles, Loader2 } from "lucide-react";
import { streamChatMessage } from "@/lib/chatbot-api";
import { WELCOME_MESSAGE, type ChatMessage } from "./types";

const SUGGESTIONS = [
  "What does radcrew specialize in?",
  "How quickly can you start a project?",
  "Do you build on Solana?",
];

/** Matches floating control height for panel stacking above the launcher. */
const CHAT_FLOAT_BUTTON_PX = 56;
const FLOAT_PANEL_GAP_PX = 12;
/** Distance from the viewport bottom edge (matches `bottom-6`). */
const FLOAT_BOTTOM_PX = 24;

export const ChatWidget = () => {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [pending, setPending] = useState(false);
  const [streamStarted, setStreamStarted] = useState(false);
  const [errorBanner, setErrorBanner] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, pending, open]);

  useEffect(() => {
    if (!open) return;
    if (messages.length > 0) return;
    const t = window.setTimeout(() => {
      setMessages([WELCOME_MESSAGE]);
    }, 300);
    return () => window.clearTimeout(t);
  }, [open, messages.length]);

  useEffect(() => {
    if (open) {
      const t = window.setTimeout(() => inputRef.current?.focus(), 400);
      return () => window.clearTimeout(t);
    }
  }, [open]);

  const canSend = draft.trim().length >= 2 && !pending;

  const sendMessage = async (text: string) => {
    const trimmed = text.trim();
    if (trimmed.length < 2 || pending) return;

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
      content: trimmed,
    };
    const assistantId = `a-${Date.now()}`;

    setMessages((m) => [...m, userMsg, { id: assistantId, role: "assistant", content: "" }]);
    setDraft("");
    setErrorBanner(null);
    setPending(true);
    setStreamStarted(false);

    try {
      await streamChatMessage(
        trimmed,
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
      setErrorBanner(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setPending(false);
      setStreamStarted(false);
    }
  };

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    void sendMessage(draft);
  };

  const showSuggestions =
    messages.filter((m) => m.role === "user").length === 0 && !pending && !streamStarted;

  const panelBottomPx = FLOAT_BOTTOM_PX + CHAT_FLOAT_BUTTON_PX + FLOAT_PANEL_GAP_PX;

  return (
    <>
      <motion.button
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.2 }}
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-controls="radcrew-chat-panel"
        className="group fixed bottom-6 right-6 z-[60] flex items-center gap-2.5 rounded-full border-2 border-primary bg-foreground px-5 py-3.5 text-background shadow-2xl ring-1 ring-primary/30 transition-all duration-300 hover:bg-foreground/90 hover:ring-primary/50"
        style={{
          boxShadow: "0 8px 32px rgba(17,17,17,0.18), 0 0 0 1px rgba(201,169,110,0.35)",
        }}
      >
        <Sparkles className="h-4 w-4 text-primary transition-transform duration-300 group-hover:rotate-12" />
        <span className="text-sm font-light uppercase tracking-widest">Ask radcrew</span>
        <span className="absolute -right-1 -top-1 h-3 w-3 animate-ping rounded-full bg-primary opacity-75" />
        <span className="absolute -right-1 -top-1 h-3 w-3 rounded-full bg-primary" />
      </motion.button>

      <AnimatePresence>
        {open && (
          <motion.div
            id="radcrew-chat-panel"
            role="dialog"
            aria-label="RadCrew chat"
            initial={{ opacity: 0, y: 24, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 24, scale: 0.97 }}
            transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className="fixed right-6 z-[55] flex w-[360px] max-w-[calc(100vw-2rem)] flex-col overflow-hidden rounded-2xl shadow-2xl"
            style={{
              bottom: `${panelBottomPx}px`,
              height: "520px",
              background: "#FAFAF7",
              border: "1px solid rgba(201,169,110,0.25)",
              boxShadow: "0 24px 64px rgba(17,17,17,0.16), 0 0 0 1px rgba(201,169,110,0.1)",
            }}
          >
            <div
              className="flex items-center justify-between border-b px-5 py-4"
              style={{ borderColor: "rgba(201,169,110,0.2)", background: "#111111" }}
            >
              <div className="flex items-center gap-3">
                <div
                  className="flex h-8 w-8 items-center justify-center rounded-full"
                  style={{ background: "rgba(201,169,110,0.15)", border: "1px solid rgba(201,169,110,0.3)" }}
                >
                  <Sparkles className="h-4 w-4" style={{ color: "#C9A96E" }} />
                </div>
                <div>
                  <div className="text-sm font-light uppercase tracking-widest text-white">radcrew</div>
                  <div className="text-xs" style={{ color: "rgba(201,169,110,0.7)" }}>
                    AI Assistant
                  </div>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setOpen(false)}
                className="flex h-8 w-8 items-center justify-center rounded-full transition-colors hover:bg-white/10"
              >
                <X className="h-4 w-4 text-white/60" />
              </button>
            </div>

            {errorBanner ? (
              <div className="border-b border-amber-200/40 bg-amber-50 px-4 py-2 text-xs text-amber-950">{errorBanner}</div>
            ) : null}

            <div className="flex-1 space-y-3 overflow-y-auto px-4 py-4" style={{ scrollbarWidth: "thin" }}>
              {messages.map((msg) => (
                <div key={msg.id} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                  <div
                    className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                      msg.role === "user" ? "rounded-br-sm text-background" : "rounded-bl-sm"
                    }`}
                    style={
                      msg.role === "user"
                        ? { background: "#111111", color: "#FAFAF7" }
                        : {
                            background: "rgba(201,169,110,0.08)",
                            color: "#111111",
                            border: "1px solid rgba(201,169,110,0.15)",
                          }
                    }
                  >
                    {msg.content || (msg.role === "assistant" && pending && !streamStarted ? (
                      <span className="flex items-center gap-1 py-0.5">
                        <span
                          className="h-1.5 w-1.5 animate-bounce rounded-full bg-current"
                          style={{ animationDelay: "0ms" }}
                        />
                        <span
                          className="h-1.5 w-1.5 animate-bounce rounded-full bg-current"
                          style={{ animationDelay: "150ms" }}
                        />
                        <span
                          className="h-1.5 w-1.5 animate-bounce rounded-full bg-current"
                          style={{ animationDelay: "300ms" }}
                        />
                      </span>
                    ) : null)}
                  </div>
                </div>
              ))}

              {showSuggestions ? (
                <div className="flex flex-col gap-2 pt-1">
                  {SUGGESTIONS.map((s) => (
                    <button
                      key={s}
                      type="button"
                      onClick={() => void sendMessage(s)}
                      className="rounded-xl px-3 py-2 text-left text-xs transition-all duration-200 hover:scale-[1.02]"
                      style={{
                        background: "transparent",
                        border: "1px solid rgba(201,169,110,0.3)",
                        color: "#111111",
                      }}
                    >
                      {s}
                    </button>
                  ))}
                </div>
              ) : null}

              <div ref={bottomRef} />
            </div>

            <div className="border-t px-4 pb-4 pt-3" style={{ borderColor: "rgba(201,169,110,0.15)" }}>
              <form onSubmit={onSubmit} className="flex items-center gap-2">
                <input
                  ref={inputRef}
                  type="text"
                  value={draft}
                  onChange={(e) => setDraft(e.target.value)}
                  placeholder="Ask anything about radcrew…"
                  disabled={pending}
                  className="flex-1 rounded-xl px-4 py-3 text-sm outline-none transition-all disabled:opacity-50"
                  style={{
                    background: "rgba(201,169,110,0.06)",
                    border: "1px solid rgba(201,169,110,0.2)",
                    color: "#111111",
                  }}
                />
                <button
                  type="submit"
                  disabled={!canSend}
                  className="flex h-10 w-10 items-center justify-center rounded-xl transition-all duration-200 hover:scale-105 disabled:opacity-40"
                  style={{ background: "#111111" }}
                >
                  {pending ? (
                    <Loader2 className="h-4 w-4 animate-spin" style={{ color: "#C9A96E" }} />
                  ) : (
                    <Send className="h-4 w-4" style={{ color: "#C9A96E" }} />
                  )}
                </button>
              </form>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};
