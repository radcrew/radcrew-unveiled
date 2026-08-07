import { useRef, useState } from "react";
import { Link } from "react-router-dom";
import { motion, useReducedMotion } from "framer-motion";
import { Menu } from "lucide-react";
import { Button } from "@components/ui/button";
import { Sheet, SheetContent, SheetDescription, SheetTitle, SheetTrigger } from "@components/ui/sheet";
import { announceOverlayOpened, useCloseOnOtherOverlayOpen } from "@/lib/overlay-events";

type NavProps = {
  isScrolled: boolean;
  activeSection: string;
  onNavigate: (sectionId: string) => void;
};

const navLinks = [
  { id: "services", label: "Services" },
  { id: "portfolio", label: "Work" },
  { id: "process", label: "Process" },
  { id: "journal", label: "Journal" },
] as const;

const focusRingClassName =
  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background";

export const Nav = ({ isScrolled, activeSection, onNavigate }: NavProps) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const navigatingRef = useRef(false);
  const reduced = useReducedMotion();

  useCloseOnOtherOverlayOpen("nav", () => setMobileOpen(false));

  const handleMobileOpenChange = (next: boolean) => {
    setMobileOpen(next);
    if (next) announceOverlayOpened("nav");
  };

  const handleMobileNavigate = (id: string) => {
    navigatingRef.current = true;
    setMobileOpen(false);
    onNavigate(id);
  };

  // The indicator is one element that moves between links rather than a colour
  // swap per link, so the eye follows it across the bar. Reduced motion keeps
  // the move but drops the travel, which is the part that reads as animation.
  const indicatorTransition = reduced
    ? { duration: 0 }
    : { type: "spring" as const, stiffness: 380, damping: 32 };

  return (
    // The bar floats clear of the viewport edge instead of sitting flush to it,
    // so the page scrolls visibly *under* glass rather than behind an opaque
    // strip. The outer element keeps the old horizontal padding, and the pill
    // inside it is capped at `max-w-7xl`, so the pill's edges land on the same
    // measure as every section below. Total occupied height is the 16px offset
    // plus the ~64px pill, which is the 5rem `--site-header-height` that
    // `scroll-padding-top` already assumes; leave both in step.
    <nav
      className={`fixed left-0 right-0 z-50 px-4 transition-all duration-500 lg:px-8 ${
        isScrolled ? "top-2" : "top-4"
      }`}
    >
      <div
        className={`mx-auto flex max-w-7xl items-center justify-between gap-6 rounded-full border px-5 py-3 backdrop-blur-xl transition-colors duration-500 ${
          isScrolled
            ? // Over the cream body. The inset highlight is what separates glass
              // from a plain translucent panel: it fakes the lit top edge.
              "border-border/70 bg-background/70 text-foreground shadow-[0_10px_36px_-16px_hsl(26_14%_9%/0.32),inset_0_1px_0_hsl(0_0%_100%/0.8)]"
            : // Over the dark hero, tinted the other way so the type stays cream.
              "border-background/20 bg-background/10 text-background shadow-[inset_0_1px_0_hsl(0_0%_100%/0.22)]"
        }`}
      >
        <Link
          to="/"
          className={`cursor-pointer pl-1 text-lg font-light uppercase tracking-[0.25em] ${focusRingClassName}`}
          data-testid="nav-logo"
        >
          radcrew
        </Link>

        <div className="hidden items-center gap-1 text-xs uppercase tracking-widest md:flex">
          {navLinks.map((link) => {
            const isActive = activeSection === link.id;
            return (
              <button
                key={link.id}
                type="button"
                onClick={() => onNavigate(link.id)}
                className={`relative rounded-full px-4 py-2 transition-colors ${focusRingClassName} ${
                  isActive
                    ? isScrolled
                      ? "text-primary"
                      : "text-primary-on-dark"
                    : isScrolled
                      ? "text-muted-foreground hover:text-foreground"
                      : "text-background/70 hover:text-background"
                }`}
                data-testid={`nav-${link.id}`}
              >
                {isActive && (
                  <motion.span
                    layoutId="nav-active-pill"
                    aria-hidden="true"
                    transition={indicatorTransition}
                    className={`absolute inset-0 rounded-full ${
                      isScrolled ? "bg-primary/10" : "bg-background/15"
                    }`}
                  />
                )}
                <span className="relative">{link.label}</span>
              </button>
            );
          })}
          <Button
            type="button"
            onClick={() => onNavigate("contact")}
            variant="outline"
            className={`ml-2 h-auto rounded-full px-6 py-2.5 text-xs font-light uppercase tracking-widest transition-colors ${
              isScrolled
                ? "border-primary text-primary hover:bg-primary hover:text-primary-foreground"
                : "border-background/40 bg-transparent text-background hover:bg-background hover:!text-foreground"
            }`}
            data-testid="nav-contact"
          >
            Get in Touch
          </Button>
        </div>

        <Sheet open={mobileOpen} onOpenChange={handleMobileOpenChange}>
          <SheetTrigger asChild>
            <button
              type="button"
              className={`rounded-full p-1 md:hidden ${focusRingClassName}`}
              aria-label="Open menu"
              data-testid="nav-mobile-trigger"
            >
              <Menu className="h-6 w-6" />
            </button>
          </SheetTrigger>
          <SheetContent
            side="right"
            className="w-3/4 rounded-none border-border bg-background sm:max-w-xs"
            onCloseAutoFocus={(e) => {
              if (navigatingRef.current) {
                e.preventDefault();
                navigatingRef.current = false;
              }
            }}
          >
            <SheetTitle className="text-left text-sm font-light uppercase tracking-widest text-muted-foreground">
              Menu
            </SheetTitle>
            <SheetDescription className="sr-only">Site navigation</SheetDescription>
            <div className="mt-10 flex flex-col gap-8 text-lg uppercase tracking-widest">
              {navLinks.map((link) => (
                <button
                  key={link.id}
                  type="button"
                  onClick={() => handleMobileNavigate(link.id)}
                  className={`text-left transition-colors hover:text-primary ${focusRingClassName} ${
                    activeSection === link.id ? "text-primary" : ""
                  }`}
                  data-testid={`nav-mobile-${link.id}`}
                >
                  {link.label}
                </button>
              ))}
              <Button
                type="button"
                onClick={() => handleMobileNavigate("contact")}
                variant="outline"
                className="h-auto w-full rounded-full border-primary px-8 py-5 font-light uppercase tracking-widest text-primary hover:bg-primary hover:text-primary-foreground"
                data-testid="nav-mobile-contact"
              >
                Get in Touch
              </Button>
            </div>
          </SheetContent>
        </Sheet>
      </div>
    </nav>
  );
};
