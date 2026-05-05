import { motion } from "framer-motion";
import { fadeIn, staggerContainer } from "../motion";

const capabilityCards = [
  {
    index: "01",
    title: "Full Stack Product Engineering",
    description:
      "From scalable data pipelines to bulletproof production systems. We build platforms that are architected to scale elegantly from day one.",
  },
  {
    index: "02",
    title: "Web3 on EVM & Solana",
    description:
      "Secure smart contract development, complex DeFi mechanics, and full-stack dApp architecture. Rigorously tested, flawlessly executed.",
  },
  {
    index: "03",
    title: "AI in the Real Product",
    description:
      "Embedding intelligent capabilities into existing stacks. From custom RAG pipelines to fine-tuned autonomous agents.",
  },
] as const;

const cardClassName =
  "group border border-primary/20 bg-background p-10 transition-all duration-500 hover:-translate-y-2 hover:border-primary/50 hover:shadow-xl hover:shadow-primary/5";

export function Capabilities() {
  return (
    <section id="services" className="relative bg-muted px-6 py-32 lg:px-12">
      <div className="mx-auto max-w-7xl">
        <motion.div
          initial="hidden"
          whileInView="visible"
          variants={fadeIn}
          viewport={{ once: true, margin: "-100px" }}
        >
          <h2 className="mb-20 border-b border-border pb-8 font-serif text-5xl text-foreground md:text-7xl">Capabilities</h2>
        </motion.div>

        <div className="grid gap-8 md:grid-cols-3">
          {capabilityCards.map((card) => (
            <motion.div
              key={card.index}
              initial="hidden"
              whileInView="visible"
              variants={staggerContainer}
              viewport={{ once: true }}
              className={cardClassName}
            >
              <div className="mb-8 font-serif text-3xl italic text-primary">{card.index}</div>
              <h3 className="mb-4 font-serif text-3xl text-foreground">{card.title}</h3>
              <p className="font-light leading-relaxed text-muted-foreground">{card.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
