import type { ReactNode } from "react";
import { motion, useReducedMotion } from "framer-motion";

type MarqueeProps = {
  children: ReactNode;
  /** Seconds for one full pass. Higher is slower. */
  duration?: number;
  reverse?: boolean;
  className?: string;
};

/**
 * Continuous horizontal scroll. `children` is rendered twice and the track is
 * translated by exactly half its width, so the second copy lands where the
 * first started and the loop has no visible seam.
 *
 * Under `prefers-reduced-motion` a single static copy is rendered in a
 * horizontally scrollable row, so the content stays reachable without motion.
 */
export const Marquee = ({ children, duration = 40, reverse = false, className }: MarqueeProps) => {
  const reduced = useReducedMotion();

  if (reduced) {
    return (
      <div className={`overflow-x-auto ${className ?? ""}`}>
        <div className="flex w-max items-center">{children}</div>
      </div>
    );
  }

  return (
    <div className={`overflow-hidden ${className ?? ""}`}>
      <motion.div
        className="flex w-max items-center"
        animate={{ x: reverse ? ["-50%", "0%"] : ["0%", "-50%"] }}
        transition={{ duration, ease: "linear", repeat: Infinity }}
      >
        <div className="flex shrink-0 items-center">{children}</div>
        <div className="flex shrink-0 items-center" aria-hidden="true">
          {children}
        </div>
      </motion.div>
    </div>
  );
};
