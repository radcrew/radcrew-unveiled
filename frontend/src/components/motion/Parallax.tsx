import { useRef, type ReactNode } from "react";
import { motion, useReducedMotion, useScroll, useTransform } from "framer-motion";

type ParallaxProps = {
  children: ReactNode;
  /** Pixels of travel across the full pass through the viewport. */
  distance?: number;
  className?: string;
};

/**
 * Drifts its children against the scroll direction as the wrapper crosses the
 * viewport. Disabled entirely under `prefers-reduced-motion`, since parallax is
 * one of the more common vestibular triggers.
 */
export const Parallax = ({ children, distance = 80, className }: ParallaxProps) => {
  const ref = useRef<HTMLDivElement>(null);
  const reduced = useReducedMotion();
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start end", "end start"] });
  const y = useTransform(scrollYProgress, [0, 1], [distance, -distance]);

  if (reduced) return <div className={className}>{children}</div>;

  return (
    <div ref={ref} className={className}>
      <motion.div style={{ y }}>{children}</motion.div>
    </div>
  );
};
