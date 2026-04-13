import { Layers, Hexagon, Brain } from "lucide-react";
import { CardTitle } from "@/components/ui/card";
import { ScrollDriven } from "@/components/ScrollDriven";
import { RadCard } from "@/components/ui/rad-card";

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
  return (
    <section id="services" className="services-shell">
      <div className="content-stack">
        <ScrollDriven>
          <header className="section-block">
            <p className="kicker">What we do</p>
            <h2 className="section-heading max-w-2xl lg:max-w-3xl">Capabilities across stack, chain, and model.</h2>
            <p className="section-prose">
              One crew covers the surfaces users see, the systems behind them, and the on-chain and AI layers when your
              roadmap goes there.
            </p>
          </header>
        </ScrollDriven>

        <div className="grid shrink-0 gap-6 md:grid-cols-3 md:gap-8">
          {pillars.map(({ icon: Icon, title, description }) => (
            <ScrollDriven key={title}>
              <RadCard role="article" className="h-full p-8">
                <div className="service-icon-wrap">
                  <Icon className="h-7 w-7" strokeWidth={1.5} />
                </div>
                <CardTitle className="mb-3 mt-0 text-xl font-bold">{title}</CardTitle>
                <p className="muted-p">{description}</p>
              </RadCard>
            </ScrollDriven>
          ))}
        </div>
      </div>
    </section>
  );
};

export default ServicesSection;
