import type { ReactNode } from "react";
import { motion, useReducedMotion } from "framer-motion";

const offsets = {
  up: { x: 0, y: 30 },
  down: { x: 0, y: -30 },
  left: { x: 40, y: 0 },
  right: { x: -40, y: 0 },
} as const;

type RevealProps = {
  children: ReactNode;
  /** Side the content travels in from. */
  from?: keyof typeof offsets;
  delay?: number;
  className?: string;
};

/**
 * Scroll-triggered entrance. Under `prefers-reduced-motion` the content is
 * rendered in its final state with no transition, so nothing moves or fades in.
 */
export const Reveal = ({ children, from = "up", delay = 0, className }: RevealProps) => {
  const reduced = useReducedMotion();

  if (reduced) return <div className={className}>{children}</div>;

  return (
    <motion.div
      initial={{ opacity: 0, ...offsets[from] }}
      whileInView={{ opacity: 1, x: 0, y: 0 }}
      viewport={{ once: true, margin: "-80px" }}
      transition={{ duration: 0.8, delay, ease: [0.16, 1, 0.3, 1] }}
      className={className}
    >
      {children}
    </motion.div>
  );
};
