import { Marquee } from "@components/motion/Marquee";
import { Reveal } from "@components/motion/Reveal";
import { placeholderClients } from "../placeholder-content";

export const Clients = () => {
  return (
    <section className="bg-background py-20">
      <Reveal className="mb-14 px-6 text-center lg:px-12">
        <p className="text-sm font-light uppercase tracking-widest text-muted-foreground">
          Trusted by teams shipping in production
        </p>
      </Reveal>

      {/* Wordmarks, not images: a fabricated logo file would read as a real endorsement. */}
      <Marquee duration={45} className="[mask-image:linear-gradient(to_right,transparent,black_8%,black_92%,transparent)]">
        {placeholderClients.map((client) => (
          <span key={client.name} className="flex items-baseline gap-3 px-10">
            <span className="whitespace-nowrap font-serif text-3xl text-foreground/70 md:text-4xl">{client.name}</span>
            <span className="whitespace-nowrap text-[0.625rem] font-light uppercase tracking-widest text-primary/60">
              {client.sector}
            </span>
          </span>
        ))}
      </Marquee>
    </section>
  );
};
