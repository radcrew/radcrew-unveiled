import { useEffect, useRef, useState } from "react";
import { motion, useReducedMotion, useScroll, useTransform, type MotionValue, type Variants } from "framer-motion";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
  type CarouselApi,
} from "@components/ui/carousel";
import { useIsMobile } from "@/hooks/useIsMobile";
import { featuredProjects, type FeaturedProject } from "../static-data";
import { fadeIn } from "../motion";

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

type ProjectCarouselProps = {
  title: string;
  images: string[];
};

const ProjectCarousel = ({ title, images }: ProjectCarouselProps) => {
  const [api, setApi] = useState<CarouselApi>();
  const [selectedIndex, setSelectedIndex] = useState(0);

  useEffect(() => {
    if (!api) return;
    setSelectedIndex(api.selectedScrollSnap());
    const onSelect = () => setSelectedIndex(api.selectedScrollSnap());
    api.on("select", onSelect);
    return () => {
      api.off("select", onSelect);
    };
  }, [api]);

  return (
    <Carousel opts={{ loop: true }} setApi={setApi} className="absolute inset-0 h-full min-h-0 w-full">
      <CarouselContent className="-ml-0 h-full min-h-0">
        {images.map((src, idx) => (
          <CarouselItem key={`${title}-${idx}`} className="relative h-full min-h-full basis-full self-stretch pl-0">
            <img
              src={src}
              alt={`${title} — screen ${idx + 1}`}
              loading="lazy"
              decoding="async"
              className="absolute inset-0 h-full w-full object-cover opacity-90 transition-opacity duration-1000 group-hover:opacity-100"
            />
          </CarouselItem>
        ))}
      </CarouselContent>
      <CarouselPrevious
        type="button"
        className="left-3 top-1/2 z-20 -translate-y-1/2 border-primary/40 bg-background/95 text-foreground shadow-md hover:bg-background"
      />
      <CarouselNext
        type="button"
        className="right-3 top-1/2 z-20 -translate-y-1/2 border-primary/40 bg-background/95 text-foreground shadow-md hover:bg-background"
      />
      {images.length > 1 && (
        <div className="absolute bottom-4 left-1/2 z-20 flex -translate-x-1/2 items-center gap-2">
          {images.map((_, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => api?.scrollTo(idx)}
              aria-label={`Go to screen ${idx + 1} of ${images.length}`}
              aria-current={idx === selectedIndex}
              className={`h-1.5 rounded-full transition-all duration-300 ${
                idx === selectedIndex ? "w-6 bg-primary" : "w-1.5 bg-background/70 hover:bg-primary/60"
              }`}
            />
          ))}
        </div>
      )}
    </Carousel>
  );
};

const ProjectMedia = ({ project }: { project: FeaturedProject }) => {
  if (project.images && project.images.length > 0) {
    return <ProjectCarousel title={project.title} images={project.images} />;
  }
  if (project.image) {
    return (
      <img
        src={project.image}
        alt={project.title}
        loading="lazy"
        decoding="async"
        className="h-full w-full object-cover opacity-90 transition-transform duration-1000 group-hover:scale-105 group-hover:opacity-100"
      />
    );
  }
  return null;
};

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
  const opacity = useCentreRamp(progress, centre, spread, [0.45, 1, 0.45]);

  return (
    <motion.article
      style={{ rotateY, scale, opacity, width: `${CARD_VW}vw` }}
      className="group flex h-[74vh] shrink-0 flex-col overflow-hidden border border-border bg-card shadow-sm"
    >
      <div className="relative min-h-0 flex-1 overflow-hidden">
        <ProjectMedia project={project} />
        <div className="pointer-events-none absolute inset-0 z-10 bg-primary/5 mix-blend-multiply transition-colors duration-700 group-hover:bg-transparent" />
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
        className="sticky top-0 flex h-[100dvh] items-center overflow-hidden"
        // Without a perspective on an ancestor, `rotateY` is an affine squash
        // rather than a rotation in depth.
        style={{ perspective: "1600px" }}
      >
        <motion.div
          style={{ x, gap: `${GAP_VW}vw`, paddingLeft: `${SIDE_VW}vw`, paddingRight: `${SIDE_VW}vw` }}
          className="flex items-center"
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
          <div className="pointer-events-none absolute inset-0 z-10 bg-primary/5 mix-blend-multiply transition-colors duration-700 group-hover:bg-transparent" />
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

  return (
    <section id="portfolio" className="border-t border-border bg-background py-20 md:py-32">
      <motion.div
        initial="hidden"
        whileInView="visible"
        variants={fadeIn}
        viewport={{ once: true }}
        className="mx-auto mb-24 flex max-w-7xl flex-col items-baseline justify-between gap-8 border-b border-border px-6 pb-8 md:flex-row lg:px-12"
      >
        <h2 className="font-serif text-5xl text-foreground md:text-7xl">Selected Work</h2>
      </motion.div>

      {pinned ? <PinnedProjects /> : <StackedProjects />}
    </section>
  );
};
