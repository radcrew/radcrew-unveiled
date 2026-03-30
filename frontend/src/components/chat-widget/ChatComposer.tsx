import type { FormEvent } from "react";
import { Loader2, SendHorizontal } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

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
  <form onSubmit={onSubmit} className="shrink-0 space-y-2 border-t border-border bg-background p-4">
    <Textarea
      value={draft}
      onChange={(e) => onDraftChange(e.target.value)}
      placeholder="e.g. What does RadCrew build? How do I contact you?"
      rows={3}
      className="min-h-[5rem] resize-none"
      disabled={pending}
      onKeyDown={(e) => {
        if (e.key === "Enter" && !e.shiftKey) {
          e.preventDefault();
          if (canSend) void onSend();
        }
      }}
    />
    <div className="flex justify-end">
      <Button type="submit" disabled={!canSend} className="gap-2">
        {pending ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" />
            Sending
          </>
        ) : (
          <>
            <SendHorizontal className="h-4 w-4" />
            Send
          </>
        )}
      </Button>
    </div>
  </form>
);
