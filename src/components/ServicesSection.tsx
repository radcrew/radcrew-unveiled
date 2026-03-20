import { Layers, Hexagon, Brain } from "lucide-react";
import { useScrollReveal } from "@/hooks/useScrollReveal";

const pillars = [
  {
    icon: Layers,
    title: "Full-stack product engineering",
    description:
      "Web apps, APIs, dashboards, and integrations—from greenfield MVPs to hardening production systems. TypeScript-first, cloud-ready, and built for maintainability.",
  },
  {
    icon: Hexagon,
    title: "Web3 on EVM & Solana",
    description:
      "Smart contracts, wallets, indexing, and protocol UX. We ship on Ethereum and L2s plus Solana when your product needs speed, composability, or cross-chain clarity.",
  },
  {
    icon: Brain,
    title: "AI in the real product",
    description:
      "LLM features, agents, RAG, and evaluation—not demos. We connect models to your data, your auth, and your stack so AI ships with the rest of the product.",
  },
];

const ServicesSection = () => {
  const ref = useScrollReveal();

  return (
    <section
      id="services"
      className="flex min-h-screen min-h-dvh flex-col justify-center border-y border-border bg-muted/40 section-padding py-10 sm:py-12 md:py-14 lg:py-16"
      ref={ref}
    >
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-10 md:gap-12 lg:gap-14">
        <header className="shrink-0 space-y-3 md:space-y-4">
          <p className="text-sm font-semibold uppercase tracking-widest text-accent">What we do</p>
          <h2 className="max-w-2xl text-3xl font-bold md:text-4xl lg:max-w-3xl">
            Capabilities across stack, chain, and model.
          </h2>
          <p className="max-w-2xl text-base leading-relaxed text-muted-foreground md:text-lg lg:max-w-3xl">
            One crew covers the surfaces users see, the systems behind them, and the on-chain and AI layers when your
            roadmap goes there.
          </p>
        </header>

        <div className="grid shrink-0 gap-6 md:grid-cols-3 md:gap-8">
          {pillars.map(({ icon: Icon, title, description }) => (
            <article
              key={title}
              className="rounded-lg border border-border bg-card p-8 transition-shadow duration-300 hover:border-accent/30 hover:shadow-lg hover:shadow-accent/5"
            >
              <div className="mb-6 flex h-14 w-14 items-center justify-center rounded-full bg-accent/10 text-accent">
                <Icon className="h-7 w-7" strokeWidth={1.5} />
              </div>
              <h3 className="mb-3 text-xl font-bold">{title}</h3>
              <p className="text-sm leading-relaxed text-muted-foreground">{description}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
};

export default ServicesSection;
