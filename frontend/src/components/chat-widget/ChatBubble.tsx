import type { ChatbotSource } from "@/lib/chatbot-api";
import { cn } from "@/lib/utils";

interface ChatBubbleProps {
  role: "user" | "assistant";
  content: string;
  sources?: ChatbotSource[];
}

export function ChatBubble({ role, content, sources }: ChatBubbleProps) {
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
      {role === "assistant" && sources && sources.length > 0 && (
        <p className="mt-2 border-t border-border/60 pt-2 text-xs text-muted-foreground">
          Sources:{" "}
          {sources.slice(0, 3).map((s) => (
            <span key={s.id} className="mr-2 inline-block">
              {s.url ? (
                <a
                  href={s.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="underline-offset-2 hover:text-accent hover:underline"
                >
                  {s.title}
                </a>
              ) : (
                s.title
              )}
            </span>
          ))}
        </p>
      )}
    </div>
  );
}
