import { Link } from "react-router-dom";
import { useState } from "react";
import { Menu, X } from "lucide-react";
import { Button } from "@/components/ui/button";

const NAV_LINKS = [
  { href: "#services", label: "Services" },
  { href: "#how-we-work", label: "How we work" },
  { href: "#portfolio", label: "Portfolio" },
  { href: "#team", label: "Team" },
  { href: "#contact", label: "Contact" },
] as const;

const Navbar = () => {
  const [open, setOpen] = useState(false);

  return (
    <nav className="nav-shell">
      <div className="nav-inner">
        <Link to="/" className="text-xl font-bold tracking-tight">
          Rad<span className="text-accent">Crew</span>
        </Link>

        <div className="hidden gap-8 text-sm font-medium md:flex">
          {NAV_LINKS.map(({ href, label }) => (
            <a key={href} href={href} className="nav-link">
              {label}
            </a>
          ))}
        </div>

        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="md:hidden"
          onClick={() => setOpen(!open)}
          aria-label="Toggle menu"
        >
          {open ? <X size={20} /> : <Menu size={20} />}
        </Button>
      </div>

      {open && (
        <div className="section-padding flex flex-col gap-4 border-t border-border bg-background py-4 text-sm font-medium md:hidden">
          {NAV_LINKS.map(({ href, label }) => (
            <a key={href} href={href} className="nav-link" onClick={() => setOpen(false)}>
              {label}
            </a>
          ))}
        </div>
      )}
    </nav>
  );
};

export default Navbar;
