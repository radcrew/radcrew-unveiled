import * as React from "react";

import { cn } from "@/lib/utils";

import { Card } from "./card";

/** Tailwind classes for accent outer + inner glow on hover; merge with `cn()` on any surface. */
export const radCardHoverClassName = cn(
  "transition-[box-shadow,border-color] duration-300 ease-out",
  "hover:border-accent/35",
  "hover:shadow-[0_0_0_1px_hsl(var(--accent)_/_0.12),0_12px_40px_-8px_hsl(var(--accent)_/_0.2),inset_0_0_32px_hsl(var(--accent)_/_0.06)]",
);

export const RadCard = React.forwardRef<HTMLDivElement, React.ComponentPropsWithoutRef<typeof Card>>(
  ({ className, ...props }, ref) => (
    <Card ref={ref} className={cn(radCardHoverClassName, className)} {...props} />
  ),
);
RadCard.displayName = "RadCard";
