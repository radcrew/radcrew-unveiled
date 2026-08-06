import { motion, type Variants } from "framer-motion";
import { fadeIn } from "../motion";

const phases = [
  {
    num: "I.",
    title: "Discover",
    desc: "We map the architecture, define constraints, and build the blueprint.",
    deliverables: ["Architecture review", "Constraint map", "Scoped estimate"],
  },
  {
    num: "II.",
    title: "Build",
    desc: "Elite engineering velocity. Transparent sprints. Relentless precision.",
    deliverables: ["Weekly working demos", "Tests written alongside", "Your repo, your review process"],
  },
  {
    num: "III.",
    title: "Ship",
    desc: "Deploy to production, stabilize infrastructure, and hand off clean docs.",
    deliverables: ["Production deploy", "Runbooks and handover", "Monitoring and alerts"],
  },
  {
    num: "IV.",
    title: "Partner",
    desc: "Long-term embedded relationship to scale the product forward.",
    deliverables: ["Embedded engineers", "Roadmap input", "Migration and scaling support"],
  },
] as const;

const phaseItemVariants: Variants = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5 } },
};

const phaseContainerVariants = (delay: number): Variants => ({
  hidden: {},
  visible: { transition: { delayChildren: delay, staggerChildren: 0.12 } },
});

export const Process = () => {
  return (
    <section id="process" className="bg-background px-6 py-20 md:py-32 lg:px-12">
      <div className="mx-auto max-w-7xl">
        <motion.div initial="hidden" whileInView="visible" variants={fadeIn} viewport={{ once: true }} className="mb-24">
          <h2 className="max-w-4xl font-serif text-5xl leading-tight text-foreground md:text-7xl">
            From first call to production—and after.
          </h2>
        </motion.div>

        <div className="relative grid gap-12 pl-8 md:grid-cols-4 md:pl-0 md:pt-12">
          <div className="absolute inset-y-0 left-0 w-px bg-primary/20 md:hidden" />
          <motion.div
            initial={{ scaleY: 0 }}
            whileInView={{ scaleY: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 1.1, ease: [0.16, 1, 0.3, 1] }}
            className="absolute inset-y-0 left-0 w-px origin-top bg-primary md:hidden"
          />

          <div className="absolute inset-x-0 top-0 hidden h-px bg-primary/20 md:block" />
          <motion.div
            initial={{ scaleX: 0 }}
            whileInView={{ scaleX: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 1.1, ease: [0.16, 1, 0.3, 1] }}
            className="absolute inset-x-0 top-0 hidden h-px origin-left bg-primary md:block"
          />

          {phases.map((phase, i) => (
            <motion.div
              key={phase.num}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              variants={phaseContainerVariants(i * 0.15)}
              className="relative"
            >
              <motion.div variants={phaseItemVariants} className="mb-6 font-serif text-4xl italic text-primary">
                {phase.num}
              </motion.div>
              <motion.h4 variants={phaseItemVariants} className="mb-4 font-serif text-2xl text-foreground">
                {phase.title}
              </motion.h4>
              {/* Reserves three lines so the deliverable lists share a baseline
                  across columns whose descriptions wrap to different heights. */}
              <motion.p
                variants={phaseItemVariants}
                className="mb-6 font-light leading-relaxed text-muted-foreground md:min-h-[4.875rem]"
              >
                {phase.desc}
              </motion.p>
              <motion.ul variants={phaseItemVariants} className="space-y-2">
                {phase.deliverables.map((item) => (
                  <li key={item} className="flex gap-3 text-sm font-light text-muted-foreground">
                    <span aria-hidden="true" className="text-primary">
                      &mdash;
                    </span>
                    {item}
                  </li>
                ))}
              </motion.ul>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};
