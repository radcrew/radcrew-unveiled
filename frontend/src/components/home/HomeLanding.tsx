import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { motion, useScroll, useMotionValueEvent } from "framer-motion";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Linkedin } from "lucide-react";
import {
  SiReact,
  SiTypescript,
  SiNodedotjs,
  SiRust,
  SiPython,
  SiOpenai,
  SiPostgresql,
  SiRedis,
  SiGraphql,
  SiDocker,
  SiGithub,
  SiX,
} from "react-icons/si";

import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { useToast } from "@/hooks/useToast";
import { getWeb3FormsAccessKey, submitWeb3Form } from "@/lib/web3forms-submit";
import HeroCanvas from "@/components/HeroCanvas";
import { homeFaqs, homeProjects, homeTeam, homeTestimonial } from "./home-static-data";

const contactSchema = z.object({
  name: z.string().min(1, "Name is required"),
  email: z.string().email("Invalid email address"),
  company: z.string().optional(),
  projectType: z.enum(["fullstack", "web3", "ai", "other"], {
    required_error: "Please select a project type",
  }),
  message: z.string().min(10, "Please provide more details about your project"),
});

type ContactFormValues = z.infer<typeof contactSchema>;

function AnimatedCounter({ end, suffix = "", duration = 2 }: { end: number; suffix?: string; duration?: number }) {
  const [count, setCount] = useState(0);
  const nodeRef = useRef<HTMLDivElement>(null);
  const [inView, setInView] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting) {
          setInView(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1 },
    );
    if (nodeRef.current) observer.observe(nodeRef.current);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (!inView) return;
    let startTime: number | null = null;
    let animationFrameId = 0;

    const animate = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / (duration * 1000), 1);
      const easeProgress = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
      setCount(Math.floor(easeProgress * end));
      if (progress < 1) {
        animationFrameId = requestAnimationFrame(animate);
      }
    };

    animationFrameId = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationFrameId);
  }, [end, duration, inView]);

  return (
    <div ref={nodeRef} className="font-serif text-5xl text-foreground md:text-6xl">
      {count}
      <span className="ml-1 text-primary">{suffix}</span>
    </div>
  );
}

const fadeIn = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: [0.16, 1, 0.3, 1] } },
};

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.2 },
  },
};

