import * as React from "react";

import { cn } from "@/lib/utils";

import { Button, type ButtonProps } from "./button";

/** Tailwind classes for accent outer + inner glow on hover; merge with `cn()` on any control. */
export const radButtonHoverClassName = cn(
  "transition-[box-shadow,border-color,background-color,color,opacity] duration-300 ease-out",
  "hover:border-accent/35",
  "hover:shadow-[0_0_0_1px_hsl(var(--accent)_/_0.12),0_10px_32px_-8px_hsl(var(--accent)_/_0.2),inset_0_0_24px_hsl(var(--accent)_/_0.06)]",
);

export const RadButton = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, ...props }, ref) => (
    <Button ref={ref} className={cn(radButtonHoverClassName, className)} {...props} />
  ),
);
RadButton.displayName = "RadButton";
