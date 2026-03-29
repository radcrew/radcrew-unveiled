import { cn } from "@/lib/utils";

interface ChatBubbleProps {
  role: "user" | "assistant";
  content: string;
}

export function ChatBubble({ role, content }: ChatBubbleProps) {
  return (
    <div
      className={cn(
        "max-w-[92%] rounded-xl px-3 py-2.5 text-sm leading-relaxed shadow-sm",
        role === "user"
          ? "ml-auto bg-accent text-accent-foreground"
          : "mr-auto border border-border bg-card text-card-foreground",
      )}
    >
      <p className="whitespace-pre-wrap">{content}</p>
    </div>
  );
}
