import { useRef } from "react";
import { motion, useReducedMotion, useScroll, useTransform, type MotionValue, type Variants } from "framer-motion";
import { useIsMobile } from "@/hooks/use-is-mobile";
import { ProjectMedia } from "../ProjectMedia";
import { featuredProjects, type FeaturedProject } from "../static-data";
import { maskWipe } from "../motion";

const tagContainerVariants: Variants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.05 } },
};

const tagVariants: Variants = {
  hidden: { opacity: 0, y: 8 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.3 } },
};

/**
 * Track geometry, in viewport widths. Sizing the cards in `vw` rather than
 * measuring them is what lets the horizontal travel be a constant the transform
 * can be written against directly, with no ResizeObserver and no layout read.
 * `SIDE_VW` is the padding that centres the first and last card, so card `i`
 * sits dead centre at scroll progress `i / (count - 1)`.
 */
const CARD_VW = 68;
const GAP_VW = 4;
const SIDE_VW = (100 - CARD_VW) / 2;

const tagClassName =
  "border border-primary/30 px-3 py-1.5 text-[0.6875rem] font-light uppercase tracking-wider text-primary";

/**
 * A ramp that peaks as the card passes the middle of the viewport and falls away
 * on both sides.
 *
 * The stops outside [0, 1] are dropped rather than kept and clamped, because
 * framer-motion passes an input range straight through to the Web Animations API
 * as keyframe offsets, and those must be non-decreasing and within [0, 1]. The
 * first and last card sit at the very ends of the scroll, so a range written
 * symmetrically around either one leaves that interval and throws. Dropping the
 * unreachable stop is lossless: `useTransform` already holds the end values
 * beyond the range it is given.
 */
const useCentreRamp = (
  progress: MotionValue<number>,
  centre: number,
  spread: number,
  values: [number, number, number],
) => {
  const reachable = [centre - spread, centre, centre + spread]
    .map((stop, i) => ({ stop, value: values[i] }))
    .filter(({ stop }) => stop >= 0 && stop <= 1);

  return useTransform(
    progress,
    reachable.map(({ stop }) => stop),
    reachable.map(({ value }) => value),
  );
};

type PinnedCardProps = {
  project: FeaturedProject;
  index: number;
  count: number;
  progress: MotionValue<number>;
};

const PinnedCard = ({ project, index, count, progress }: PinnedCardProps) => {
  // The progress at which this card is centred. With the track padded by
  // `SIDE_VW`, the first card is centred at 0 and the last at 1, so one card's
  // worth of travel is one step of `spread`.
  const centre = index / (count - 1);
  const spread = 1 / (count - 1);

  // Positive `rotateY` sends a card's right edge away from the viewer, which is
  // what a card sitting to the right of centre should do. Hence the descending
  // output range: the card turns to face the middle of the viewport from either
  // side and is square to it only as it passes through.
  const rotateY = useCentreRamp(progress, centre, spread, [14, 0, -14]);
  const scale = useCentreRamp(progress, centre, spread, [0.9, 1, 0.9]);

  // Depth is carried by the turn and the scale alone. There was an opacity ramp
  // here too, fading off-centre cards to 0.45, which compounded with the image's
  // own dimming to hold the screenshots near half strength and made them read as
  // disabled rather than as further away.
  return (
    <motion.article
      style={{ rotateY, scale, width: `${CARD_VW}vw` }}
      // `h-full` rather than a fixed `74vh`: the card now shares the pinned
      // screen with the heading, so its height is whatever the track is given
      // once the heading and padding are taken out.
      className="group flex h-full shrink-0 flex-col overflow-hidden border border-border bg-card shadow-sm"
    >
      <div className="relative min-h-0 flex-1 overflow-hidden">
        <ProjectMedia project={project} />
      </div>

      <div className="shrink-0 border-t border-border p-6 md:p-8">
        <h3 className="mb-4 font-serif text-3xl leading-tight text-foreground md:text-4xl">{project.title}</h3>
        <div className="mb-4 flex flex-wrap gap-2">
          {project.tags.map((tag) => (
            <span key={tag} className={tagClassName}>
              {tag}
            </span>
          ))}
        </div>
        <p className="max-w-3xl text-base font-light leading-relaxed text-muted-foreground">{project.description}</p>
      </div>
    </motion.article>
  );
};

/**
 * Shared so the pinned and stacked layouts cannot drift apart. The pinned one
 * renders it *inside* the sticky child rather than above it, which is what lets
 * a single screen hold the heading and a whole card at once.
 */
const SectionHeading = ({ className = "" }: { className?: string }) => (
  <motion.div
    initial="hidden"
    whileInView="visible"
    variants={maskWipe}
    viewport={{ once: true }}
    className={`mx-auto flex w-full max-w-7xl flex-col items-baseline justify-between gap-8 border-b border-border px-6 pb-8 md:flex-row lg:px-12 ${className}`}
  >
    <h2 className="font-serif text-5xl text-foreground md:text-7xl">Selected Work</h2>
  </motion.div>
);

