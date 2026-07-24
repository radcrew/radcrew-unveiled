import { motion } from "framer-motion";
import { Clock, Layers, ShieldCheck, Users } from "lucide-react";
import { AnimatedCounter } from "../AnimatedCounter";
import { fadeIn, staggerContainer } from "../motion";

const statLabelClassName = "mt-4 text-sm font-light uppercase tracking-widest text-muted-foreground";
const statIconClassName = "mb-4 h-6 w-6 text-primary/60";

const stats = [
  { Icon: Layers, end: 40, suffix: "+", decimals: 0, label: "Projects Shipped" },
  { Icon: Users, end: 12, suffix: "+", decimals: 0, label: "Happy Clients" },
  { Icon: Clock, end: 5, suffix: "", decimals: 0, label: "Years Building" },
  { Icon: ShieldCheck, end: 99.9, suffix: "%", decimals: 1, label: "Uptime SLA" },
] as const;

export const Stats = () => {
  return (
    <section className="border-t border-border bg-background px-6 py-24 lg:px-12">
      <div className="mx-auto max-w-7xl">
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-2 gap-12 text-center md:grid-cols-4 md:divide-x md:divide-primary/15 md:text-left"
        >
          {stats.map(({ Icon, end, suffix, decimals, label }) => (
            <motion.div key={label} variants={fadeIn} className="flex flex-col items-center md:items-start md:pl-8 md:first:pl-0">
              <Icon className={statIconClassName} aria-hidden="true" />
              <AnimatedCounter end={end} suffix={suffix} decimals={decimals} />
              <div className={statLabelClassName}>{label}</div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};
