import { Mail, ArrowRight } from "lucide-react";
import { useScrollReveal } from "@/hooks/useScrollReveal";

const ContactSection = () => {
  const ref = useScrollReveal();
  const email = "hello@radcrew.dev";

  return (
    <section id="contact" className="contact-shell" ref={ref}>
      <div className="content-max">
        <div className="contact-card">
          <div className="max-w-xl">
            <p className="kicker mb-3">Start a project</p>
            <h2 className="section-heading mb-4">Tell us what you’re building.</h2>
            <p className="text-lg leading-relaxed text-muted-foreground">
              Full-stack, Web3, AI, or all three—we’ll reply with next steps, rough timelines, and how the crew would
              engage.
            </p>
          </div>
          <div className="mt-10 flex flex-col gap-4 lg:mt-0 lg:shrink-0">
            <a href={`mailto:${email}`} className="email-cta">
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
