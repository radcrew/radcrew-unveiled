import useEmblaCarousel from "embla-carousel-react";
import { useCallback } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { ScrollDriven } from "@components/ScrollDriven";
import { RadButton } from "@components/ui/rad-button";

import workspace1 from "@/assets/workspace-1.jpg";
import workspace2 from "@/assets/workspace-2.jpg";
import workspace3 from "@/assets/workspace-3.jpg";

const slides = [
  { src: workspace1, alt: "Open office with multiple coding stations" },
  { src: workspace2, alt: "Team collaboration around a large screen" },
  { src: workspace3, alt: "Night coding setup with ambient lighting" },
];

const WorkspaceCarousel = () => {
  const [emblaRef, emblaApi] = useEmblaCarousel({ loop: true, align: "center" });

  const scrollPrev = useCallback(() => emblaApi?.scrollPrev(), [emblaApi]);
  const scrollNext = useCallback(() => emblaApi?.scrollNext(), [emblaApi]);

  return (
    <section id="workspace" className="workspace-shell">
      <ScrollDriven className="content-max section-padding mb-10">
        <p className="kicker mb-3">Where We Work</p>
        <h2 className="section-heading">Our workspace.</h2>
      </ScrollDriven>

      <ScrollDriven className="relative">
        <div className="overflow-hidden" ref={emblaRef}>
          <div className="flex">
            {slides.map((slide, i) => (
              <div key={i} className="workspace-slide">
                <div className="overflow-hidden rounded-xl">
                  <img
                    src={slide.src}
                    alt={slide.alt}
                    className="h-[300px] w-full object-cover md:h-[480px]"
                    loading="lazy"
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-8 flex justify-center gap-3">
          <RadButton
            type="button"
            variant="outline"
            size="icon"
            className="rounded-full"
            onClick={scrollPrev}
            aria-label="Previous slide"
          >
            <ChevronLeft size={18} />
          </RadButton>
          <RadButton
            type="button"
            variant="outline"
            size="icon"
            className="rounded-full"
            onClick={scrollNext}
            aria-label="Next slide"
          >
            <ChevronRight size={18} />
          </RadButton>
        </div>
      </ScrollDriven>
    </section>
  );
};

export default WorkspaceCarousel;
