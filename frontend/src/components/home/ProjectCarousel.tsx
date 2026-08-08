import { useEffect, useState } from "react";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
  type CarouselApi,
} from "@components/ui/carousel";

type ProjectCarouselProps = {
  title: string;
  images: string[];
};

/**
 * The screen-by-screen carousel inside a project card. Absolutely positioned to
 * fill its container, so the caller owns the aspect ratio and this owns only
 * what moves through it.
 */
export const ProjectCarousel = ({ title, images }: ProjectCarouselProps) => {
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
              className="absolute inset-0 h-full w-full object-cover"
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
