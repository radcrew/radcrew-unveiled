const FooterSection = () => {
  return (
    <footer id="footer" className="py-16 md:py-24 section-padding border-t border-border">
      <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between gap-12">
        <div>
          <p className="text-xl font-bold mb-2">
            Rad<span className="text-accent">Crew</span>
          </p>
          <p className="text-muted-foreground text-sm max-w-xs leading-relaxed">
            A tight-knit crew of engineers building across the full stack, blockchain, and AI.
          </p>
        </div>
        <div className="text-sm text-muted-foreground space-y-2">
          <p>hello@radcrew.dev</p>
          <p>© {new Date().getFullYear()} RadCrew. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default FooterSection;
