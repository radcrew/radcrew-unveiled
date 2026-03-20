import { Link } from "react-router-dom";
import { useState } from "react";
import { Menu, X } from "lucide-react";

const Navbar = () => {
  const [open, setOpen] = useState(false);

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-md border-b border-border">
      <div className="max-w-6xl mx-auto section-padding flex items-center justify-between h-16">
        <Link to="/" className="text-xl font-bold tracking-tight">
          Rad<span className="text-accent">Crew</span>
        </Link>

        <div className="hidden md:flex items-center gap-8 text-sm font-medium">
          <a href="#services" className="text-muted-foreground hover:text-foreground transition-colors">Services</a>
          <a href="#how-we-work" className="text-muted-foreground hover:text-foreground transition-colors">How we work</a>
          <a href="#team" className="text-muted-foreground hover:text-foreground transition-colors">Team</a>
          <a href="#contact" className="text-muted-foreground hover:text-foreground transition-colors">Contact</a>
        </div>

        <button
          className="md:hidden p-2 text-foreground active:scale-95 transition-transform"
          onClick={() => setOpen(!open)}
          aria-label="Toggle menu"
        >
          {open ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {open && (
        <div className="md:hidden border-t border-border bg-background section-padding py-4 flex flex-col gap-4 text-sm font-medium">
          <a href="#services" onClick={() => setOpen(false)} className="text-muted-foreground hover:text-foreground">Services</a>
          <a href="#how-we-work" onClick={() => setOpen(false)} className="text-muted-foreground hover:text-foreground">How we work</a>
          <a href="#team" onClick={() => setOpen(false)} className="text-muted-foreground hover:text-foreground">Team</a>
          <a href="#contact" onClick={() => setOpen(false)} className="text-muted-foreground hover:text-foreground">Contact</a>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
