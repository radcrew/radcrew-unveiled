import { useRef, type PointerEvent, type ReactNode } from "react";
import { motion, useMotionValue, useReducedMotion, useSpring } from "framer-motion";

type MagneticProps = {
  children: ReactNode;
  /** Share of the cursor's offset from centre that the child follows. */
  strength?: number;
  className?: string;
};

/**
 * Pulls its children toward the pointer on hover. Wrap a button or link rather
 * than replacing it, so focus, keyboard activation and semantics stay with the
 * caller's element.
 *
 * Bound to pointer events with a `(hover: hover)` guard: on touch the pointer
 * lands at the tap position and the child would jump under the finger.
 */
export const Magnetic = ({ children, strength = 0.35, className }: MagneticProps) => {
  const ref = useRef<HTMLDivElement>(null);
  const reduced = useReducedMotion();
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const springX = useSpring(x, { stiffness: 200, damping: 18, mass: 0.4 });
  const springY = useSpring(y, { stiffness: 200, damping: 18, mass: 0.4 });

  const handleMove = (event: PointerEvent<HTMLDivElement>) => {
    if (!ref.current || !window.matchMedia("(hover: hover)").matches) return;
    const rect = ref.current.getBoundingClientRect();
    x.set((event.clientX - (rect.left + rect.width / 2)) * strength);
    y.set((event.clientY - (rect.top + rect.height / 2)) * strength);
  };

  const reset = () => {
    x.set(0);
    y.set(0);
  };

  if (reduced) return <div className={className}>{children}</div>;

  return (
    <motion.div
      ref={ref}
      onPointerMove={handleMove}
      onPointerLeave={reset}
      style={{ x: springX, y: springY }}
      className={className}
    >
      {children}
    </motion.div>
  );
};
