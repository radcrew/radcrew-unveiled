import { ArrowDown } from "lucide-react";

const HeroSection = () => {
  return (
    <section className="min-h-[90vh] flex flex-col justify-center section-padding pt-24 pb-16 max-w-6xl mx-auto">
      <div className="reveal">
        <p className="text-accent font-semibold text-sm uppercase tracking-widest mb-4">Development Agency</p>
      </div>
      <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-bold leading-[0.95] reveal reveal-delay-1 max-w-4xl">
        We build what's <span className="text-accent">next.</span>
      </h1>
      <div className="mt-8 space-y-4 text-lg md:text-xl text-muted-foreground max-w-2xl reveal reveal-delay-2 leading-relaxed">
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
    </section>
  );
};

export default HeroSection;
