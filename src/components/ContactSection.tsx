import { Mail, ArrowRight } from "lucide-react";
import { useScrollReveal } from "@/hooks/useScrollReveal";

const ContactSection = () => {
  const ref = useScrollReveal();
  const email = "hello@radcrew.dev";

  return (
    <section
      id="contact"
      className="border-t border-border bg-gradient-to-b from-accent/[0.06] to-background py-24 md:py-32 section-padding"
      ref={ref}
    >
      <div className="mx-auto max-w-6xl">
        <div className="rounded-2xl border border-border bg-card p-10 md:p-14 lg:flex lg:items-center lg:justify-between lg:gap-12">
          <div className="max-w-xl">
            <p className="mb-3 text-sm font-semibold uppercase tracking-widest text-accent">Start a project</p>
            <h2 className="mb-4 text-3xl font-bold md:text-4xl">Tell us what you’re building.</h2>
            <p className="text-lg text-muted-foreground leading-relaxed">
              Full-stack, Web3, AI, or all three—we’ll reply with next steps, rough timelines, and how the crew would engage.
            </p>
          </div>
          <div className="mt-10 flex flex-col gap-4 lg:mt-0 lg:shrink-0">
            <a
              href={`mailto:${email}`}
              className="inline-flex items-center justify-center gap-2 rounded-lg bg-accent px-8 py-4 text-base font-semibold text-accent-foreground transition-opacity hover:opacity-90 active:scale-[0.98]"
            >
              <Mail className="h-5 w-5" />
              Email {email}
              <ArrowRight className="h-4 w-4 opacity-80" />
            </a>
            <p className="text-center text-xs text-muted-foreground lg:text-right">
              We usually respond within one to two business days.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ContactSection;
