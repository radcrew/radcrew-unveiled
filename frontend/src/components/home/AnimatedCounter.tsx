import { useEffect, useRef, useState } from "react";
import { useReducedMotion } from "framer-motion";

export function AnimatedCounter({
  end,
  suffix = "",
  duration = 2,
  decimals = 0,
  className = "font-serif text-5xl text-foreground md:text-6xl",
  suffixClassName = "text-primary",
}: {
  end: number;
  suffix?: string;
  duration?: number;
  decimals?: number;
  className?: string;
  /** Override on dark sections, where `text-primary` is too dark to read. */
  suffixClassName?: string;
}) {
  const reduced = useReducedMotion();
  const [value, setValue] = useState(reduced ? end : 0);
  const nodeRef = useRef<HTMLDivElement>(null);
  const [inView, setInView] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting) {
          setInView(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1 },
    );
    if (nodeRef.current) observer.observe(nodeRef.current);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    // Counting up is the animation here, so reduced motion means showing the
    // final number rather than tweening to it.
    if (!inView || reduced) return;
    let startTime: number | null = null;
    let animationFrameId = 0;

    const animate = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / (duration * 1000), 1);
      const easeProgress = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
      setValue(easeProgress * end);
      if (progress < 1) {
        animationFrameId = requestAnimationFrame(animate);
      }
    };

    animationFrameId = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationFrameId);
  }, [end, duration, inView, reduced]);

  return (
    <div ref={nodeRef} className={className}>
      {decimals > 0 ? value.toFixed(decimals) : Math.floor(value)}
      <span className={`ml-1 ${suffixClassName}`}>{suffix}</span>
    </div>
  );
}
