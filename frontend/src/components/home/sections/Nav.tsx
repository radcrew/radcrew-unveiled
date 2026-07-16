import { useRef, useState } from "react";
import { Link } from "react-router-dom";
import { Menu } from "lucide-react";
import { Button } from "@components/ui/button";
import { Sheet, SheetContent, SheetDescription, SheetTitle, SheetTrigger } from "@components/ui/sheet";

type NavProps = {
  isScrolled: boolean;
  onNavigate: (sectionId: string) => void;
};

const navLinks = [
  { id: "services", label: "Services" },
  { id: "portfolio", label: "Work" },
  { id: "process", label: "Process" },
] as const;

export const Nav = ({ isScrolled, onNavigate }: NavProps) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const navigatingRef = useRef(false);

  const handleMobileNavigate = (id: string) => {
    navigatingRef.current = true;
    setMobileOpen(false);
    onNavigate(id);
  };

  return (
    <nav
      className={`fixed left-0 right-0 top-0 z-50 transition-all duration-500 ${
        isScrolled ? "border-b border-primary/20 bg-background/90 py-4 backdrop-blur-xl" : "bg-transparent py-6"
      }`}
    >
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 lg:px-12">
        <Link
          to="/"
          className="-ml-6 cursor-pointer text-xl font-light uppercase tracking-[0.25em] lg:-ml-12"
          data-testid="nav-logo"
        >
          radcrew
        </Link>
        <div className="hidden items-center gap-10 text-sm uppercase tracking-widest md:flex">
          <button
            type="button"
            onClick={() => onNavigate("services")}
            className="transition-colors hover:text-primary"
            data-testid="nav-services"
          >
            Services
          </button>
          <button
            type="button"
            onClick={() => onNavigate("portfolio")}
            className="transition-colors hover:text-primary"
            data-testid="nav-portfolio"
          >
            Work
          </button>
          <button
            type="button"
            onClick={() => onNavigate("process")}
            className="transition-colors hover:text-primary"
            data-testid="nav-process"
          >
            Process
          </button>
          <Button
            type="button"
            onClick={() => onNavigate("contact")}
            variant="outline"
            className="h-auto rounded-none border-primary px-8 py-5 font-light uppercase tracking-widest text-primary hover:bg-primary hover:text-primary-foreground"
            data-testid="nav-contact"
          >
            Get in Touch
          </Button>
        </div>

        <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
          <SheetTrigger asChild>
            <button
              type="button"
              className="text-foreground md:hidden"
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
                  className="text-left transition-colors hover:text-primary"
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
