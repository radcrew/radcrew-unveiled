import { useState } from "react";
import { motion, useMotionValueEvent, useScroll } from "framer-motion";
import { ChevronDown } from "lucide-react";
import { Button } from "@components/ui/button";
import HeroCanvas from "@components/HeroCanvas";
import { Magnetic } from "@components/motion/Magnetic";
import { SplitText } from "@components/motion/SplitText";
import { AnimatedCounter } from "../AnimatedCounter";
import { fadeIn, staggerContainer } from "../motion";

type HeroProps = {
  onNavigate: (sectionId: string) => void;
};

/**
 * Track record, shown as the hero's right-hand rail. These numbers used to sit
 * in a standalone `Stats` section one screen further down; they carry more
 * weight next to the claim they support than they did on their own.
 */
const trackRecord = [
  { end: 40, suffix: "+", decimals: 0, label: "Projects shipped" },
  { end: 12, suffix: "+", decimals: 0, label: "Clients partnered" },
  { end: 5, suffix: "", decimals: 0, label: "Years building" },
  { end: 99.9, suffix: "%", decimals: 1, label: "Uptime SLA" },
] as const;

export const Hero = ({ onNavigate }: HeroProps) => {
  const [isScrolled, setIsScrolled] = useState(false);
  const { scrollY } = useScroll();

  useMotionValueEvent(scrollY, "change", (latest) => {
    setIsScrolled(latest > 50);
  });

  return (
    // Extra bottom padding on mobile keeps the last row of figures clear of the
    // fixed chat launcher in the bottom-right corner.
    <section className="relative flex min-h-[100dvh] items-center overflow-hidden px-6 pb-28 pt-28 md:pb-28 md:pt-32 lg:px-12">
      <div className="absolute inset-0 z-0">
        <HeroCanvas />
        {/* The canvas reads as noise behind text at full strength. Fading it from
            the left gives the headline a clean field while keeping the texture
            visible on the open right-hand side. */}
        <div className="absolute inset-0 bg-gradient-to-r from-background via-background/80 to-transparent" />
        <div className="absolute inset-0 bg-gradient-to-b from-background/40 via-transparent to-background" />
      </div>

      <div className="relative z-10 mx-auto grid w-full max-w-7xl items-center gap-10 md:grid-cols-12 md:gap-12">
        <motion.div
          initial="hidden"
          animate="visible"
          variants={staggerContainer}
          className="md:col-span-7"
        >
          <motion.p variants={fadeIn} className="mb-8 flex items-center gap-4">
            <span aria-hidden="true" className="h-px w-10 shrink-0 bg-primary" />
            <span className="text-sm font-light uppercase tracking-widest text-primary">
              Hire one of us, not a company
            </span>
          </motion.p>

          <h1 className="mb-8 font-serif text-[clamp(3.5rem,11vw+0.5rem,9rem)] leading-[0.88] tracking-tight text-foreground">
            <SplitText text="We build" />
            <br />
            <SplitText text="what's next." delay={0.12} className="font-medium italic text-primary" />
          </h1>

          <motion.p
            variants={fadeIn}
            className="mb-10 max-w-xl text-lg font-light leading-relaxed text-muted-foreground md:mb-12 md:text-xl"
          >
            A guild of independent senior engineers building AI/ML products and Web3 solutions on EVM and Solana, from
            prototype to production.
          </motion.p>

          <motion.div variants={fadeIn} className="flex flex-col gap-4 sm:flex-row">
            <Magnetic>
              <Button
                type="button"
                onClick={() => onNavigate("portfolio")}
                className="h-auto w-full rounded-none bg-primary px-10 py-6 text-sm font-light uppercase tracking-widest md:py-7 text-primary-foreground hover:bg-primary/90"
                data-testid="hero-cta-work"
              >
                View Selected Work
              </Button>
            </Magnetic>
            <Magnetic>
              <Button
                type="button"
                onClick={() => onNavigate("contact")}
                variant="outline"
                className="h-auto w-full rounded-none border-border px-10 py-6 text-sm font-light uppercase tracking-widest md:py-7 hover:bg-muted hover:!text-primary"
                data-testid="hero-cta-contact"
              >
                Start a Project
              </Button>
            </Magnetic>
          </motion.div>
        </motion.div>

        {/* One list, two layouts. On mobile the four figures sit inline as a
            compact wrapped row; a stacked rail there costs ~170px and pushes the
            last row under the fixed chat launcher. From `md` it becomes the
            vertical rail that fills the space beside the headline.
            The `*-reverse` classes show each figure ahead of its label while the
            DOM keeps the label first, so each pair still reads as "label: value". */}
        <motion.dl
          initial="hidden"
          animate="visible"
          variants={staggerContainer}
          className="flex flex-wrap gap-x-6 gap-y-3 md:col-span-4 md:col-start-9 md:grid md:grid-cols-1 md:gap-0 md:border-l md:border-primary/20 md:pl-10"
        >
          {trackRecord.map(({ end, suffix, decimals, label }) => (
            <motion.div
              key={label}
              variants={fadeIn}
              className="flex flex-row-reverse items-baseline gap-2 md:flex-col-reverse md:items-start md:gap-0 md:border-b md:border-primary/10 md:py-5 md:first:pt-0 md:last:border-b-0 md:last:pb-0"
            >
              <dt className="text-[0.625rem] font-light uppercase tracking-widest text-muted-foreground md:mt-2 md:text-xs">
                {label}
              </dt>
              <dd>
                <AnimatedCounter
                  end={end}
                  suffix={suffix}
                  decimals={decimals}
                  className="font-serif text-2xl text-foreground md:text-5xl"
                />
              </dd>
            </motion.div>
          ))}
        </motion.dl>
      </div>

      <motion.button
        type="button"
        onClick={() => window.scrollBy({ top: window.innerHeight, behavior: "smooth" })}
        initial={{ opacity: 0 }}
        animate={{ opacity: isScrolled ? 0 : 1 }}
        transition={{ duration: isScrolled ? 0.3 : 0.8, delay: isScrolled ? 0 : 1.2 }}
        className={`absolute bottom-8 left-1/2 z-10 hidden -translate-x-1/2 flex-col items-center gap-2 text-muted-foreground md:flex transition-colors hover:text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background ${isScrolled ? "pointer-events-none" : ""}`}
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
