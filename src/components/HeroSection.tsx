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
      <p className="mt-8 text-lg md:text-xl text-muted-foreground max-w-xl reveal reveal-delay-2 leading-relaxed">
        Three engineers. Full-stack, Web3, and AI. We ship fast, build smart, and don't cut corners.
      </p>
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
