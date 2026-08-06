import { useEffect, useState } from "react";
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

const NAV_SECTION_IDS = ["services", "portfolio", "process", "journal"];

const Landing = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [activeSection, setActiveSection] = useState("");
  const { scrollY } = useScroll();

  useMotionValueEvent(scrollY, "change", (latest) => {
    setIsScrolled(latest > 50);
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

  const scrollTo = (id: string) => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <div className="min-h-[100dvh] bg-background font-sans text-foreground selection:bg-primary/30 selection:text-primary">
      <Nav isScrolled={isScrolled} activeSection={activeSection} onNavigate={scrollTo} />
      <Hero onNavigate={scrollTo} />
      <Clients />
      <ProofBand />
      <Capabilities onNavigate={scrollTo} />
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

export default Landing;
