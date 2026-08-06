import { motion, useScroll, useSpring } from "framer-motion";

/**
 * Fixed reading-progress bar for the top of the page.
 *
 * Deliberately not gated on `prefers-reduced-motion`: the bar tracks scroll
 * position directly rather than animating on its own, so it carries none of the
 * self-driven movement that setting is meant to suppress.
 */
export const ScrollProgress = () => {
  const { scrollYProgress } = useScroll();
  const scaleX = useSpring(scrollYProgress, { stiffness: 120, damping: 30, restDelta: 0.001 });

  return (
    <motion.div
      style={{ scaleX }}
      className="fixed left-0 top-0 z-[60] h-[2px] w-full origin-left bg-primary"
      aria-hidden="true"
    />
  );
};
