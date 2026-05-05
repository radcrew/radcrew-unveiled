import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { faqs } from "../static-data";

export function Faq() {
  return (
    <section className="border-t border-border bg-muted px-6 py-32 lg:px-12">
      <div className="mx-auto max-w-3xl">
        <h2 className="mb-16 text-center font-serif text-4xl text-foreground md:text-6xl">Common Questions</h2>

        <Accordion type="single" collapsible className="w-full">
          {faqs.map((faq, i) => (
            <AccordionItem key={faq.question} value={`item-${i}`} className="border-border">
              <AccordionTrigger className="py-6 text-left font-serif text-lg font-medium hover:text-primary hover:no-underline md:text-xl">
                {faq.question}
              </AccordionTrigger>
              <AccordionContent className="pb-6 text-base font-light leading-relaxed text-muted-foreground">
                {faq.answer}
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </div>
    </section>
  );
}
