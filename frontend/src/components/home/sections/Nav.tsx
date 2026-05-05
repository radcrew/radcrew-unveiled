import { Link } from "react-router-dom";
import { Button } from "@components/ui/button";

type NavProps = {
  isScrolled: boolean;
  onNavigate: (sectionId: string) => void;
};

export function Nav({ isScrolled, onNavigate }: NavProps) {
  return (
    <nav
      className={`fixed left-0 right-0 top-0 z-50 transition-all duration-500 ${
        isScrolled ? "border-b border-primary/20 bg-background/90 py-4 backdrop-blur-xl" : "bg-transparent py-6"
      }`}
    >
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 lg:px-12">
        <Link to="/" className="cursor-pointer text-xl font-light uppercase tracking-[0.25em]" data-testid="nav-logo">
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
          <button
            type="button"
            onClick={() => onNavigate("team")}
            className="transition-colors hover:text-primary"
            data-testid="nav-team"
          >
            Team
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
      </div>
    </nav>
  );
}
