import { motion } from "framer-motion";
import { teamMembers } from "../static-data";
import { fadeIn } from "../motion";

export function Team() {
  return (
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
          {teamMembers.map((member, i) => (
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
  );
}
