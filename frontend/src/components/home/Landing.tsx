import { useEffect, useRef, useState } from "react";
import { useScroll, useMotionValueEvent } from "framer-motion";
import { Nav } from "./sections/Nav";
import { Hero } from "./sections/Hero";
import { Clients } from "./sections/Clients";
import { ProofBand } from "./sections/ProofBand";
import { Capabilities } from "./sections/Capabilities";
import { Spotlight } from "./sections/Spotlight";
import { Process } from "./sections/Process";
import { Portfolio } from "./sections/Portfolio";
import { TechStack } from "./sections/TechStack";
import { Testimonial } from "./sections/Testimonial";
import { Journal } from "./sections/Journal";
import { Faq } from "./sections/Faq";
import { ContactSection } from "./sections/ContactSection";
import { Footer } from "./sections/Footer";
import { scrollSectionIntoView } from "@/lib/scroll-to-section";

const NAV_SECTION_IDS = ["services", "portfolio", "process", "journal"];

export const Landing = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isNavHidden, setIsNavHidden] = useState(false);
  const [activeSection, setActiveSection] = useState("");
  const { scrollY } = useScroll();
  const lastScrollY = useRef(0);

  useMotionValueEvent(scrollY, "change", (latest) => {
    setIsScrolled(latest > 50);

    const previous = lastScrollY.current;
    lastScrollY.current = latest;

    // Reading down hides the bar, any move back up brings it straight back, and
    // the top of the page always shows it so the page never opens hidden. The
    // 4px deadband is what stops trackpad jitter and momentum overscroll from
    // flickering it on and off.
    if (latest < 140) setIsNavHidden(false);
    else if (latest - previous > 4) setIsNavHidden(true);
    else if (previous - latest > 4) setIsNavHidden(false);
  });

  useEffect(() => {
    const elements = NAV_SECTION_IDS.map((id) => document.getElementById(id)).filter(
      (el): el is HTMLElement => el !== null,
    );
    if (elements.length === 0) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) setActiveSection(entry.target.id);
        });
      },
      { rootMargin: "-50% 0px -50% 0px", threshold: 0 },
    );
    elements.forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, []);

  return (
    <div className="min-h-[100dvh] bg-background font-sans text-foreground selection:bg-primary/30 selection:text-primary">
      <Nav isScrolled={isScrolled} isHidden={isNavHidden} activeSection={activeSection} onNavigate={scrollSectionIntoView} />
      <Hero onNavigate={scrollSectionIntoView} />
      <Clients />
      <ProofBand />
      <Capabilities onNavigate={scrollSectionIntoView} />
      <Spotlight />
      <Process />
      <Portfolio />
      <TechStack />
      <Testimonial />
      <Journal />
      <Faq />
      <ContactSection />
      <Footer />
    </div>
  );
};
