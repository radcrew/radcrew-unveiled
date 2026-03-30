import { cn } from "@/lib/utils";
import type { ReactNode } from "react";

interface ChatBubbleProps {
  role: "user" | "assistant";
  content: string;
}

function renderInlineMarkdown(text: string): ReactNode[] {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, index) => {
    const boldMatch = /^\*\*([^*]+)\*\*$/.exec(part);
    if (boldMatch) {
      return <strong key={`b-${index}`}>{boldMatch[1]}</strong>;
    }
    return <span key={`t-${index}`}>{part}</span>;
  });
}

function renderAssistantContent(content: string): ReactNode {
  const blocks = content.split(/\n{2,}/).filter((b) => b.trim().length > 0);
  return (
    <div className="space-y-2">
      {blocks.map((block, index) => {
        const lines = block.split("\n").filter((line) => line.trim().length > 0);
        const ordered = lines.every((line) => /^\d+\.\s+/.test(line.trim()));
        const unordered = lines.every((line) => /^-\s+/.test(line.trim()));

        if (ordered) {
          return (
            <ol key={`o-${index}`} className="list-decimal space-y-1 pl-5">
              {lines.map((line, lineIndex) => (
                <li key={`ol-${index}-${lineIndex}`}>
                  {renderInlineMarkdown(line.trim().replace(/^\d+\.\s+/, ""))}
                </li>
              ))}
            </ol>
          );
        }

        if (unordered) {
          return (
            <ul key={`u-${index}`} className="list-disc space-y-1 pl-5">
              {lines.map((line, lineIndex) => (
                <li key={`ul-${index}-${lineIndex}`}>
                  {renderInlineMarkdown(line.trim().replace(/^-\s+/, ""))}
                </li>
              ))}
            </ul>
          );
        }

        return (
          <p key={`p-${index}`} className="whitespace-pre-wrap">
            {renderInlineMarkdown(block)}
          </p>
        );
      })}
    </div>
  );
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
      {role === "assistant" ? renderAssistantContent(content) : <p className="whitespace-pre-wrap">{content}</p>}
    </div>
  );
}
