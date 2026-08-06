import { motion } from "framer-motion";
import { Button } from "@components/ui/button";
import { Magnetic } from "@components/motion/Magnetic";
import { SplitText } from "@components/motion/SplitText";
import { AnimatedCounter } from "../AnimatedCounter";
import { Grain } from "../Grain";
import { fadeIn, staggerContainer } from "../motion";

type HeroProps = {
  onNavigate: (sectionId: string) => void;
};

/**
 * Track record, shown as a band across the foot of the hero. These numbers used
 * to sit in a standalone `Stats` section a screen further down; they carry more
 * weight next to the claim they support.
 */
const trackRecord = [
  { end: 40, suffix: "+", decimals: 0, label: "Projects shipped" },
  { end: 12, suffix: "+", decimals: 0, label: "Clients partnered" },
  { end: 5, suffix: "", decimals: 0, label: "Years building" },
  { end: 99.9, suffix: "%", decimals: 1, label: "Uptime SLA" },
] as const;

export const Hero = ({ onNavigate }: HeroProps) => {
  return (
    // Inverted to the dark ground the Spotlight and Footer already use. On cream,
    // the gold accent measures 2.3:1 against the background and the filled CTA
    // 2.4:1, both below AA. The same gold on this ground is 7.8:1 and the cream
    // type is 18:1, so the section gets its contrast from the palette rather
    // than from adding weight to the type.
    // `antialiased` matters on the dark ground: subpixel rendering fringes the
    // serif's thin strokes with colour against it.
    <section className="relative flex min-h-[100dvh] flex-col justify-end overflow-hidden bg-foreground px-6 text-background antialiased lg:px-12">
      <div aria-hidden="true" className="absolute inset-0 z-0">
        {/* Warm bloom behind the headline, so the type sits in light rather than
            on a flat rectangle. */}
        <div
          className="absolute inset-0"
          style={{
            background:
              "radial-gradient(120% 90% at 12% 28%, hsl(38 60% 55% / 0.16) 0%, hsl(38 60% 55% / 0.05) 34%, transparent 68%)",
          }}
        />
        <Grain />
        {/* Settles the foot of the section into the band and the page below it. */}
        <div className="absolute inset-x-0 bottom-0 h-1/3 bg-gradient-to-t from-foreground to-transparent" />
      </div>

      <motion.div
        initial="hidden"
        animate="visible"
        variants={staggerContainer}
        className="relative z-10 mx-auto flex w-full max-w-7xl flex-1 flex-col justify-end pb-12 pt-28"
      >
        <motion.p variants={fadeIn} className="mb-8 flex items-center gap-4 md:mb-10">
          <span aria-hidden="true" className="h-px w-12 shrink-0 bg-primary-on-dark" />
          <span className="text-xs font-light uppercase tracking-[0.28em] text-primary-on-dark sm:text-sm">
            Hire one of us, not a company
          </span>
        </motion.p>

        {/* Full width rather than a column, so the display face can run to the
            measure of the page. This is where the section spends its boldness. */}
        <h1 className="mb-10 font-serif text-[clamp(3rem,11vw,10rem)] leading-[0.86] tracking-[-0.02em]">
          <SplitText text="We build" />
          <br />
          <SplitText text="what's next." delay={0.12} className="font-medium italic text-primary-on-dark" />
        </h1>

        <div className="flex flex-col gap-10 lg:flex-row lg:items-end lg:justify-between">
          <motion.p
            variants={fadeIn}
            className="max-w-xl text-lg font-light leading-relaxed text-background/70 md:text-xl"
          >
            A guild of independent senior engineers building AI/ML products and Web3 solutions on EVM and Solana, from
            prototype to production.
          </motion.p>

          <motion.div variants={fadeIn} className="flex shrink-0 flex-col gap-4 sm:flex-row">
            <Magnetic>
              {/* Cream on dark is the highest-contrast pairing available here, and
                  it reads as the primary action without relying on the gold. */}
              <Button
                type="button"
                onClick={() => onNavigate("portfolio")}
                className="h-auto w-full rounded-none bg-background px-10 py-6 text-sm font-light uppercase tracking-widest text-foreground hover:bg-background/90 md:py-7"
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
                className="h-auto w-full rounded-none border-background/30 bg-transparent px-10 py-6 text-sm font-light uppercase tracking-widest text-background hover:bg-background hover:!text-foreground md:py-7"
                data-testid="hero-cta-contact"
              >
                Start a Project
              </Button>
            </Magnetic>
          </motion.div>
        </div>
      </motion.div>

      {/* The band anchors the section: a rule the full width of the page, with the
          proof sitting on it. `flex-col-reverse` shows each figure above its label
          while the DOM keeps the label first, so each pair reads as "label: value". */}
      <motion.dl
        initial="hidden"
        animate="visible"
        variants={staggerContainer}
        className="relative z-10 mx-auto flex w-full max-w-7xl flex-wrap gap-x-7 gap-y-3 border-t border-background/15 pb-10 pt-6 md:grid md:grid-cols-4 md:gap-8"
      >
        {trackRecord.map(({ end, suffix, decimals, label }) => (
          <motion.div
            key={label}
            variants={fadeIn}
            className="flex flex-row-reverse items-baseline gap-2 md:flex-col-reverse md:items-start md:gap-0"
          >
            <dt className="text-[0.625rem] font-light uppercase tracking-[0.2em] text-background/55 md:mt-2 md:text-[0.6875rem]">
              {label}
            </dt>
            <dd>
              <AnimatedCounter
                end={end}
                suffix={suffix}
                decimals={decimals}
                className="font-serif text-2xl text-background md:text-5xl"
                suffixClassName="text-primary-on-dark"
              />
            </dd>
          </motion.div>
        ))}
      </motion.dl>

    </section>
  );
};
