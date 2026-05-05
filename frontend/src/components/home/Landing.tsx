import { useState } from "react";
import { useScroll, useMotionValueEvent } from "framer-motion";
import { Nav } from "./sections/Nav";
import { Hero } from "./sections/Hero";
import { Stats } from "./sections/Stats";
import { Capabilities } from "./sections/Capabilities";
import { Process } from "./sections/Process";
import { Portfolio } from "./sections/Portfolio";
import { TechStack } from "./sections/TechStack";
import { Testimonial } from "./sections/Testimonial";
import { Team } from "./sections/Team";
import { Faq } from "./sections/Faq";
import { ContactSection } from "./sections/ContactSection";
import { Footer } from "./sections/Footer";

export default function Landing() {
  const [isScrolled, setIsScrolled] = useState(false);
  const { scrollY } = useScroll();

  useMotionValueEvent(scrollY, "change", (latest) => {
    setIsScrolled(latest > 50);
  });

  const scrollTo = (id: string) => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <div className="min-h-[100dvh] bg-background font-sans text-foreground selection:bg-primary/30 selection:text-primary">
      <Nav isScrolled={isScrolled} onNavigate={scrollTo} />
      <Hero onNavigate={scrollTo} />
      <Stats />
      <Capabilities />
      <Process />
      <Portfolio />
      <TechStack />
      <Testimonial />
      <Team />
      <Faq />
      <ContactSection />
      <Footer />
    </div>
  );
}
