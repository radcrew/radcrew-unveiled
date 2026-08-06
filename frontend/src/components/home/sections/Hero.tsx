import { useState } from "react";
import { motion, useMotionValueEvent, useScroll } from "framer-motion";
import { ChevronDown } from "lucide-react";
import { Button } from "@components/ui/button";
import HeroCanvas from "@components/HeroCanvas";
import { fadeIn, staggerContainer } from "../motion";

type HeroProps = {
  onNavigate: (sectionId: string) => void;
};

export const Hero = ({ onNavigate }: HeroProps) => {
  const [isScrolled, setIsScrolled] = useState(false);
  const { scrollY } = useScroll();

  useMotionValueEvent(scrollY, "change", (latest) => {
    setIsScrolled(latest > 50);
  });

  return (
    <section className="relative flex min-h-[100dvh] items-center justify-center overflow-hidden px-6 pt-24">
      <div className="absolute inset-0 z-0">
        <HeroCanvas />
        <div className="absolute inset-0 bg-gradient-to-b from-background/30 via-transparent to-background" />
      </div>

      <div className="relative z-10 mx-auto w-full max-w-7xl text-center md:text-left">
        <motion.div initial="hidden" whileInView="visible" variants={staggerContainer} viewport={{ once: true }}>
          <motion.h1
            variants={fadeIn}
            className="mb-8 font-serif text-[clamp(3.75rem,13vw+0.75rem,11rem)] leading-[0.9] tracking-tight text-foreground"
          >
            We build <br />
            <span className="font-medium italic text-primary">what&apos;s next.</span>
          </motion.h1>
          <motion.p
            variants={fadeIn}
            className="mx-auto mb-12 max-w-2xl text-xl font-light leading-relaxed text-muted-foreground md:mx-0 md:text-2xl"
          >
            A guild of independent developers building AI/ML products and Web3 solutions on EVM and Solana. Hire one of
            us, not a company.
          </motion.p>
          <motion.div variants={fadeIn} className="flex flex-col justify-center gap-6 sm:flex-row md:justify-start">
            <Button
              type="button"
              onClick={() => onNavigate("portfolio")}
              className="h-auto rounded-none bg-primary px-10 py-7 text-sm font-light uppercase tracking-widest text-primary-foreground hover:bg-primary/90"
              data-testid="hero-cta-work"
            >
              View Selected Work
            </Button>
            <Button
              type="button"
              onClick={() => onNavigate("contact")}
              variant="outline"
              className="h-auto rounded-none border-border px-10 py-7 text-sm font-light uppercase tracking-widest hover:bg-muted hover:!text-primary"
              data-testid="hero-cta-contact"
            >
              Start a Project
            </Button>
          </motion.div>
        </motion.div>
      </div>

      <motion.button
        type="button"
        onClick={() => window.scrollBy({ top: window.innerHeight, behavior: "smooth" })}
        initial={{ opacity: 0 }}
        animate={{ opacity: isScrolled ? 0 : 1 }}
        transition={{ duration: isScrolled ? 0.3 : 0.8, delay: isScrolled ? 0 : 1.2 }}
        className={`absolute bottom-8 left-1/2 z-10 flex -translate-x-1/2 flex-col items-center gap-2 text-muted-foreground transition-colors hover:text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background ${isScrolled ? "pointer-events-none" : ""}`}
        aria-label="Scroll down"
        aria-hidden={isScrolled}
        tabIndex={isScrolled ? -1 : 0}
      >
        <span className="text-xs font-light uppercase tracking-widest">Scroll</span>
        <motion.span animate={{ y: [0, 6, 0] }} transition={{ duration: 1.6, repeat: Infinity, ease: "easeInOut" }}>
          <ChevronDown className="h-5 w-5" />
        </motion.span>
      </motion.button>
    </section>
  );
};
