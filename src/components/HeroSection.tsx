import { ArrowDown } from "lucide-react";
import heroTechBg from "@/assets/hero-tech-bg.png";

const HeroSection = () => {
  return (
    <section className="relative flex min-h-screen min-h-dvh flex-col justify-center overflow-hidden">
      {/* Light hero background: full-stack · blockchain · AI (decorative) */}
      <div className="pointer-events-none absolute inset-0 -z-10 min-h-screen min-h-dvh" aria-hidden>
        <img
          src={heroTechBg}
          alt=""
          className="h-full min-h-screen min-h-dvh w-full object-fill"
        />
        {/* Fade from solid page background so headline & copy stay readable */}
        <div className="absolute inset-0 bg-gradient-to-r from-background from-[5%] via-background/95 via-[42%] to-background/55 md:via-background/88 md:to-background/25 lg:to-transparent" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent from-60% to-background" />
      </div>

      <div className="section-padding relative z-10 mx-auto flex w-full max-w-7xl xl:max-w-[90rem] 2xl:max-w-[100rem] flex-col justify-center pt-24 pb-16">
        <div className="reveal">
          <p className="text-accent font-semibold text-sm uppercase tracking-widest mb-4">Development Agency</p>
        </div>
        <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-bold leading-[0.95] reveal reveal-delay-1 max-w-5xl xl:max-w-6xl 2xl:max-w-7xl">
          We build what's <span className="text-accent">next.</span>
        </h1>
        <div className="mt-8 space-y-4 text-lg md:text-xl text-muted-foreground max-w-3xl xl:max-w-4xl 2xl:max-w-5xl reveal reveal-delay-2 leading-relaxed">
          <p>
            RadCrew is a lean development agency for serious products: end-to-end web and APIs, on-chain
            systems on <span className="text-foreground/90">EVM and Solana</span>, and AI-powered features
            from prototypes to production.
          </p>
          <p>
            Our crew is three senior engineers—a lead who owns architecture and delivery, a Web3/AI
            specialist deep in smart contracts and chains, and a full-stack/AI engineer who ties
            interfaces, backends, and models together. We partner with teams who want velocity without
            sacrificing quality.
          </p>
        </div>
        <div className="mt-12 reveal reveal-delay-3">
          <a
            href="#team"
            className="inline-flex items-center gap-2 text-sm font-medium text-accent hover:underline underline-offset-4 transition-all"
          >
            Meet the crew <ArrowDown size={16} />
          </a>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
