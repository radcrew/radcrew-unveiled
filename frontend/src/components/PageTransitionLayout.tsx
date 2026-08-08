import { useEffect, useLayoutEffect } from "react";
import { Outlet, useLocation } from "react-router-dom";
import Navbar from "@components/Navbar";
import { scrollBehaviorForViewport, scrollSectionIntoView } from "@/lib/scroll-to-section";

export function PageTransitionLayout() {
  const { pathname, hash } = useLocation();

  useLayoutEffect(() => {
    if (pathname !== "/") return;
    const id = hash.replace(/^#/, "");
    if (!id) return;
    const run = () => scrollSectionIntoView(id);
    requestAnimationFrame(() => {
      requestAnimationFrame(run);
    });
  }, [pathname, hash]);

  useEffect(() => {
    const behavior = scrollBehaviorForViewport();
    const id = hash.replace(/^#/, "");

    if (pathname === "/" && id) return;

    window.scrollTo({ top: 0, left: 0, behavior });
  }, [pathname, hash]);

  return (
    <>
      {/* Index uses its own fixed nav (`Landing`); keep this bar for inner routes only. */}
      {pathname !== "/" ? <Navbar /> : null}
      {/*
        No `fill-mode-both`. It holds the enter keyframe's final state on the
        element forever, and that keyframe always sets a transform, even for a
        pure fade. An element with any transform other than `none` becomes the
        containing block for its `position: fixed` descendants, so `Landing`'s
        nav was positioned against this div rather than the viewport and scrolled
        away with the page despite computing as fixed. Without the fill mode the
        transform is present only while the 300ms animation runs, which happens
        at the top of the page where it cannot be seen.
      */}
      <div
        key={pathname}
        className="motion-safe:animate-in motion-safe:fade-in motion-safe:slide-in-from-bottom-2 motion-safe:duration-300"
      >
        <Outlet />
      </div>
    </>
  );
}
