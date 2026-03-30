import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import type { FormEvent, RefObject } from "react";
import { ChatComposer } from "../ChatComposer";
import { ChatErrorBanner } from "../ChatErrorBanner";
import { ChatMessageList } from "../ChatMessageList";
import type { ChatMessage } from "../types";
import * as styles from "./styles";

interface ChatPanelProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  messages: ChatMessage[];
  pending: boolean;
  showLoading: boolean;
  error: string | null;
  draft: string;
  onDraftChange: (value: string) => void;
  canSend: boolean;
  onSubmit: (e: FormEvent) => void;
  onSend: () => void;
  scrollAnchorRef: RefObject<HTMLDivElement | null>;
}

export const ChatPanel = ({
  open,
  onOpenChange,
  messages,
  pending,
  showLoading,
  error,
  draft,
  onDraftChange,
  canSend,
  onSubmit,
  onSend,
  scrollAnchorRef,
}: ChatPanelProps) => (
  <Sheet open={open} onOpenChange={onOpenChange}>
    <SheetContent side="right" className={styles.sheetContent}>
      <SheetHeader className={styles.sheetHeader}>
        <SheetTitle className={styles.sheetTitle}>RadCrew FAQ</SheetTitle>
        <p className={styles.disclaimer}>
          AI assistant responses may be inaccurate. Please verify important details.
        </p>
      </SheetHeader>

      <div className={styles.body}>
        <ChatMessageList messages={messages} showLoading={showLoading} scrollAnchorRef={scrollAnchorRef} />
        {error && <ChatErrorBanner message={error} />}
        <ChatComposer
          draft={draft}
          onDraftChange={onDraftChange}
          pending={pending}
          canSend={canSend}
          onSubmit={onSubmit}
          onSend={onSend}
        />
      </div>
    </SheetContent>
  </Sheet>
);
