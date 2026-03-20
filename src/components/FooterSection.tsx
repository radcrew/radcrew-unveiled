const FooterSection = () => {
  return (
    <footer
      id="footer"
      className="flex min-h-screen min-h-dvh flex-col justify-center border-t border-border section-padding py-10 sm:py-12 md:py-14 lg:py-16"
    >
      <div className="mx-auto flex w-full max-w-6xl flex-col justify-between gap-12 md:flex-row md:items-center">
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
