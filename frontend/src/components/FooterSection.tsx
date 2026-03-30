const FooterSection = () => {
  return (
    <footer id="footer" className="footer-shell">
      <div className="footer-row">
        <div>
          <p className="mb-2 text-xl font-bold">
            Rad<span className="text-accent">Crew</span>
          </p>
          <p className="max-w-xs text-sm leading-relaxed text-muted-foreground">
            A tight-knit crew of engineers building across the full stack, blockchain, and AI.
          </p>
        </div>
        <div className="space-y-2 text-sm text-muted-foreground">
          <p>code@radcrew.org</p>
          <p>© {new Date().getFullYear()} RadCrew. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default FooterSection;
