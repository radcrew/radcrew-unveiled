import { motion } from "framer-motion";
import { Button } from "@components/ui/button";
import HeroCanvas from "@components/HeroCanvas";
import { fadeIn, staggerContainer } from "../motion";

type HeroProps = {
  onNavigate: (sectionId: string) => void;
};

export function Hero({ onNavigate }: HeroProps) {
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
            className="mb-8 font-serif text-6xl leading-[0.9] tracking-tight text-foreground md:text-8xl lg:text-[11rem]"
          >
            We build <br />
            <span className="font-medium italic text-primary">what&apos;s next.</span>
          </motion.h1>
          <motion.p
            variants={fadeIn}
            className="mx-auto mb-12 max-w-2xl text-xl font-light leading-relaxed text-muted-foreground md:mx-0 md:text-2xl"
          >
            An elite engineering studio building AI/ML products and Web3 solutions on EVM and Solana. For discerning
            clients who demand precision.
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
    </section>
  );
}
