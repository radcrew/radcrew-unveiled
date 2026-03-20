import { useCallback, useEffect, useState } from "react";
import useEmblaCarousel from "embla-carousel-react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { useScrollReveal } from "@/hooks/useScrollReveal";
import { portfolioProjects } from "@/lib/portfolio-data";

const PortfolioSection = () => {
  const [emblaRef, emblaApi] = useEmblaCarousel({ loop: true, align: "center" });
  const ref = useScrollReveal();
  const [selected, setSelected] = useState(0);

  const scrollPrev = useCallback(() => emblaApi?.scrollPrev(), [emblaApi]);
  const scrollNext = useCallback(() => emblaApi?.scrollNext(), [emblaApi]);

  const scrollTo = useCallback((i: number) => emblaApi?.scrollTo(i), [emblaApi]);

  useEffect(() => {
    if (!emblaApi) return;
    const onSelect = () => setSelected(emblaApi.selectedScrollSnap());
    emblaApi.on("select", onSelect);
    onSelect();
    return () => {
      emblaApi.off("select", onSelect);
    };
  }, [emblaApi]);

  return (
    <section
      id="portfolio"
      className="border-y border-border bg-muted/40 py-24 md:py-32"
      ref={ref}
    >
      <div className="section-padding mx-auto mb-10 max-w-6xl">
        <p className="mb-3 text-sm font-semibold uppercase tracking-widest text-accent">Portfolio</p>
        <h2 className="mb-4 text-3xl font-bold md:text-4xl">Past wins, shipped end to end.</h2>
        <p className="max-w-2xl text-lg leading-relaxed text-muted-foreground">
          A snapshot of the kinds of problems we take from idea to production—swap in your own screenshots
          and stories anytime.
        </p>
      </div>

      <div className="relative">
        <div className="overflow-hidden px-0" ref={emblaRef}>
          <div className="flex">
            {portfolioProjects.map((project) => (
              <div
                key={project.id}
                className="min-w-0 flex-[0_0_88%] px-3 sm:flex-[0_0_76%] md:flex-[0_0_58%] lg:flex-[0_0_50%] xl:flex-[0_0_44%]"
              >
                <article className="overflow-hidden rounded-xl border border-border bg-card shadow-sm">
                  <div className="flex justify-center bg-muted/60 px-4 pb-1 pt-5">
                    <div className="relative aspect-[16/10] w-full max-w-sm overflow-hidden rounded-lg bg-muted sm:max-w-md md:max-w-lg">
                      <img
                        src={project.image}
                        alt={project.imageAlt}
                        className="h-full w-full object-cover"
                        loading="lazy"
                      />
                    </div>
                  </div>
                  <div className="border-t border-border p-6 md:p-8">
                    <div className="mb-3 flex flex-wrap gap-2">
                      {project.tags.map((tag) => (
                        <span
                          key={tag}
                          className="rounded-full border border-border bg-background px-3 py-0.5 text-xs font-medium text-muted-foreground"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                    <h3 className="mb-2 text-xl font-bold md:text-2xl">{project.title}</h3>
                    <p className="text-sm leading-relaxed text-muted-foreground md:text-base">
                      {project.achievement}
                    </p>
                  </div>
                </article>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-8 flex flex-col items-center gap-6">
          <div className="flex justify-center gap-3">
            <button
              type="button"
              onClick={scrollPrev}
              className="flex h-10 w-10 items-center justify-center rounded-full border border-border transition-colors hover:bg-card active:scale-95"
              aria-label="Previous project"
            >
              <ChevronLeft size={18} />
            </button>
            <button
              type="button"
              onClick={scrollNext}
              className="flex h-10 w-10 items-center justify-center rounded-full border border-border transition-colors hover:bg-card active:scale-95"
              aria-label="Next project"
            >
              <ChevronRight size={18} />
            </button>
          </div>
          <div className="flex justify-center gap-2" role="tablist" aria-label="Portfolio slides">
            {portfolioProjects.map((project, i) => (
              <button
                key={project.id}
                type="button"
                role="tab"
                aria-selected={selected === i}
                aria-label={`Show project ${i + 1}: ${project.title}`}
                onClick={() => scrollTo(i)}
                className={`h-2 rounded-full transition-all ${
                  selected === i ? "w-8 bg-accent" : "w-2 bg-border hover:bg-muted-foreground/40"
                }`}
              />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default PortfolioSection;
