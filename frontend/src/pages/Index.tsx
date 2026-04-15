import { useEffect } from "react";
import HeroSection from "@/components/HeroSection";
import ServicesSection from "@/components/ServicesSection";
import HowWeWorkSection from "@/components/HowWeWorkSection";
import PortfolioSection from "@/components/PortfolioSection";
import TeamSection from "@/components/TeamSection";
import ContactSection from "@/components/ContactSection";
import FooterSection from "@/components/FooterSection";

const HOME_SCROLL_CLASS = "home-scroll-sections";

const Index = () => {
  useEffect(() => {
    document.documentElement.classList.add(HOME_SCROLL_CLASS);
    return () => document.documentElement.classList.remove(HOME_SCROLL_CLASS);
  }, []);

  return (
    <div className="min-h-screen">
      <HeroSection />
      <ServicesSection />
      <HowWeWorkSection />
      <PortfolioSection />
      <TeamSection />
      <div id="contact" className="contact-footer-stack" data-scroll-block="end">
        <ContactSection />
        <FooterSection />
      </div>
    </div>
  );
};

export default Index;
