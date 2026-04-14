export function prefersScrollReducedMotion(): boolean {
  return typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

export function scrollBehaviorForViewport(): ScrollBehavior {
  return prefersScrollReducedMotion() ? "auto" : "smooth";
}

/** Smooth (or instant if reduced motion) scroll to an element id; returns whether the target existed. */
export function scrollSectionIntoView(id: string): boolean {
  const el = document.getElementById(id);
  if (!el) return false;
  el.scrollIntoView({
    behavior: scrollBehaviorForViewport(),
    block: el.dataset.scrollBlock === "end" ? "end" : "start",
  });
  return true;
}
