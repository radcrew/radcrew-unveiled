import { Loader2 } from "lucide-react";
import type { RefObject } from "react";
import type { ChatMessage } from "./types";
import { ChatBubble } from "./ChatBubble";

interface ChatMessageListProps {
  messages: ChatMessage[];
  pending: boolean;
  scrollAnchorRef: RefObject<HTMLDivElement | null>;
}

export function ChatMessageList({ messages, pending, scrollAnchorRef }: ChatMessageListProps) {
  return (
    <div className="min-h-0 flex-1 space-y-3 overflow-y-auto px-4 py-4">
      {messages.map((msg) => (
        <ChatBubble key={msg.id} role={msg.role} content={msg.content} sources={msg.sources} />
      ))}
      {pending && (
        <div className="mr-auto flex max-w-[92%] items-center gap-2 rounded-xl border border-border bg-muted/50 px-3 py-2.5 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 shrink-0 animate-spin" aria-hidden />
          Thinking…
        </div>
      )}
      <div ref={scrollAnchorRef} aria-hidden className="h-px w-full shrink-0" />
    </div>
  );
}
