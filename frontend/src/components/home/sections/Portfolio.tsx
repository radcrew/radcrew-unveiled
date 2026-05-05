import { motion } from "framer-motion";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel";
import { featuredProjects } from "../static-data";
import { fadeIn } from "../motion";

export function Portfolio() {
  return (
    <section id="portfolio" className="border-y border-border bg-muted px-6 py-32 lg:px-12">
      <div className="mx-auto max-w-7xl">
        <motion.div
          initial="hidden"
          whileInView="visible"
          variants={fadeIn}
          viewport={{ once: true }}
          className="mb-24 flex flex-col items-baseline justify-between gap-8 border-b border-border pb-8 md:flex-row"
        >
          <h2 className="font-serif text-5xl text-foreground md:text-7xl">Selected Work</h2>
          <div className="text-sm font-light uppercase tracking-widest text-muted-foreground">Crafted with intent.</div>
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
                <div className="relative aspect-[4/3] overflow-hidden border border-border bg-background shadow-sm md:aspect-[16/10]">
                  {project.images && project.images.length > 0 ? (
                    <Carousel opts={{ loop: true }} className="absolute inset-0 h-full min-h-0 w-full">
                      <CarouselContent className="-ml-0 h-full min-h-0">
                        {project.images.map((src, idx) => (
                          <CarouselItem
                            key={`${project.title}-${idx}`}
                            className="relative h-full min-h-full basis-full self-stretch pl-0"
                          >
                            <img
                              src={src}
                              alt={`${project.title} — screen ${idx + 1}`}
                              className="absolute inset-0 h-full w-full object-fill opacity-90 transition-opacity duration-1000 group-hover:opacity-100"
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
                    </Carousel>
                  ) : project.image ? (
                    <img
                      src={project.image}
                      alt={project.title}
                      className="h-full w-full object-cover opacity-90 transition-transform duration-1000 group-hover:scale-105 group-hover:opacity-100"
                    />
                  ) : null}
                  <div className="pointer-events-none absolute inset-0 z-10 mix-blend-multiply bg-primary/5 transition-colors duration-700 group-hover:bg-transparent" />
                </div>
              </div>
              <div className={`flex flex-col justify-center md:col-span-5 ${i % 2 !== 0 ? "md:pr-12" : "md:pl-12"}`}>
                <div className="mb-8 flex flex-wrap gap-3">
                  {project.tags.map((tag) => (
                    <span
                      key={tag}
                      className="border border-primary/30 px-4 py-2 text-xs font-light uppercase tracking-widest text-primary"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
                <h3 className="mb-6 font-serif text-4xl leading-tight text-foreground md:text-5xl">{project.title}</h3>
                <p className="text-lg font-light leading-relaxed text-muted-foreground md:text-xl">{project.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
