import { motion } from "framer-motion";
import { fadeIn } from "../motion";

const phases = [
  { num: "I.", title: "Discover", desc: "We map the architecture, define constraints, and build the blueprint." },
  { num: "II.", title: "Build", desc: "Elite engineering velocity. Transparent sprints. Relentless precision." },
  { num: "III.", title: "Ship", desc: "Deploy to production, stabilize infrastructure, and hand off clean docs." },
  { num: "IV.", title: "Partner", desc: "Long-term embedded relationship to scale the product forward." },
] as const;

export const Process = () => {
  return (
    <section id="process" className="border-t border-border bg-background px-6 py-32 lg:px-12">
      <div className="mx-auto max-w-7xl">
        <motion.div initial="hidden" whileInView="visible" variants={fadeIn} viewport={{ once: true }} className="mb-24">
          <h2 className="max-w-4xl font-serif text-5xl leading-tight text-foreground md:text-7xl">
            From first call to production—and after.
          </h2>
        </motion.div>

        <div className="grid gap-12 border-l border-primary/20 pl-8 md:grid-cols-4 md:border-l-0 md:border-t md:border-primary/20 md:pl-0 md:pt-12">
          {phases.map((phase, i) => (
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
  );
};
