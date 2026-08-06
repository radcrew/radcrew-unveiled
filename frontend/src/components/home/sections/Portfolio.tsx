import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { motion, type Variants } from "framer-motion";
import { ArrowRight } from "lucide-react";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
  type CarouselApi,
} from "@components/ui/carousel";
import { featuredProjects } from "../static-data";
import { fadeIn } from "../motion";

const tagContainerVariants: Variants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.05 } },
};

const tagVariants: Variants = {
  hidden: { opacity: 0, y: 8 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.3 } },
};

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

export const Portfolio = () => {
  return (
    <section id="portfolio" className="border-t border-border bg-background px-6 py-20 md:py-32 lg:px-12">
      <div className="mx-auto max-w-7xl">
        <motion.div
          initial="hidden"
          whileInView="visible"
          variants={fadeIn}
          viewport={{ once: true }}
          className="mb-24 flex flex-col items-baseline justify-between gap-8 border-b border-border pb-8 md:flex-row"
        >
          <h2 className="font-serif text-5xl text-foreground md:text-7xl">Selected Work</h2>
        </motion.div>

        <div className="space-y-32">
          {featuredProjects.map((project, i) => (
            <motion.div
              key={project.title}
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 1 }}
              className="group grid items-center gap-12 md:grid-cols-12"
            >
              <div className={`md:col-span-7 ${i % 2 !== 0 ? "md:order-last" : ""}`}>
                <motion.div
                  initial={{ clipPath: "inset(0 100% 0 0)" }}
                  whileInView={{ clipPath: "inset(0 0% 0 0)" }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
                  className="relative aspect-[2/1] overflow-hidden border border-border bg-background shadow-sm"
                >
                  {project.images && project.images.length > 0 ? (
                    <ProjectCarousel title={project.title} images={project.images} />
                  ) : project.image ? (
                    <img
                      src={project.image}
                      alt={project.title}
                      loading="lazy"
                      decoding="async"
                      className="h-full w-full object-cover opacity-90 transition-transform duration-1000 group-hover:scale-105 group-hover:opacity-100"
                    />
                  ) : null}
                  <div className="pointer-events-none absolute inset-0 z-10 mix-blend-multiply bg-primary/5 transition-colors duration-700 group-hover:bg-transparent" />
                </motion.div>
              </div>
              <div className={`flex flex-col justify-center md:col-span-5 ${i % 2 !== 0 ? "md:pr-12" : "md:pl-12"}`}>
                <motion.div
                  initial="hidden"
                  whileInView="visible"
                  variants={tagContainerVariants}
                  viewport={{ once: true }}
                  className="mb-8 flex flex-wrap gap-3"
                >
                  {project.tags.map((tag) => (
                    <motion.span
                      key={tag}
                      variants={tagVariants}
                      className="border border-primary/30 px-4 py-2 text-xs font-light uppercase tracking-widest text-primary"
                    >
                      {tag}
                    </motion.span>
                  ))}
                </motion.div>
                <h3 className="mb-6 font-serif text-4xl leading-tight text-foreground md:text-5xl">{project.title}</h3>
                <p className="mb-8 text-lg font-light leading-relaxed text-muted-foreground md:text-xl">
                  {project.description}
                </p>
                <Link
                  to={`/work/${project.slug}`}
                  className="inline-flex items-center gap-2 text-sm font-light uppercase tracking-widest text-primary transition-colors hover:text-foreground"
                >
                  Read the case study
                  <ArrowRight aria-hidden="true" className="h-4 w-4" />
                </Link>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};
