import { useState, type FormEvent } from "react";
import { Globe, Mail } from "lucide-react";
import { SiGithub } from "react-icons/si";
import { Button } from "@components/ui/button";
import { useToast } from "@/hooks/useToast";
import { getWeb3FormsAccessKey, submitWeb3Form } from "@/lib/web3forms-submit";

export const Footer = () => {
  const { toast } = useToast();
  const [newsletterPending, setNewsletterPending] = useState(false);
  const [newsletterEmail, setNewsletterEmail] = useState("");

  const handleNewsletterSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!newsletterEmail.trim()) return;
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
        email: newsletterEmail.trim(),
        message: `Newsletter signup: ${newsletterEmail.trim()}`,
      });
      toast({
        title: "Subscribed successfully.",
        description: "You're now on the list.",
      });
      setNewsletterEmail("");
    } catch {
      toast({
        title: "Subscription failed.",
        description: "Please try again later.",
        variant: "destructive",
      });
    } finally {
      setNewsletterPending(false);
    }
  };

  return (
    <footer id="footer" className="border-t-4 border-primary bg-foreground px-6 pb-12 pt-24 text-background lg:px-12">
      <div className="mx-auto max-w-7xl">
        <div className="mb-24 grid gap-16 md:grid-cols-2">
          <div>
            <div className="mb-8 text-3xl font-light uppercase tracking-[0.25em]">radcrew</div>
            <p className="max-w-sm leading-relaxed font-light text-background/70">
              An elite engineering studio building the future of technology for those who demand excellence.
            </p>
          </div>

          <div className="w-full max-w-md md:justify-self-end">
            <h4 className="mb-6 text-sm font-light uppercase tracking-widest opacity-70">Stay in the loop</h4>
            <form onSubmit={handleNewsletterSubmit} className="flex gap-2">
              <input
                type="email"
                placeholder="Email address"
                value={newsletterEmail}
                onChange={(e) => setNewsletterEmail(e.target.value)}
                className="h-14 flex-1 rounded-none border border-background/20 bg-background/10 px-6 font-light text-background placeholder:text-background/50 transition-colors focus:border-primary focus:outline-none"
                required
                data-testid="newsletter-email"
              />
              <Button
                type="submit"
                variant="outline"
                className="h-14 rounded-none bg-primary border-background/20 px-8 text-sm font-light uppercase tracking-widest text-background transition-all hover:bg-background hover:text-foreground"
                disabled={newsletterPending}
                data-testid="newsletter-submit"
              >
                {newsletterPending ? "Wait" : "Subscribe"}
              </Button>
            </form>
          </div>
        </div>

        <div className="flex flex-col items-center justify-between gap-6 border-t border-background/10 pt-8 text-sm font-light uppercase tracking-widest opacity-60 md:flex-row">
          <div className="flex gap-6">
            <a
              href="https://radcrew.org"
              target="_blank"
              rel="noopener noreferrer"
              className="transition-colors hover:text-primary"
              aria-label="RadCrew website"
            >
              <Globe className="h-5 w-5" />
            </a>
            <a href="mailto:code@radcrew.org" className="transition-colors hover:text-primary" aria-label="Email RadCrew">
              <Mail className="h-5 w-5" />
            </a>
            <a href="https://github.com/radcrew" className="transition-colors hover:text-primary" aria-label="GitHub">
              <SiGithub className="h-5 w-5" />
            </a>
          </div>
          <div className="text-center md:text-right">© {new Date().getFullYear()} radcrew. All rights reserved.</div>
        </div>
      </div>
    </footer>
  );
};
