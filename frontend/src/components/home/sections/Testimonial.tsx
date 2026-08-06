import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Carousel, CarouselContent, CarouselItem, type CarouselApi } from "@components/ui/carousel";
import { placeholderTestimonials as testimonials } from "../placeholder-content";

const AUTOPLAY_INTERVAL_MS = 6000;

export const Testimonial = () => {
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

  useEffect(() => {
    if (!api || testimonials.length <= 1) return;
    const id = setInterval(() => api.scrollNext(), AUTOPLAY_INTERVAL_MS);
    return () => clearInterval(id);
  }, [api]);

  return (
    <section className="relative overflow-hidden border-t border-border bg-muted px-6 py-20 md:py-32 lg:px-12">
      <div className="mx-auto max-w-4xl text-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.5 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="mb-10 font-serif text-4xl italic text-primary"
        >
          &quot;
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1], delay: 0.15 }}
        >
          <Carousel opts={{ loop: true }} setApi={setApi}>
            <CarouselContent>
              {testimonials.map((item) => (
                <CarouselItem key={item.clientName}>
                  <h3 className="mb-12 font-serif text-3xl leading-snug text-foreground md:text-5xl">{item.quote}</h3>
                  <div className="font-sans text-sm font-light uppercase tracking-widest">
                    <span className="font-medium text-foreground">{item.clientName}</span>
                    <span className="mx-2 text-muted-foreground">—</span>
                    <span className="text-muted-foreground">
                      {item.clientRole}, {item.clientCompany}
                    </span>
                  </div>
                </CarouselItem>
              ))}
            </CarouselContent>
          </Carousel>

          {testimonials.length > 1 && (
            <div className="mt-10 flex items-center justify-center gap-2">
              {testimonials.map((item, idx) => (
                <button
                  key={item.clientName}
                  type="button"
                  onClick={() => api?.scrollTo(idx)}
                  aria-label={`Go to testimonial ${idx + 1} of ${testimonials.length}`}
                  aria-current={idx === selectedIndex}
                  className={`h-1.5 rounded-full transition-all duration-300 ${
                    idx === selectedIndex ? "w-6 bg-primary" : "w-1.5 bg-foreground/20 hover:bg-primary/60"
                  }`}
                />
              ))}
            </div>
          )}
        </motion.div>
      </div>
    </section>
  );
};
