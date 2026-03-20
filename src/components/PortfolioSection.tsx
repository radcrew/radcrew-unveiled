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
      className="flex min-h-screen min-h-dvh flex-col justify-center border-y border-border bg-muted/40 py-10 sm:py-12 md:py-14 lg:py-16"
      ref={ref}
    >
      <div className="flex w-full flex-col gap-8 md:gap-10 lg:gap-12">
        <div className="section-padding mx-auto w-full max-w-6xl shrink-0">
          <header className="space-y-3 md:space-y-4">
            <p className="text-sm font-semibold uppercase tracking-widest text-accent">Portfolio</p>
            <h2 className="text-3xl font-bold md:text-4xl">Past wins, shipped end to end.</h2>
            <p className="max-w-2xl text-base leading-relaxed text-muted-foreground md:text-lg">
              A snapshot of the kinds of problems we take from idea to production—swap in your own screenshots and
              stories anytime.
            </p>
          </header>
        </div>

        <div className="relative w-full min-h-0 shrink-0">
          <div className="overflow-hidden px-0" ref={emblaRef}>
            <div className="flex">
              {portfolioProjects.map((project) => (
                <div
                  key={project.id}
                  className="min-w-0 flex-[0_0_78%] px-2 sm:flex-[0_0_66%] sm:px-3 md:flex-[0_0_48%] lg:flex-[0_0_40%] xl:flex-[0_0_34%]"
                >
                  <article className="w-full overflow-hidden rounded-xl border border-border bg-card shadow-sm">
                    {/* Full-bleed top: image only, stretched to fill (no padding) */}
                    <div className="relative aspect-[16/10] w-full overflow-hidden bg-muted">
                      <img
                        src={project.image}
                        alt={project.imageAlt}
                        className="h-full w-full object-fill"
                        loading="lazy"
                      />
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
      </div>
    </section>
  );
};

export default PortfolioSection;
