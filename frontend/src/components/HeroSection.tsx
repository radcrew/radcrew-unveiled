import { ArrowDown } from "lucide-react";
import { Button } from "@components/ui/button";
import { useHeroParallax } from "@/hooks/useHeroParallax";
import heroTechBg from "@/assets/hero-tech-bg.png";

const HeroSection = () => {
  const heroRef = useHeroParallax();

  return (
    <section ref={heroRef} className="hero-root">
      <div className="hero-bg" aria-hidden>
        <img src={heroTechBg} alt="" className="hero-bg-img" />
        <div
          className="absolute inset-0 bg-gradient-to-r from-background from-0% via-background/78 via-[32%] to-background/25 md:via-background/55 md:to-background/10 lg:via-background/35 lg:to-transparent"
          aria-hidden
        />
        <div
          className="absolute inset-0 bg-gradient-to-b from-transparent from-[48%] via-background/25 to-background"
          aria-hidden
        />
      </div>

      <div className="hero-inner">
        <div className="reveal">
          <p className="kicker mb-4">Development Agency</p>
        </div>
        <h1 className="hero-title reveal reveal-delay-1">
          We build what's <span className="text-accent">next.</span>
        </h1>
        <div className="hero-blurb reveal reveal-delay-2">
          <p>
            RadCrew is a lean development agency for serious products: end-to-end web and APIs, on-chain systems on{" "}
            <span className="text-foreground/90">EVM and Solana</span>, and AI-powered features from prototypes to
            production.
          </p>
          <p>
            Our crew is three senior engineers—a lead who owns architecture and delivery, a Web3/AI specialist deep in
            smart contracts and chains, and a full-stack/AI engineer who ties interfaces, backends, and models together.
            We partner with teams who want velocity without sacrificing quality.
          </p>
        </div>
        <div className="mt-12 reveal reveal-delay-3">
          <Button
            variant="link"
            asChild
            className="h-auto gap-2 p-0 text-sm font-medium text-accent underline-offset-4 hover:text-accent hover:underline"
          >
            <a href="#team">
              Meet the crew <ArrowDown size={16} />
            </a>
          </Button>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
