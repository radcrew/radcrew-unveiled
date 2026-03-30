import {
  parseAssistantBlocks,
  textToInlineRuns,
  type AssistantBlock,
  type InlineRun,
  type InlineSegment,
} from "@/lib/chat-bubble-format";
import type { ReactNode } from "react";
import * as styles from "./styles";

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
          className={styles.link}
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
    <div className={styles.assistantBody}>
      {blocks.map((block, index) => {
        if (block.kind === "ordered") {
          return (
            <ol key={`o-${index}`} className={styles.orderedList}>
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
            <ul key={`u-${index}`} className={styles.unorderedList}>
              {block.items.map((item, lineIndex) => (
                <li key={`ul-${index}-${lineIndex}`}>
                  <InlineRunList runs={textToInlineRuns(item)} />
                </li>
              ))}
            </ul>
          );
        }

        return (
          <p key={`p-${index}`} className={styles.assistantParagraph}>
            <InlineRunList runs={textToInlineRuns(block.body)} />
          </p>
        );
      })}
    </div>
  );
};

export const ChatBubble = ({ role, content }: ChatBubbleProps) => (
  <div className={styles.shellClassName(role)}>
    {role === "assistant" ? (
      <AssistantMessageBody content={content} />
    ) : (
      <p className={styles.userParagraph}>{content}</p>
    )}
  </div>
);
