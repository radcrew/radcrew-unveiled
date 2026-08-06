import { Link, useLocation } from "react-router-dom";
import { useState } from "react";
import { Menu, X } from "lucide-react";
import { RadButton } from "@components/ui/rad-button";
import { scrollSectionIntoView } from "@/lib/scroll-to-section";

/**
 * Section ids must exist on `Landing`; `how-we-work` was dropped when that
 * section was removed and pointed at nothing until this was corrected.
 */
const NAV_LINKS = [
  { hash: "services", label: "Services" },
  { hash: "portfolio", label: "Work" },
  { hash: "process", label: "Process" },
  { hash: "team", label: "Team" },
  { hash: "journal", label: "Journal" },
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
  // Matches the landing nav's treatment so inner routes do not read as a
  // different site.
  const className = "text-sm uppercase tracking-widest transition-colors hover:text-primary";

  if (pathname === "/") {
    return (
      <a
        href={`#${hash}`}
        className={className}
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
    <Link to={to} className={className} onClick={() => onNavigate?.()}>
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
        <Link to="/" className="text-xl font-light uppercase tracking-[0.25em]">
          radcrew
        </Link>

        <div className="hidden gap-8 md:flex">
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
        <div className="section-padding flex flex-col gap-4 border-t border-border bg-background py-4 md:hidden">
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
