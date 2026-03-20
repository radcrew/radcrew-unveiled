import Navbar from "@/components/Navbar";
import HeroSection from "@/components/HeroSection";
import TeamSection from "@/components/TeamSection";
import WorkspaceCarousel from "@/components/WorkspaceCarousel";
import FooterSection from "@/components/FooterSection";

const Index = () => {
  return (
    <div className="min-h-screen">
      <Navbar />
      <HeroSection />
      <TeamSection />
      <WorkspaceCarousel />
      <FooterSection />
    </div>
  );
};

export default Index;
