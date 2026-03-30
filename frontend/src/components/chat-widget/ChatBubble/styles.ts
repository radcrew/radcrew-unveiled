import { cn } from "@/lib/utils";

export const link = "underline underline-offset-2";
export const assistantBody = "space-y-2";
export const orderedList = "list-decimal space-y-1 pl-5";
export const unorderedList = "list-disc space-y-1 pl-5";
export const assistantParagraph = "whitespace-pre-wrap";
export const userParagraph = "whitespace-pre-wrap";

export function shellClassName(role: "user" | "assistant"): string {
  return cn(
    "max-w-[92%] rounded-xl px-3 py-2.5 text-sm leading-relaxed shadow-sm",
    role === "user"
      ? "ml-auto bg-accent text-accent-foreground"
      : "mr-auto border border-border bg-card text-card-foreground",
  );
}
