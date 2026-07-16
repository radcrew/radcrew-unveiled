import { motion } from "framer-motion";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@components/ui/accordion";
import { faqs } from "../static-data";
import { fadeIn, staggerContainer } from "../motion";

export const Faq = () => {
  return (
    <section className="border-t border-border bg-muted px-6 py-20 md:py-32 lg:px-12">
      <div className="mx-auto max-w-3xl">
        <motion.h2
          initial="hidden"
          whileInView="visible"
          variants={fadeIn}
          viewport={{ once: true }}
          className="mb-16 text-center font-serif text-4xl text-foreground md:text-6xl"
        >
          Common Questions
        </motion.h2>

        <motion.div initial="hidden" whileInView="visible" variants={staggerContainer} viewport={{ once: true }}>
          <Accordion type="single" collapsible className="w-full">
            {faqs.map((faq, i) => (
              <motion.div key={faq.question} variants={fadeIn}>
                <AccordionItem value={`item-${i}`} className="border-border">
                  <AccordionTrigger className="py-6 text-left font-serif text-lg font-medium hover:text-primary hover:no-underline md:text-xl">
                    {faq.question}
                  </AccordionTrigger>
                  <AccordionContent className="pb-6 text-base font-light leading-relaxed text-muted-foreground">
                    {faq.answer}
                  </AccordionContent>
                </AccordionItem>
              </motion.div>
            ))}
          </Accordion>
        </motion.div>
      </div>
    </section>
  );
};