export default function HomeLanding() {
  const { toast } = useToast();
  const [isScrolled, setIsScrolled] = useState(false);
  const { scrollY } = useScroll();

  useMotionValueEvent(scrollY, "change", (latest) => {
    setIsScrolled(latest > 50);
  });

  const [contactPending, setContactPending] = useState(false);
  const [newsletterPending, setNewsletterPending] = useState(false);
  const [newsletterEmail, setNewsletterEmail] = useState("");

  const form = useForm<ContactFormValues>({
    resolver: zodResolver(contactSchema),
    defaultValues: {
      name: "",
      email: "",
      company: "",
      projectType: undefined,
      message: "",
    },
  });

  async function onSubmit(data: ContactFormValues) {
    if (!getWeb3FormsAccessKey()) {
      toast({
        title: "Email us directly",
        description: "Set VITE_WEB3FORMS_ACCESS_KEY for the form, or write to code@radcrew.org.",
        variant: "destructive",
      });
      return;
    }
    setContactPending(true);
    try {
      const lines = [
        `Name: ${data.name}`,
        `Email: ${data.email}`,
        data.company ? `Company: ${data.company}` : "",
        `Project type: ${data.projectType}`,
        "",
        data.message,
      ].filter(Boolean);
      await submitWeb3Form({
        subject: "RadCrew — website inquiry",
        from_name: data.name,
        email: data.email,
        message: lines.join("\n"),
      });
      toast({
        title: "Inquiry received.",
        description: "We'll be in touch shortly to schedule a discovery call.",
      });
      form.reset();
    } catch {
      toast({
        title: "Something went wrong.",
        description: "Please try again later or email code@radcrew.org.",
        variant: "destructive",
      });
    } finally {
      setContactPending(false);
    }
  }

  const handleNewsletterSubmit = async (e: React.FormEvent) => {
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

  const scrollTo = (id: string) => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <div className="min-h-[100dvh] bg-background font-sans text-foreground selection:bg-primary/30 selection:text-primary">
      <nav
        className={`fixed left-0 right-0 top-0 z-50 transition-all duration-500 ${
          isScrolled ? "border-b border-primary/20 bg-background/90 py-4 backdrop-blur-xl" : "bg-transparent py-6"
        }`}
      >
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 lg:px-12">
          <Link
            to="/"
            className="cursor-pointer text-xl font-light uppercase tracking-[0.25em]"
            data-testid="nav-logo"
          >
            radcrew
          </Link>
          <div className="hidden items-center gap-10 text-sm uppercase tracking-widest md:flex">
            <button
              type="button"
              onClick={() => scrollTo("services")}
              className="transition-colors hover:text-primary"
              data-testid="nav-services"
            >
              Services
            </button>
            <button
              type="button"
              onClick={() => scrollTo("portfolio")}
              className="transition-colors hover:text-primary"
              data-testid="nav-portfolio"
            >
              Work
            </button>
            <button
              type="button"
              onClick={() => scrollTo("process")}
              className="transition-colors hover:text-primary"
              data-testid="nav-process"
            >
              Process
            </button>
            <button
              type="button"
              onClick={() => scrollTo("team")}
              className="transition-colors hover:text-primary"
              data-testid="nav-team"
            >
              Team
            </button>
            <Button
              type="button"
              onClick={() => scrollTo("contact")}
              variant="outline"
              className="h-auto rounded-none border-primary px-8 py-5 font-light uppercase tracking-widest text-primary hover:bg-primary hover:text-primary-foreground"
              data-testid="nav-contact"
            >
              Get in Touch
            </Button>
          </div>
        </div>
      </nav>

      <section className="relative flex min-h-[100dvh] items-center justify-center overflow-hidden px-6 pt-24">
        <div className="absolute inset-0 z-0">
          <HeroCanvas />
          <div className="absolute inset-0 bg-gradient-to-b from-background/30 via-transparent to-background" />
        </div>

        <div className="relative z-10 mx-auto w-full max-w-7xl text-center md:text-left">
          <motion.div initial="hidden" whileInView="visible" variants={staggerContainer} viewport={{ once: true }}>
            <motion.h1
              variants={fadeIn}
              className="mb-8 font-serif text-6xl leading-[0.9] tracking-tight text-foreground md:text-8xl lg:text-[11rem]"
            >
              We build <br />
              <span className="font-medium italic text-primary">what&apos;s next.</span>
            </motion.h1>
            <motion.p
              variants={fadeIn}
              className="mx-auto mb-12 max-w-2xl text-xl font-light leading-relaxed text-muted-foreground md:mx-0 md:text-2xl"
            >
              An elite engineering studio building AI/ML products and Web3 solutions on EVM and Solana. For discerning
              clients who demand precision.
            </motion.p>
            <motion.div
              variants={fadeIn}
              className="flex flex-col justify-center gap-6 sm:flex-row md:justify-start"
            >
              <Button
                type="button"
                onClick={() => scrollTo("portfolio")}
                className="h-auto rounded-none bg-primary px-10 py-7 text-sm font-light uppercase tracking-widest text-primary-foreground hover:bg-primary/90"
                data-testid="hero-cta-work"
              >
                View Selected Work
              </Button>
              <Button
                type="button"
                onClick={() => scrollTo("contact")}
                variant="outline"
                className="h-auto rounded-none border-border px-10 py-7 text-sm font-light uppercase tracking-widest hover:bg-muted"
                data-testid="hero-cta-contact"
              >
                Start a Project
              </Button>
            </motion.div>
          </motion.div>
        </div>
      </section>

      <section className="border-t border-border bg-background px-6 py-24 lg:px-12">
        <div className="mx-auto max-w-7xl">
          <div className="grid grid-cols-2 gap-12 text-center md:grid-cols-4 md:text-left">
            <div>
              <AnimatedCounter end={40} suffix="+" />
              <div className="mt-4 text-sm font-light uppercase tracking-widest text-muted-foreground">
                Projects Shipped
              </div>
            </div>
            <div>
              <AnimatedCounter end={12} suffix="+" />
              <div className="mt-4 text-sm font-light uppercase tracking-widest text-muted-foreground">
                Happy Clients
              </div>
            </div>
            <div>
              <AnimatedCounter end={5} suffix="" />
              <div className="mt-4 text-sm font-light uppercase tracking-widest text-muted-foreground">
                Years Building
              </div>
            </div>
            <div>
              <div className="font-serif text-5xl text-foreground md:text-6xl">
                99.9<span className="ml-1 text-primary">%</span>
              </div>
              <div className="mt-4 text-sm font-light uppercase tracking-widest text-muted-foreground">Uptime SLA</div>
            </div>
          </div>
        </div>
      </section>

      <section id="services" className="relative bg-muted px-6 py-32 lg:px-12">
        <div className="mx-auto max-w-7xl">
          <motion.div
            initial="hidden"
            whileInView="visible"
            variants={fadeIn}
            viewport={{ once: true, margin: "-100px" }}
          >
            <h2 className="mb-20 border-b border-border pb-8 font-serif text-5xl text-foreground md:text-7xl">
              Capabilities
            </h2>
          </motion.div>

          <div className="grid gap-8 md:grid-cols-3">
            <motion.div
              initial="hidden"
              whileInView="visible"
              variants={staggerContainer}
              viewport={{ once: true }}
              className="group border border-primary/20 bg-background p-10 transition-all duration-500 hover:-translate-y-2 hover:border-primary/50 hover:shadow-xl hover:shadow-primary/5"
            >
              <div className="mb-8 font-serif text-3xl italic text-primary">01</div>
              <h3 className="mb-4 font-serif text-3xl text-foreground">Full Stack Product Engineering</h3>
              <p className="font-light leading-relaxed text-muted-foreground">
                From scalable data pipelines to bulletproof production systems. We build platforms that are architected
                to scale elegantly from day one.
              </p>
            </motion.div>

            <motion.div
              initial="hidden"
              whileInView="visible"
              variants={staggerContainer}
              viewport={{ once: true }}
              className="group border border-primary/20 bg-background p-10 transition-all duration-500 hover:-translate-y-2 hover:border-primary/50 hover:shadow-xl hover:shadow-primary/5"
            >
              <div className="mb-8 font-serif text-3xl italic text-primary">02</div>
              <h3 className="mb-4 font-serif text-3xl text-foreground">Web3 on EVM & Solana</h3>
              <p className="font-light leading-relaxed text-muted-foreground">
                Secure smart contract development, complex DeFi mechanics, and full-stack dApp architecture. Rigorously
                tested, flawlessly executed.
              </p>
            </motion.div>

            <motion.div
              initial="hidden"
              whileInView="visible"
              variants={staggerContainer}
              viewport={{ once: true }}
              className="group border border-primary/20 bg-background p-10 transition-all duration-500 hover:-translate-y-2 hover:border-primary/50 hover:shadow-xl hover:shadow-primary/5"
            >
              <div className="mb-8 font-serif text-3xl italic text-primary">03</div>
              <h3 className="mb-4 font-serif text-3xl text-foreground">AI in the Real Product</h3>
              <p className="font-light leading-relaxed text-muted-foreground">
                Embedding intelligent capabilities into existing stacks. From custom RAG pipelines to fine-tuned
                autonomous agents.
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      <section id="process" className="border-t border-border bg-background px-6 py-32 lg:px-12">
        <div className="mx-auto max-w-7xl">
          <motion.div initial="hidden" whileInView="visible" variants={fadeIn} viewport={{ once: true }} className="mb-24">
            <h2 className="max-w-4xl font-serif text-5xl leading-tight text-foreground md:text-7xl">
              From first call to production—and after.
            </h2>
          </motion.div>

          <div className="grid gap-12 border-l border-primary/20 pl-8 md:grid-cols-4 md:border-l-0 md:border-t md:border-primary/20 md:pl-0 md:pt-12">
            {[
              { num: "I.", title: "Discover", desc: "We map the architecture, define constraints, and build the blueprint." },
              { num: "II.", title: "Build", desc: "Elite engineering velocity. Transparent sprints. Relentless precision." },
              { num: "III.", title: "Ship", desc: "Deploy to production, stabilize infrastructure, and hand off clean docs." },
              { num: "IV.", title: "Partner", desc: "Long-term embedded relationship to scale the product forward." },
            ].map((phase, i) => (
              <motion.div
                key={phase.num}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.8, delay: i * 0.15 }}
                className="relative"
              >
                <div className="mb-6 font-serif text-4xl italic text-primary">{phase.num}</div>
                <h4 className="mb-4 font-serif text-2xl text-foreground">{phase.title}</h4>
                <p className="font-light leading-relaxed text-muted-foreground">{phase.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <section id="portfolio" className="border-y border-border bg-muted px-6 py-32 lg:px-12">
        <div className="mx-auto max-w-7xl">
          <motion.div
            initial="hidden"
            whileInView="visible"
            variants={fadeIn}
            viewport={{ once: true }}
            className="mb-24 flex flex-col items-baseline justify-between gap-8 border-b border-border pb-8 md:flex-row"
          >
            <h2 className="font-serif text-5xl text-foreground md:text-7xl">Selected Work</h2>
            <div className="text-sm font-light uppercase tracking-widest text-muted-foreground">Crafted with intent.</div>
          </motion.div>

          <div className="space-y-32">
            {homeProjects.map((project, i) => (
              <motion.div
                key={project.title}
                initial={{ opacity: 0, y: 40 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 1 }}
                className="group grid items-center gap-12 md:grid-cols-12"
              >
                <div className={`md:col-span-7 ${i % 2 !== 0 ? "md:order-last" : ""}`}>
                  <div className="relative aspect-[4/3] overflow-hidden border border-border bg-background shadow-sm md:aspect-[16/10]">
                    <img
                      src={project.image}
                      alt={project.title}
                      className="h-full w-full object-cover opacity-90 transition-transform duration-1000 group-hover:scale-105 group-hover:opacity-100"
                    />
                    <div className="absolute inset-0 mix-blend-multiply bg-primary/5 transition-colors duration-700 group-hover:bg-transparent" />
                  </div>
                </div>
                <div className={`flex flex-col justify-center md:col-span-5 ${i % 2 !== 0 ? "md:pr-12" : "md:pl-12"}`}>
                  <div className="mb-8 flex flex-wrap gap-3">
                    {project.tags.map((tag) => (
                      <span
                        key={tag}
                        className="border border-primary/30 px-4 py-2 text-xs font-light uppercase tracking-widest text-primary"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                  <h3 className="mb-6 font-serif text-4xl leading-tight text-foreground md:text-5xl">{project.title}</h3>
                  <p className="text-lg font-light leading-relaxed text-muted-foreground md:text-xl">{project.description}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-background px-6 py-24 lg:px-12">
        <div className="mx-auto max-w-7xl text-center">
          <div className="mb-12 text-sm font-light uppercase tracking-widest text-muted-foreground">
            Technologies We Master
          </div>

          <div className="flex flex-wrap justify-center gap-12 text-muted-foreground/60">
            <SiReact className="h-10 w-10 transition-colors duration-300 hover:text-primary" title="React" />
            <SiTypescript className="h-10 w-10 transition-colors duration-300 hover:text-primary" title="TypeScript" />
            <SiNodedotjs className="h-10 w-10 transition-colors duration-300 hover:text-primary" title="Node.js" />
            <SiRust className="h-10 w-10 transition-colors duration-300 hover:text-primary" title="Rust" />
            <div className="flex items-center justify-center text-xl font-bold uppercase tracking-widest transition-colors duration-300 hover:text-primary">
              Solana
            </div>
            <div className="flex items-center justify-center text-xl font-bold uppercase tracking-widest transition-colors duration-300 hover:text-primary">
              EVM
            </div>
            <SiPython className="h-10 w-10 transition-colors duration-300 hover:text-primary" title="Python" />
            <SiOpenai className="h-10 w-10 transition-colors duration-300 hover:text-primary" title="OpenAI" />
            <SiPostgresql className="h-10 w-10 transition-colors duration-300 hover:text-primary" title="PostgreSQL" />
            <SiRedis className="h-10 w-10 transition-colors duration-300 hover:text-primary" title="Redis" />
            <SiGraphql className="h-10 w-10 transition-colors duration-300 hover:text-primary" title="GraphQL" />
            <SiDocker className="h-10 w-10 transition-colors duration-300 hover:text-primary" title="Docker" />
          </div>
        </div>
      </section>

      <section className="relative overflow-hidden border-t border-border bg-muted px-6 py-32 lg:px-12">
        <div className="mx-auto max-w-4xl text-center">
          <div className="mb-10 font-serif text-4xl italic text-primary">&quot;</div>

          <motion.div initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} transition={{ duration: 1 }}>
            <h3 className="mb-12 font-serif text-3xl leading-snug text-foreground md:text-5xl">{homeTestimonial.quote}</h3>
            <div className="font-sans text-sm font-light uppercase tracking-widest">
              <span className="font-medium text-foreground">{homeTestimonial.clientName}</span>
              <span className="mx-2 text-muted-foreground">—</span>
              <span className="text-muted-foreground">
                {homeTestimonial.clientRole}, {homeTestimonial.clientCompany}
              </span>
            </div>
          </motion.div>
        </div>
      </section>

      <section id="team" className="relative border-t border-border bg-background px-6 py-32 lg:px-12">
        <div className="mx-auto max-w-7xl">
          <motion.div
            initial="hidden"
            whileInView="visible"
            variants={fadeIn}
            viewport={{ once: true }}
            className="mb-24 text-center"
          >
            <h2 className="mb-6 font-serif text-5xl text-foreground md:text-7xl">Three minds, one mission.</h2>
            <p className="text-xl font-light text-muted-foreground">Senior talent only. Precision at every level.</p>
          </motion.div>

          <div className="mx-auto grid max-w-5xl gap-12 md:grid-cols-3">
            {homeTeam.map((member, i) => (
              <motion.div
                key={member.name}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.8, delay: i * 0.15 }}
                className="group text-center"
              >
                <div className="relative mx-auto mb-8 aspect-[3/4] w-full overflow-hidden border border-border bg-muted">
                  <div className="absolute inset-0 z-10 mix-blend-multiply bg-primary/10 transition-colors duration-700 group-hover:bg-transparent" />
                  <img
                    src={member.image}
                    alt={member.name}
                    className="h-full w-full object-cover grayscale transition-all duration-1000 group-hover:grayscale-0"
                  />
                </div>
                <h3 className="mb-3 font-serif text-3xl text-foreground">{member.name}</h3>
                <p className="text-sm font-light uppercase tracking-widest text-primary">{member.role}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <section className="border-t border-border bg-muted px-6 py-32 lg:px-12">
        <div className="mx-auto max-w-3xl">
          <h2 className="mb-16 text-center font-serif text-4xl text-foreground md:text-6xl">Common Questions</h2>

          <Accordion type="single" collapsible className="w-full">
            {homeFaqs.map((faq, i) => (
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

      <section id="contact" className="relative border-t border-border bg-background px-6 py-32 lg:px-12">
        <div className="mx-auto max-w-4xl">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="mb-16 text-center"
          >
            <h2 className="mb-6 font-serif text-5xl leading-tight text-foreground md:text-7xl">
              Tell us what you&apos;re <span className="italic text-primary">building.</span>
            </h2>
            <p className="mx-auto max-w-2xl text-xl font-light text-muted-foreground">
              A private invitation to collaborate. Fill out the form and we&apos;ll arrange a technical discovery session.
            </p>
          </motion.div>

          <div className="border border-border bg-muted p-8 shadow-sm md:p-12">
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
                <div className="grid gap-8 md:grid-cols-2">
                  <FormField
                    control={form.control}
                    name="name"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-sm font-light uppercase tracking-widest text-muted-foreground">
                          Full Name
                        </FormLabel>
                        <FormControl>
                          <Input
                            placeholder="Jane Doe"
                            {...field}
                            className="h-14 rounded-none border-border bg-background font-light focus-visible:ring-primary"
                            data-testid="contact-name"
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="email"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-sm font-light uppercase tracking-widest text-muted-foreground">
                          Email Address
                        </FormLabel>
                        <FormControl>
                          <Input
                            placeholder="jane@company.com"
                            {...field}
                            className="h-14 rounded-none border-border bg-background font-light focus-visible:ring-primary"
                            data-testid="contact-email"
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                <div className="grid gap-8 md:grid-cols-2">
                  <FormField
                    control={form.control}
                    name="company"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-sm font-light uppercase tracking-widest text-muted-foreground">
                          Company (Optional)
                        </FormLabel>
                        <FormControl>
                          <Input
                            placeholder="Company Inc."
                            {...field}
                            className="h-14 rounded-none border-border bg-background font-light focus-visible:ring-primary"
                            data-testid="contact-company"
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="projectType"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-sm font-light uppercase tracking-widest text-muted-foreground">
                          Project Type
                        </FormLabel>
                        <Select onValueChange={field.onChange} value={field.value ?? ""}>
                          <FormControl>
                            <SelectTrigger
                              className="h-14 rounded-none border-border bg-background font-light data-[state=open]:text-foreground focus:ring-primary text-muted-foreground"
                              data-testid="contact-project-type"
                            >
                              <SelectValue placeholder="Select type" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent className="rounded-none border-border">
                            <SelectItem value="fullstack" className="cursor-pointer font-light">
                              Full Stack Engineering
                            </SelectItem>
                            <SelectItem value="web3" className="cursor-pointer font-light">
                              Web3 / Blockchain
                            </SelectItem>
                            <SelectItem value="ai" className="cursor-pointer font-light">
                              AI / Machine Learning
                            </SelectItem>
                            <SelectItem value="other" className="cursor-pointer font-light">
                              Other
                            </SelectItem>
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                <FormField
                  control={form.control}
                  name="message"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-sm font-light uppercase tracking-widest text-muted-foreground">
                        Project Details
                      </FormLabel>
                      <FormControl>
                        <Textarea
                          placeholder="Tell us about the vision, timeline, and budget..."
                          className="min-h-[150px] resize-y rounded-none border-border bg-background font-light focus-visible:ring-primary"
                          {...field}
                          data-testid="contact-message"
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <Button
                  type="submit"
                  className="h-16 w-full rounded-none bg-primary text-sm font-light uppercase tracking-widest text-primary-foreground transition-all hover:bg-primary/90"
                  disabled={contactPending}
                  data-testid="contact-submit"
                >
                  {contactPending ? "Submitting..." : "Submit Inquiry"}
                </Button>
              </form>
            </Form>
          </div>
        </div>
      </section>

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
                  className="h-14 rounded-none border-background/20 px-8 text-sm font-light uppercase tracking-widest text-background transition-all hover:bg-background hover:text-foreground"
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
              <a href="https://github.com" className="transition-colors hover:text-primary" aria-label="GitHub">
                <SiGithub className="h-5 w-5" />
              </a>
              <a href="https://twitter.com" className="transition-colors hover:text-primary" aria-label="Twitter">
                <SiX className="h-5 w-5" />
              </a>
              <a href="https://linkedin.com" className="transition-colors hover:text-primary" aria-label="LinkedIn">
                <Linkedin className="h-5 w-5" />
              </a>
            </div>
            <div className="text-center md:text-right">© {new Date().getFullYear()} radcrew. All rights reserved.</div>
          </div>
        </div>
      </footer>
    </div>
  );
}
