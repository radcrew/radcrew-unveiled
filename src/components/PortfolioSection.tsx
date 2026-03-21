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
      className="box-border flex h-screen h-dvh min-h-0 flex-col justify-center overflow-y-auto border-y border-border bg-muted/40 py-8 sm:py-10 md:py-12"
      ref={ref}
    >
      <div className="content-max section-padding flex min-h-0 flex-1 flex-col justify-center gap-6 md:gap-8 lg:gap-10">
        <header className="w-full shrink-0 space-y-3 md:space-y-4">
          <p className="text-sm font-semibold uppercase tracking-widest text-accent">Portfolio</p>
          <h2 className="text-3xl font-bold md:text-4xl">Past wins, shipped end to end.</h2>
          <p className="max-w-2xl text-base leading-relaxed text-muted-foreground md:text-lg">
            A snapshot of the kinds of problems we take from idea to production—swap in your own screenshots and stories
            anytime.
          </p>
        </header>

        <div className="relative w-full min-h-0 shrink-0">
          <div className="overflow-hidden px-0" ref={emblaRef}>
            <div className="flex">
              {portfolioProjects.map((project) => (
                <div
                  key={project.id}
                  className="min-w-0 flex-[0_0_70%] px-1.5 sm:flex-[0_0_58%] sm:px-2 md:flex-[0_0_40%] md:px-2.5 lg:flex-[0_0_32%] xl:flex-[0_0_26%]"
                >
                  <article className="mx-auto w-full max-w-[17rem] overflow-hidden rounded-xl border border-border bg-card shadow-sm sm:max-w-[19rem] md:max-w-[21rem] lg:max-w-[23rem]">
                    {/* Full-bleed top: image only, stretched to fill (no padding) */}
                    <div className="relative aspect-[16/10] w-full overflow-hidden bg-muted">
                      <img
                        src={project.image}
                        alt={project.imageAlt}
                        className="h-full w-full object-fill"
                        loading="lazy"
                      />
                    </div>
                    <div className="border-t border-border p-4 md:p-5">
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
                      <h3 className="mb-2 text-lg font-bold md:text-xl">{project.title}</h3>
                      <p className="text-sm leading-relaxed text-muted-foreground md:text-base">
                        {project.achievement}
                      </p>
                    </div>
                  </article>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-5 flex flex-col items-center gap-4 md:mt-6 md:gap-5">
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
