import { Mail, ArrowRight } from "lucide-react";
import { RadButton } from "@/components/ui/rad-button";
import { ScrollDriven } from "@/components/ScrollDriven";
import { RadCard } from "@/components/ui/rad-card";

const ContactSection = () => {
  const email = "code@radcrew.org";

  return (
    <section id="contact" className="contact-shell">
      <div className="content-max">
        <ScrollDriven>
          <RadCard className="rounded-2xl p-10 shadow-sm md:p-14 lg:flex lg:items-center lg:justify-between lg:gap-12">
            <div className="max-w-xl">
              <p className="kicker mb-3">Start a project</p>
              <h2 className="section-heading mb-4">Tell us what you’re building.</h2>
              <p className="section-prose max-w-none">
                Full-stack, Web3, AI, or all three—we’ll reply with next steps, rough timelines, and how the crew would
                engage.
              </p>
            </div>
            <div className="mt-10 flex flex-col gap-4 lg:mt-0 lg:shrink-0">
              <RadButton
                asChild
                className="h-auto gap-2 rounded-lg bg-accent px-8 py-4 text-base font-semibold text-accent-foreground shadow-none hover:bg-accent hover:opacity-90 active:scale-[0.98]"
              >
                <a href={`mailto:${email}`}>
                  <Mail className="h-5 w-5" />
                  Email {email}
                  <ArrowRight className="h-4 w-4 opacity-80" />
                </a>
              </RadButton>
              <p className="text-center text-xs text-muted-foreground lg:text-right">
                We usually respond within one to two business days.
              </p>
            </div>
          </RadCard>
        </ScrollDriven>
      </div>
    </section>
  );
};

export default ContactSection;
