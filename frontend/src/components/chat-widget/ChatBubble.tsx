import { cn } from "@/lib/utils";
import {
  parseAssistantBlocks,
  textToInlineRuns,
  type AssistantBlock,
  type InlineRun,
  type InlineSegment,
} from "@/lib/chat-bubble-format";
import type { ReactNode } from "react";

interface ChatBubbleProps {
  role: "user" | "assistant";
  content: string;
}

const isExternalHref = (href: string): boolean =>
  href.startsWith("http://") || href.startsWith("https://");

const SegmentList = ({ segments }: { segments: InlineSegment[] }): ReactNode =>
  segments
    .map((seg, i) => ({ seg, i }))
    .filter(({ seg }) => seg.kind !== "text" || seg.value.length > 0)
    .map(({ seg, i }) => {
      if (seg.kind === "text") {
        return <span key={`t-${i}`}>{seg.value}</span>;
      }
      const external = isExternalHref(seg.href);
      return (
        <a
          key={`a-${i}`}
          href={seg.href}
          target={external ? "_blank" : undefined}
          rel={external ? "noopener noreferrer" : undefined}
          className="underline underline-offset-2"
        >
          {seg.label}
        </a>
      );
    });

const InlineRunList = ({ runs }: { runs: InlineRun[] }): ReactNode =>
  runs.map((run, i) => {
    const inner = <SegmentList segments={run.segments} />;
    if (run.bold) {
      return <strong key={`b-${i}`}>{inner}</strong>;
    }
    return <span key={`p-${i}`}>{inner}</span>;
  });

const AssistantMessageBody = ({ content }: { content: string }): ReactNode => {
  const blocks: AssistantBlock[] = parseAssistantBlocks(content);

  return (
    <div className="space-y-2">
      {blocks.map((block, index) => {
        if (block.kind === "ordered") {
          return (
            <ol key={`o-${index}`} className="list-decimal space-y-1 pl-5">
              {block.items.map((item, lineIndex) => (
                <li key={`ol-${index}-${lineIndex}`}>
                  <InlineRunList runs={textToInlineRuns(item)} />
                </li>
              ))}
            </ol>
          );
        }

        if (block.kind === "unordered") {
          return (
            <ul key={`u-${index}`} className="list-disc space-y-1 pl-5">
              {block.items.map((item, lineIndex) => (
                <li key={`ul-${index}-${lineIndex}`}>
                  <InlineRunList runs={textToInlineRuns(item)} />
                </li>
              ))}
            </ul>
          );
        }

        return (
          <p key={`p-${index}`} className="whitespace-pre-wrap">
            <InlineRunList runs={textToInlineRuns(block.body)} />
          </p>
        );
      })}
    </div>
  );
};

export const ChatBubble = ({ role, content }: ChatBubbleProps) => (
  <div
    className={cn(
      "max-w-[92%] rounded-xl px-3 py-2.5 text-sm leading-relaxed shadow-sm",
      role === "user"
        ? "ml-auto bg-accent text-accent-foreground"
        : "mr-auto border border-border bg-card text-card-foreground",
    )}
  >
    {role === "assistant" ? <AssistantMessageBody content={content} /> : <p className="whitespace-pre-wrap">{content}</p>}
  </div>
);
