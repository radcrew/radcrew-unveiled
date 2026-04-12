import { cn } from "@/lib/utils";

export const button = cn(
  "fixed bottom-6 right-6 z-40 h-10 w-auto max-w-[calc(100vw-3rem)]",
  "rounded-full border border-border bg-background px-3 shadow-lg",
  "justify-start gap-1.5 text-left text-muted-foreground hover:bg-muted",
  "[&_svg]:h-3.5 [&_svg]:w-3.5 [&_svg]:shrink-0",
);

export const icon = "shrink-0";
export const placeholder = "text-sm";