/**
 * The pinned variant. The outer element is tall; the inner one sticks to the top
 * of the viewport for the whole of that height, and the track inside it is
 * translated horizontally by how far through the tall element the page has
 * scrolled. Vertical scrolling therefore reads as horizontal travel.
 */
const PinnedProjects = () => {
  const pinRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ target: pinRef, offset: ["start start", "end end"] });

  const travelVw = (featuredProjects.length - 1) * (CARD_VW + GAP_VW);
  const x = useTransform(scrollYProgress, [0, 1], ["0vw", `-${travelVw}vw`]);

  return (
    // `relative` is not cosmetic: `useScroll` measures its target's offset and
    // warns that the result is unreliable when that target is statically
    // positioned.
    <div ref={pinRef} className="relative" style={{ height: `${featuredProjects.length * 100}vh` }}>
      <div
        // Padded by the header height rather than centred on the raw viewport:
        // the nav is fixed and translucent, so content centred on the full
        // height slides under it and shows through.
        className="sticky top-0 flex h-[100dvh] flex-col overflow-hidden pb-10 pt-[var(--site-header-height)]"
        // Without a perspective on an ancestor, `rotateY` is an affine squash
        // rather than a rotation in depth.
        style={{ perspective: "1600px" }}
      >
        <SectionHeading className="shrink-0" />

        {/* `min-h-0` so this can actually shrink: a flex child defaults to
            min-height auto and would otherwise refuse to go below its content,
            pushing the track past the bottom of the pinned viewport. */}
        <div className="flex min-h-0 flex-1 items-center pt-10">
          <motion.div
            style={{ x, gap: `${GAP_VW}vw`, paddingLeft: `${SIDE_VW}vw`, paddingRight: `${SIDE_VW}vw` }}
            className="flex h-full items-center"
          >
            {featuredProjects.map((project, index) => (
              <PinnedCard
                key={project.title}
                project={project}
                index={index}
                count={featuredProjects.length}
                progress={scrollYProgress}
              />
            ))}
          </motion.div>
        </div>
      </div>
    </div>
  );
};

/**
 * The fallback, and the layout this section had before the pinned one existed.
 * Used on phones, where a scroll-driven horizontal track fights the browser's
 * own gesture handling, and under reduced motion, where turning vertical scroll
 * into horizontal travel is exactly the effect the preference asks us to drop.
 */
const StackedProjects = () => (
  <div className="mx-auto max-w-7xl space-y-32 px-6 lg:px-12">
    {featuredProjects.map((project) => (
      <motion.div
        key={project.title}
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 1 }}
        className="group"
      >
        <div className="mb-10">
          <h3 className="mb-5 font-serif text-4xl leading-tight text-foreground md:text-5xl">{project.title}</h3>

          <motion.div
            initial="hidden"
            whileInView="visible"
            variants={tagContainerVariants}
            viewport={{ once: true }}
            className="mb-6 flex flex-wrap gap-2"
          >
            {project.tags.map((tag) => (
              <motion.span key={tag} variants={tagVariants} className={tagClassName}>
                {tag}
              </motion.span>
            ))}
          </motion.div>

          <p className="max-w-3xl text-lg font-light leading-relaxed text-muted-foreground md:text-xl">
            {project.description}
          </p>
        </div>

        <motion.div
          initial={{ clipPath: "inset(0 100% 0 0)" }}
          whileInView={{ clipPath: "inset(0 0% 0 0)" }}
          viewport={{ once: true }}
          transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
          className="relative aspect-[2/1] overflow-hidden border border-border bg-card shadow-sm"
        >
          <ProjectMedia project={project} />
          </motion.div>
      </motion.div>
    ))}
  </div>
);

export const Portfolio = () => {
  const isMobile = useIsMobile();
  const reduced = useReducedMotion();
  // The pinned layout maps each card onto a share of the scroll, which needs at
  // least two of them to divide.
  const pinned = !isMobile && !reduced && featuredProjects.length > 1;

  if (pinned) {
    return (
      <section
        id="portfolio"
        className="border-t border-border bg-background"
        // Negative, to cancel `scroll-padding-top` for this section alone.
        // Everywhere else that padding is what stops a section landing under the
        // nav. Here it stopped the landing 6.5rem short of the point where the
        // sticky child pins, and until it pins the first card sits half below
        // the fold. The sticky child carries the same measurement as its own top
        // padding, so the nav is still cleared once the track is engaged.
        style={{ scrollMarginTop: "calc(-1 * var(--site-header-height))" }}
      >
        <PinnedProjects />
      </section>
    );
  }

  return (
    <section id="portfolio" className="border-t border-border bg-background py-20 md:py-32">
      <SectionHeading className="mb-10" />
      <StackedProjects />
    </section>
  );
};
