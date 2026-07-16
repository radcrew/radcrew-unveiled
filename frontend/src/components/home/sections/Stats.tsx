import { motion } from "framer-motion";
import { AnimatedCounter } from "../AnimatedCounter";
import { fadeIn, staggerContainer } from "../motion";

const statLabelClassName = "mt-4 text-sm font-light uppercase tracking-widest text-muted-foreground";

export const Stats = () => {
  return (
    <section className="border-t border-border bg-background px-6 py-24 lg:px-12">
      <div className="mx-auto max-w-7xl">
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-2 gap-12 text-center md:grid-cols-4 md:text-left"
        >
          <motion.div variants={fadeIn}>
            <AnimatedCounter end={40} suffix="+" />
            <div className={statLabelClassName}>Projects Shipped</div>
          </motion.div>
          <motion.div variants={fadeIn}>
            <AnimatedCounter end={12} suffix="+" />
            <div className={statLabelClassName}>Happy Clients</div>
          </motion.div>
          <motion.div variants={fadeIn}>
            <AnimatedCounter end={5} suffix="" />
            <div className={statLabelClassName}>Years Building</div>
          </motion.div>
          <motion.div variants={fadeIn}>
            <AnimatedCounter end={99.9} suffix="%" decimals={1} />
            <div className={statLabelClassName}>Uptime SLA</div>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
};
