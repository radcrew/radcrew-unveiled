import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";
import { maskWipe, riseIn, staggerContainer } from "../motion";

type CapabilitiesProps = {
  onNavigate: (sectionId: string) => void;
};

const capabilityCards = [
  {
    index: "01",
    title: "Full Stack Product Engineering",
    description:
      "From scalable data pipelines to bulletproof production systems. We build platforms that are architected to scale elegantly from day one.",
    relatedProject: "Forgeng",
  },
  {
    index: "02",
    title: "Web3 on EVM & Solana",
    description:
      "Secure smart contract development, complex DeFi mechanics, and full-stack dApp architecture. Rigorously tested, flawlessly executed.",
    relatedProject: "CryptoPets",
  },
  {
    index: "03",
    title: "AI in the Real Product",
    description:
      "Embedding intelligent capabilities into existing stacks. From custom RAG pipelines to fine-tuned autonomous agents.",
    relatedProject: "Real Estate Consultant",
  },
  {
    index: "04",
    title: "Contract Review & Security",
    description:
      "Line-by-line review of the code that holds funds. Accounting drift, upgrade paths, and the failure modes that survive a happy-path test suite.",
    relatedProject: null,
  },
  {
    index: "05",
    title: "Data Platforms & Pipelines",
    description:
      "Ingestion, transformation, and retrieval that stay predictable under load. Built to be resumed after a failure rather than restarted.",
    relatedProject: null,
  },
  {
    index: "06",
    title: "Embedded Engineering",
    description:
      "Senior engineers inside your team, on your standups and in your repo. Not a black box that returns a deliverable at the end of a quarter.",
    relatedProject: null,
  },
] as const;

// `bg-card` sits a step lighter than the paper ground, so the cards read as
// raised surfaces. They previously used `bg-background`, the same colour as the
// section behind them, and were defined only by their hairline border.
const cardClassName =
  "group border border-border bg-card p-10 shadow-[0_1px_2px_rgba(26,23,20,0.04)] transition-all duration-500 hover:-translate-y-2 hover:border-primary/40 hover:shadow-xl hover:shadow-primary/10";

export const Capabilities = ({ onNavigate }: CapabilitiesProps) => {
  return (
    <section id="services" className="relative border-t border-border bg-background px-6 py-20 md:py-32 lg:px-12">
      <div className="mx-auto max-w-7xl">
        <motion.div
          initial="hidden"
          whileInView="visible"
          variants={maskWipe}
          // No `margin` here, unlike every other viewport trigger in this
          // file's history: a negative viewport margin stops the `clipPath`
          // keyframes firing at all, and the heading stays fully clipped and
          // invisible. `fadeIn` was unaffected, which is why the margin
          // survived until this section took the wipe.
          viewport={{ once: true }}
        >
          <h2 className="mb-20 border-b border-border pb-8 font-serif text-5xl text-foreground md:text-7xl">Capabilities</h2>
        </motion.div>

        {/* The stagger belongs on the grid, not on each card. It was previously
            set on every card individually, where it had no variant children to
            stagger and so amounted to a plain fade six times over. */}
        <motion.div
          initial="hidden"
          whileInView="visible"
          variants={staggerContainer}
          viewport={{ once: true }}
          className="grid gap-8 md:grid-cols-3"
        >
          {capabilityCards.map((card) => (
            <motion.div key={card.index} variants={riseIn} className={cardClassName}>
              <div className="mb-8 font-serif text-3xl italic text-primary transition-transform duration-500 group-hover:translate-x-2">
                {card.index}
              </div>
              <h3 className="mb-4 font-serif text-3xl text-foreground">{card.title}</h3>
              <p className="mb-6 font-light leading-relaxed text-muted-foreground">{card.description}</p>
              {card.relatedProject ? (
                <button
                  type="button"
                  onClick={() => onNavigate("portfolio")}
                  className="inline-flex items-center gap-2 text-sm font-light uppercase tracking-widest text-primary transition-colors hover:text-foreground"
                >
                  See it in {card.relatedProject}
                  <ArrowRight className="h-4 w-4 transition-transform duration-500 group-hover:translate-x-1" />
                </button>
              ) : null}
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};
