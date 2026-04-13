const FooterSection = () => {
  return (
    <footer id="footer" className="footer-shell">
      <div className="footer-row">
        <div>
          <p className="text-xl font-bold">
            Rad<span className="text-accent">Crew</span>
          </p>
        </div>
        <div className="text-sm text-muted-foreground">
          <p>© {new Date().getFullYear()} RadCrew. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default FooterSection;
