import { Link, useLocation } from "react-router-dom";
import { useState } from "react";
import { Menu, X } from "lucide-react";
import { RadButton } from "@components/ui/rad-button";
import { scrollSectionIntoView } from "@/lib/scroll-to-section";

const NAV_LINKS = [
  { hash: "services", label: "Services" },
  { hash: "how-we-work", label: "How we work" },
  { hash: "portfolio", label: "Portfolio" },
  { hash: "team", label: "Team" },
  { hash: "contact", label: "Contact" },
] as const;

function SectionNavLink({
  hash,
  label,
  pathname,
  onNavigate,
}: {
  hash: string;
  label: string;
  pathname: string;
  onNavigate?: () => void;
}) {
  const to = `/#${hash}`;

  if (pathname === "/") {
    return (
      <a
        href={`#${hash}`}
        className="nav-link"
        onClick={(e) => {
          e.preventDefault();
          scrollSectionIntoView(hash);
          window.history.replaceState(null, "", `#${hash}`);
          onNavigate?.();
        }}
      >
        {label}
      </a>
    );
  }

  return (
    <Link to={to} className="nav-link" onClick={() => onNavigate?.()}>
      {label}
    </Link>
  );
}

const Navbar = () => {
  const [open, setOpen] = useState(false);
  const { pathname } = useLocation();

  return (
    <nav className="nav-shell">
      <div className="nav-inner">
        <Link to="/" className="text-xl font-bold tracking-tight">
          Rad<span className="text-accent">Crew</span>
        </Link>

        <div className="hidden gap-8 text-sm font-medium md:flex">
          {NAV_LINKS.map(({ hash, label }) => (
            <SectionNavLink key={hash} hash={hash} label={label} pathname={pathname} />
          ))}
        </div>

        <RadButton
          type="button"
          variant="ghost"
          size="icon"
          className="md:hidden"
          onClick={() => setOpen(!open)}
          aria-label="Toggle menu"
        >
          {open ? <X size={20} /> : <Menu size={20} />}
        </RadButton>
      </div>

      {open && (
        <div className="section-padding flex flex-col gap-4 border-t border-border bg-background py-4 text-sm font-medium md:hidden">
          {NAV_LINKS.map(({ hash, label }) => (
            <SectionNavLink
              key={hash}
              hash={hash}
              label={label}
              pathname={pathname}
              onNavigate={() => setOpen(false)}
            />
          ))}
        </div>
      )}
    </nav>
  );
};

export default Navbar;
