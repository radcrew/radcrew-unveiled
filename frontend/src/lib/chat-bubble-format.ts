/**
 * Parse assistant chat text (lite Markdown + autolink fragments) into structured data.
 * Keeps regex and string rules out of UI components.
 */

const LINK_PATTERN = /(https?:\/\/[^\s<>()]+|[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})/gi;

const ORDERED_LINE = /^\d+\.\s+/;
const BULLET_LINE = /^-\s+/;

export type InlineSegment =
  | { kind: "text"; value: string }
  | { kind: "link"; href: string; label: string };

export type InlineRun = {
  bold: boolean;
  segments: InlineSegment[];
};

export type AssistantBlock =
  | { kind: "paragraph"; body: string }
  | { kind: "ordered"; items: string[] }
  | { kind: "unordered"; items: string[] };

function classifyFragment(fragment: string): InlineSegment {
  if (fragment.length === 0) {
    return { kind: "text", value: "" };
  }
  if (/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i.test(fragment)) {
    return { kind: "link", href: `mailto:${fragment}`, label: fragment };
  }
  if (/^https?:\/\//i.test(fragment)) {
    return { kind: "link", href: fragment, label: fragment };
  }
  return { kind: "text", value: fragment };
}

function splitByLinks(text: string): string[] {
  return text.split(LINK_PATTERN);
}

export function textToInlineSegments(text: string): InlineSegment[] {
  return splitByLinks(text).map(classifyFragment);
}

export function textToInlineRuns(text: string): InlineRun[] {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part) => {
    const boldMatch = /^\*\*([^*]+)\*\*$/.exec(part);
    const inner = boldMatch ? boldMatch[1] : part;
    const bold = Boolean(boldMatch);
    return { bold, segments: textToInlineSegments(inner) };
  });
}

function trimNonEmptyLines(block: string): string[] {
  return block.split("\n").filter((line) => line.trim().length > 0);
}

export function parseAssistantBlocks(content: string): AssistantBlock[] {
  return content
    .split(/\n{2,}/)
    .filter((b) => b.trim().length > 0)
    .map((block) => {
      const lines = trimNonEmptyLines(block);
      const allOrdered =
        lines.length > 0 && lines.every((line) => ORDERED_LINE.test(line.trim()));
      if (allOrdered) {
        return {
          kind: "ordered",
          items: lines.map((line) => line.trim().replace(ORDERED_LINE, "")),
        };
      }
      const allBullet =
        lines.length > 0 && lines.every((line) => BULLET_LINE.test(line.trim()));
      if (allBullet) {
        return {
          kind: "unordered",
          items: lines.map((line) => line.trim().replace(BULLET_LINE, "")),
        };
      }
      return { kind: "paragraph", body: block };
    });
}
