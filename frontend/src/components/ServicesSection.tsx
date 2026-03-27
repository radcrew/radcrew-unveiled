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
    <section id="services" className="services-shell" ref={ref}>
      <div className="content-stack">
        <header className="section-block">
          <p className="kicker">What we do</p>
          <h2 className="section-heading max-w-2xl lg:max-w-3xl">Capabilities across stack, chain, and model.</h2>
          <p className="section-prose">
            One crew covers the surfaces users see, the systems behind them, and the on-chain and AI layers when your
            roadmap goes there.
          </p>
        </header>

        <div className="grid shrink-0 gap-6 md:grid-cols-3 md:gap-8">
          {pillars.map(({ icon: Icon, title, description }) => (
            <article key={title} className="service-card">
              <div className="service-icon-wrap">
                <Icon className="h-7 w-7" strokeWidth={1.5} />
              </div>
              <h3 className="mb-3 text-xl font-bold">{title}</h3>
              <p className="muted-p">{description}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
};

export default ServicesSection;
