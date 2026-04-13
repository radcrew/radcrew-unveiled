import { useEffect, useLayoutEffect } from "react";
import { Outlet, useLocation } from "react-router-dom";
import Navbar from "@/components/Navbar";
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
      {/* Outside the animated layer so `position: fixed` on the nav is viewport-relative (transform creates a containing block). */}
      <Navbar />
      <div
        key={pathname}
        className="motion-safe:animate-in motion-safe:fade-in motion-safe:slide-in-from-bottom-2 motion-safe:duration-300 motion-safe:fill-mode-both"
      >
        <Outlet />
      </div>
    </>
  );
}
