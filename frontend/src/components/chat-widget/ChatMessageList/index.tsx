import { Loader2 } from "lucide-react";
import type { RefObject } from "react";
import { ChatBubble } from "../ChatBubble";
import type { ChatMessage } from "../types";
import * as styles from "./styles";

interface ChatMessageListProps {
  messages: ChatMessage[];
  showLoading: boolean;
  scrollAnchorRef: RefObject<HTMLDivElement | null>;
}

export const ChatMessageList = ({ messages, showLoading, scrollAnchorRef }: ChatMessageListProps) => {
  const visibleMessages = messages.filter((msg) => msg.role === "user" || msg.content.trim().length > 0);

  return (
    <div className={styles.root}>
      {visibleMessages.map((msg) => (
        <ChatBubble key={msg.id} role={msg.role} content={msg.content} />
      ))}
      {showLoading && (
        <div className={styles.loadingRow}>
          <Loader2 className={styles.loadingSpinner} aria-hidden />
          Thinking…
        </div>
      )}
      <div ref={scrollAnchorRef} aria-hidden className={styles.scrollAnchor} />
    </div>
  );
};
