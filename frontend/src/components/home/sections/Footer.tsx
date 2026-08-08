import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Globe, Loader2, Mail } from "lucide-react";
import { SiGithub } from "react-icons/si";
import { Button } from "@components/ui/button";
import { Form, FormControl, FormField, FormItem, FormMessage } from "@components/ui/form";
import { Input } from "@components/ui/input";
import { useToast } from "@/hooks/use-toast";
import { getWeb3FormsAccessKey, submitWeb3Form } from "@/lib/web3forms-submit";
import { scrollSectionIntoView } from "@/lib/scroll-to-section";
import { Grain } from "../Grain";

const newsletterSchema = z.object({
  email: z.string().email("Enter a valid email address"),
});

type NewsletterFormValues = z.infer<typeof newsletterSchema>;

const footerLinks = [
  { id: "services", label: "Services" },
  { id: "portfolio", label: "Work" },
  { id: "process", label: "Process" },
  { id: "journal", label: "Journal" },
  { id: "contact", label: "Contact" },
] as const;

const footerLinkClassName =
  "transition-colors hover:text-primary-on-dark focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-foreground";

const socialLinkClassName = footerLinkClassName;

export const Footer = () => {
  const { toast } = useToast();
  const [newsletterPending, setNewsletterPending] = useState(false);

  const newsletterForm = useForm<NewsletterFormValues>({
    resolver: zodResolver(newsletterSchema),
    defaultValues: { email: "" },
  });

  async function onNewsletterSubmit(data: NewsletterFormValues) {
    if (!getWeb3FormsAccessKey()) {
      toast({
        title: "Email us directly",
        description: "Set VITE_WEB3FORMS_ACCESS_KEY for the newsletter, or write to code@radcrew.org.",
        variant: "destructive",
      });
      return;
    }
    setNewsletterPending(true);
    try {
      await submitWeb3Form({
        subject: "RadCrew — newsletter signup",
        email: data.email,
        message: `Newsletter signup: ${data.email}`,
      });
      toast({
        title: "Subscribed successfully.",
        description: "You're now on the list.",
      });
      newsletterForm.reset();
    } catch {
      toast({
        title: "Subscription failed.",
        description: "Please try again later.",
        variant: "destructive",
      });
    } finally {
      setNewsletterPending(false);
    }
  }

  return (
    <footer
      id="footer"
      className="relative overflow-hidden border-t-4 border-primary-on-dark bg-foreground px-6 pb-12 pt-24 text-background antialiased lg:px-12"
    >
      <Grain />
      <div className="relative z-10 mx-auto max-w-7xl">
        <div className="mb-24 grid gap-16 md:grid-cols-3">
          <div>
            <div className="mb-8 text-3xl font-light uppercase tracking-[0.25em]">radcrew</div>
            <p className="max-w-sm leading-relaxed font-light text-background/70">
              A guild of independent developers building the future of technology.
            </p>
          </div>

          <div>
            <h4 className="mb-6 text-sm font-light uppercase tracking-widest opacity-70">Navigate</h4>
            <ul className="space-y-3 font-light text-background/70">
              {footerLinks.map((link) => (
                <li key={link.id}>
                  <button type="button" onClick={() => scrollSectionIntoView(link.id)} className={footerLinkClassName}>
                    {link.label}
                  </button>
                </li>
              ))}
            </ul>
          </div>

          <div className="w-full max-w-md md:justify-self-end">
            <h4 className="mb-6 text-sm font-light uppercase tracking-widest opacity-70">Stay in the loop</h4>
            <Form {...newsletterForm}>
              <form onSubmit={newsletterForm.handleSubmit(onNewsletterSubmit)} noValidate>
                <FormField
                  control={newsletterForm.control}
                  name="email"
                  render={({ field }) => (
                    <FormItem className="space-y-2">
                      <div className="flex gap-2">
                        <FormControl>
                          <Input
                            type="email"
                            placeholder="Email address"
                            {...field}
                            className="h-14 flex-1 rounded-none border-background/20 bg-background/10 font-light text-background placeholder:text-background/50 focus-visible:ring-primary focus-visible:ring-offset-foreground"
                            data-testid="newsletter-email"
                          />
                        </FormControl>
                        <Button
                          type="submit"
                          variant="outline"
                          // Ink on champagne, not cream: cream on this gold is 2.0:1.
                          className="h-14 rounded-none border-transparent bg-primary-on-dark px-8 text-sm font-light uppercase tracking-widest text-foreground transition-all hover:bg-background hover:text-foreground focus-visible:ring-offset-foreground"
                          disabled={newsletterPending}
                          data-testid="newsletter-submit"
                        >
                          {newsletterPending ? (
                            <span className="inline-flex items-center gap-2">
                              <Loader2 className="h-4 w-4 animate-spin" />
                              Subscribing
                            </span>
                          ) : (
                            "Subscribe"
                          )}
                        </Button>
                      </div>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </form>
            </Form>
          </div>
        </div>

        <div className="flex flex-col items-center justify-between gap-6 border-t border-background/10 pt-8 text-sm font-light uppercase tracking-widest opacity-60 md:flex-row">
          <div className="flex gap-6">
            <a
              href="https://radcrew.org"
              target="_blank"
              rel="noopener noreferrer"
              className={socialLinkClassName}
              aria-label="RadCrew website"
            >
              <Globe className="h-5 w-5" />
            </a>
            <a href="mailto:code@radcrew.org" className={socialLinkClassName} aria-label="Email RadCrew">
              <Mail className="h-5 w-5" />
            </a>
            <a href="https://github.com/radcrew" className={socialLinkClassName} aria-label="GitHub">
              <SiGithub className="h-5 w-5" />
            </a>
          </div>
          <div className="text-center md:text-right">© {new Date().getFullYear()} radcrew. All rights reserved.</div>
        </div>
      </div>
    </footer>
  );
};
