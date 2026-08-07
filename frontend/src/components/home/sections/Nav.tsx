import { useRef, useState } from "react";
import { Link } from "react-router-dom";
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

  return (
    // Padding sits on the nav, outside `max-w-7xl`, matching every section so
    // nav content lines up with page content at any width. These were nested
    // the other way round, and the logo used a negative margin to compensate,
    // which put it flush against the viewport edge below 1280px.
    <nav
      className={`fixed left-0 right-0 top-0 z-50 px-6 transition-all duration-500 lg:px-12 ${
        isScrolled
          ? "border-b border-primary/20 bg-background/90 py-4 text-foreground backdrop-blur-xl"
          : // Unscrolled, the bar sits over the dark hero, so it inverts.
            "bg-transparent py-6 text-background"
      }`}
    >
      <div className="mx-auto flex max-w-7xl items-center justify-between">
        <Link to="/" className="cursor-pointer text-xl font-light uppercase tracking-[0.25em]" data-testid="nav-logo">
          radcrew
        </Link>
        <div className="hidden items-center gap-10 text-sm uppercase tracking-widest md:flex">
          {navLinks.map((link) => (
            <button
              key={link.id}
              type="button"
              onClick={() => onNavigate(link.id)}
              className={`transition-colors hover:text-primary ${focusRingClassName} ${
                activeSection === link.id ? "text-primary" : ""
              }`}
              data-testid={`nav-${link.id}`}
            >
              {link.label}
            </button>
          ))}
          <Button
            type="button"
            onClick={() => onNavigate("contact")}
            variant="outline"
            className={`h-auto rounded-none px-8 py-5 font-light uppercase tracking-widest transition-colors ${
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
              className={`md:hidden ${focusRingClassName}`}
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
                  className={`text-left transition-colors hover:text-primary ${focusRingClassName}`}
                  data-testid={`nav-mobile-${link.id}`}
                >
                  {link.label}
                </button>
              ))}
              <Button
                type="button"
                onClick={() => handleMobileNavigate("contact")}
                variant="outline"
                className="h-auto w-full rounded-none border-primary px-8 py-5 font-light uppercase tracking-widest text-primary hover:bg-primary hover:text-primary-foreground"
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
