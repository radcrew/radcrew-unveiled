import { cn } from "@/lib/utils";

export const button = cn(
  "fixed bottom-6 left-1/2 z-40 h-12 w-[min(640px,calc(100vw-2rem))] -translate-x-1/2",
  "rounded-full border border-border bg-background px-4 shadow-lg",
  "justify-start gap-2 text-left text-muted-foreground hover:bg-muted",
);

export const icon = "h-4 w-4 shrink-0";
export const placeholder = "truncate text-sm";
