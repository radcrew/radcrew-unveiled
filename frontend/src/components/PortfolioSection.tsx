import { useCallback, useEffect, useState } from "react";
import useEmblaCarousel from "embla-carousel-react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@components/ui/button";
import { RadButton } from "@components/ui/rad-button";
import { ScrollDriven } from "@components/ScrollDriven";
import { RadCard } from "@components/ui/rad-card";
import { cn } from "@/lib/utils";
import { portfolioProjects } from "@/lib/portfolio-data";

const PortfolioSection = () => {
  const [emblaRef, emblaApi] = useEmblaCarousel({ loop: true, align: "center" });
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
    <section id="portfolio" className="portfolio-shell">
      <div className="portfolio-inner">
        <ScrollDriven>
          <header className="section-block w-full">
            <p className="kicker">Portfolio</p>
            <h2 className="section-heading">Past wins, shipped end to end.</h2>
            <p className="section-prose-tight">
              A snapshot of the kinds of problems we take from idea to production—swap in your own screenshots and stories
              anytime.
            </p>
          </header>
        </ScrollDriven>

        <ScrollDriven className="relative w-full min-h-0 shrink-0">
          <div className="overflow-hidden px-0" ref={emblaRef}>
            <div className="flex">
              {portfolioProjects.map((project) => (
                <div key={project.id} className="portfolio-slide">
                  <RadCard
                    role="article"
                    className="mx-auto flex h-[24rem] w-full max-w-[17rem] flex-col overflow-hidden rounded-xl border-border p-0 shadow-sm sm:max-w-[19rem] md:max-w-[21rem] lg:max-w-[23rem]"
                  >
                    <div className="portfolio-img">
                      <img
                        src={project.image}
                        alt={project.imageAlt}
                        className="h-full w-full object-fill"
                        loading="lazy"
                      />
                    </div>
                    <div className="portfolio-body">
                      <div className="mb-2 flex shrink-0 flex-wrap gap-2">
                        {project.tags.map((tag) => (
                          <span key={tag} className="tag-pill">
                            {tag}
                          </span>
                        ))}
                      </div>
                      <h3 className="portfolio-title">{project.title}</h3>
                      <p className="portfolio-desc">{project.achievement}</p>
                    </div>
                  </RadCard>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-5 flex flex-col items-center gap-4 md:mt-6 md:gap-5">
            <div className="flex justify-center gap-3">
              <RadButton
                type="button"
                variant="outline"
                size="icon"
                className="rounded-full"
                onClick={scrollPrev}
                aria-label="Previous project"
              >
                <ChevronLeft size={18} />
              </RadButton>
              <RadButton
                type="button"
                variant="outline"
                size="icon"
                className="rounded-full"
                onClick={scrollNext}
                aria-label="Next project"
              >
                <ChevronRight size={18} />
              </RadButton>
            </div>
            <div className="flex justify-center gap-2" role="tablist" aria-label="Portfolio slides">
              {portfolioProjects.map((project, i) => (
                <Button
                  key={project.id}
                  type="button"
                  variant="ghost"
                  role="tab"
                  aria-selected={selected === i}
                  aria-label={`Show project ${i + 1}: ${project.title}`}
                  onClick={() => scrollTo(i)}
                  className={cn(
                    "!h-2 min-h-0 shrink-0 rounded-full px-0 py-0 font-[inherit] shadow-none transition-all hover:bg-muted-foreground/40",
                    selected === i
                      ? "!w-8 bg-accent hover:bg-accent hover:opacity-100"
                      : "!w-2 bg-border",
                  )}
                />
              ))}
            </div>
          </div>
        </ScrollDriven>
      </div>
    </section>
  );
};

export default PortfolioSection;
