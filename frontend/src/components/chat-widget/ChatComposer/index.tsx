import type { FormEvent } from "react";
import { Loader2, SendHorizontal } from "lucide-react";
import { RadButton } from "@/components/ui/rad-button";
import { Textarea } from "@/components/ui/textarea";
import * as styles from "./styles";

interface ChatComposerProps {
  draft: string;
  onDraftChange: (value: string) => void;
  pending: boolean;
  canSend: boolean;
  onSubmit: (e: FormEvent) => void;
  onSend: () => void;
}

export const ChatComposer = ({
  draft,
  onDraftChange,
  pending,
  canSend,
  onSubmit,
  onSend,
}: ChatComposerProps) => (
  <form onSubmit={onSubmit} className={styles.form}>
    <Textarea
      value={draft}
      onChange={(e) => onDraftChange(e.target.value)}
      placeholder="e.g. What does RadCrew build? How do I contact you?"
      rows={3}
      className={styles.textarea}
      disabled={pending}
      onKeyDown={(e) => {
        if (e.key === "Enter" && !e.shiftKey) {
          e.preventDefault();
          if (canSend) void onSend();
        }
      }}
    />
    <div className={styles.actionsRow}>
      <RadButton type="submit" disabled={!canSend} className={styles.submitButton}>
        {pending ? (
          <>
            <Loader2 className={styles.pendingSpinner} />
            Sending
          </>
        ) : (
          <>
            <SendHorizontal className={styles.sendIcon} />
            Send
          </>
        )}
      </RadButton>
    </div>
  </form>
);
