import useEmblaCarousel from "embla-carousel-react";
import { useCallback } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { useScrollReveal } from "@/hooks/useScrollReveal";

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
  const ref = useScrollReveal();

  const scrollPrev = useCallback(() => emblaApi?.scrollPrev(), [emblaApi]);
  const scrollNext = useCallback(() => emblaApi?.scrollNext(), [emblaApi]);

  return (
    <section id="workspace" className="py-24 md:py-32" ref={ref}>
      <div className="content-max section-padding mb-10">
        <p className="text-accent font-semibold text-sm uppercase tracking-widest mb-3">Where We Work</p>
        <h2 className="text-3xl md:text-4xl font-bold">Our workspace.</h2>
      </div>

      <div className="relative">
        <div className="overflow-hidden" ref={emblaRef}>
          <div className="flex">
            {slides.map((slide, i) => (
              <div key={i} className="flex-[0_0_85%] md:flex-[0_0_70%] min-w-0 px-3">
                <div className="overflow-hidden rounded-xl">
                  <img
                    src={slide.src}
                    alt={slide.alt}
                    className="w-full h-[300px] md:h-[480px] object-cover"
                    loading="lazy"
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="flex justify-center gap-3 mt-8">
          <button
            onClick={scrollPrev}
            className="w-10 h-10 rounded-full border border-border flex items-center justify-center hover:bg-card transition-colors active:scale-95"
            aria-label="Previous slide"
          >
            <ChevronLeft size={18} />
          </button>
          <button
            onClick={scrollNext}
            className="w-10 h-10 rounded-full border border-border flex items-center justify-center hover:bg-card transition-colors active:scale-95"
            aria-label="Next slide"
          >
            <ChevronRight size={18} />
          </button>
        </div>
      </div>
    </section>
  );
};

export default WorkspaceCarousel;
