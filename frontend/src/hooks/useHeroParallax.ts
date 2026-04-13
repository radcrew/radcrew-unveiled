import { useEffect, useRef, type RefObject } from "react";

/** Subtle background drift while the hero is on screen (skipped when reduced motion is on). */
export function useHeroParallax(): RefObject<HTMLElement | null> {
  const ref = useRef<HTMLElement | null>(null);

  useEffect(() => {
    const root = ref.current;
    if (!root) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    const img = root.querySelector(".hero-bg-img");
    if (!(img instanceof HTMLElement)) return;

    let raf = 0;
    const update = () => {
      raf = 0;
      const rect = root.getBoundingClientRect();
      if (rect.bottom <= 0 || rect.top >= window.innerHeight) return;
      const travel = Math.min(1, Math.max(0, -rect.top / Math.max(1, rect.height)));
      const offset = travel * 72;
      img.style.transform = `translate3d(0, ${offset}px, 0) scale(1.07)`;
    };

    const onScroll = () => {
      if (!raf) raf = requestAnimationFrame(update);
    };

    update();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll, { passive: true });
    return () => {
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
      if (raf) cancelAnimationFrame(raf);
    };
  }, []);

  return ref;
}
