import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import type { FormEvent, RefObject } from "react";
import type { ChatMessage } from "./types";
import { ChatComposer } from "./ChatComposer";
import { ChatErrorBanner } from "./ChatErrorBanner";
import { ChatMessageList } from "./ChatMessageList";

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
    <SheetContent side="right" className="flex w-full flex-col gap-0 p-0 sm:max-w-md">
      <SheetHeader className="shrink-0 space-y-1 border-b border-border px-6 py-4 text-left">
        <SheetTitle className="text-lg">RadCrew FAQ</SheetTitle>
        <p className="text-xs text-muted-foreground">
          AI assistant responses may be inaccurate. Please verify important details.
        </p>
      </SheetHeader>

      <div className="flex min-h-0 flex-1 flex-col">
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
