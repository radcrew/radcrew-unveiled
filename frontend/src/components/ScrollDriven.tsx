import { useEffect, useRef, type CSSProperties, type ReactNode } from "react";

import { cn } from "@/lib/utils";

type ScrollDrivenProps = {
  children: ReactNode;
  className?: string;
  style?: CSSProperties;
};

/**
 * Scroll-linked entrance: uses CSS scroll-driven animations when supported,
 * otherwise a one-shot reveal when the block enters the viewport.
 */
export function ScrollDriven({ children, className, style }: ScrollDrivenProps) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      el.dataset.revealed = "true";
      return;
    }

    const nativeTimeline =
      typeof CSS !== "undefined" &&
      (CSS.supports("animation-timeline", "view()") || CSS.supports("animation-timeline", "view(block)"));

    if (nativeTimeline) {
      el.classList.add("scroll-driven-native");
      return;
    }

    el.classList.add("scroll-driven-fallback");
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          el.dataset.revealed = "true";
          observer.disconnect();
        }
      },
      { threshold: 0.12, rootMargin: "0px 0px -6% 0px" },
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <div ref={ref} className={cn("scroll-driven", className)} style={style}>
      {children}
    </div>
  );
}
