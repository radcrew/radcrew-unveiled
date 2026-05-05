import { motion } from "framer-motion";
import { testimonial } from "../static-data";

export const Testimonial = () => {
  return (
    <section className="relative overflow-hidden border-t border-border bg-muted px-6 py-32 lg:px-12">
      <div className="mx-auto max-w-4xl text-center">
        <div className="mb-10 font-serif text-4xl italic text-primary">&quot;</div>

        <motion.div initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} transition={{ duration: 1 }}>
          <h3 className="mb-12 font-serif text-3xl leading-snug text-foreground md:text-5xl">{testimonial.quote}</h3>
          <div className="font-sans text-sm font-light uppercase tracking-widest">
            <span className="font-medium text-foreground">{testimonial.clientName}</span>
            <span className="mx-2 text-muted-foreground">—</span>
            <span className="text-muted-foreground">
              {testimonial.clientRole}, {testimonial.clientCompany}
            </span>
          </div>
        </motion.div>
      </div>
    </section>
  );
};
