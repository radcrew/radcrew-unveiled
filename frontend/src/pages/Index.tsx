import Navbar from "@/components/Navbar";
import HeroSection from "@/components/HeroSection";
import ServicesSection from "@/components/ServicesSection";
import HowWeWorkSection from "@/components/HowWeWorkSection";
import PortfolioSection from "@/components/PortfolioSection";
import TeamSection from "@/components/TeamSection";
import ContactSection from "@/components/ContactSection";
import FooterSection from "@/components/FooterSection";

const Index = () => {
  return (
    <div className="min-h-screen">
      <Navbar />
      <HeroSection />
      <ServicesSection />
      <HowWeWorkSection />
      <PortfolioSection />
      <TeamSection />
      {/* One viewport for contact CTA + footer together */}
      <div className="contact-footer-stack">
        <ContactSection />
        <FooterSection />
      </div>
    </div>
  );
};

export default Index;
