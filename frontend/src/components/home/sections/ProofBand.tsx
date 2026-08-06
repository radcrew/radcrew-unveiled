import { Marquee } from "@components/motion/Marquee";
import { placeholderProofPoints } from "../placeholder-content";

export const ProofBand = () => {
  return (
    <section aria-label="What we are known for" className="border-y border-primary/20 bg-primary/5 py-5">
      <Marquee duration={38} reverse>
        {placeholderProofPoints.map((point) => (
          <span key={point} className="flex items-center whitespace-nowrap">
            <span className="px-8 text-sm font-light uppercase tracking-widest text-foreground/80">{point}</span>
            <span aria-hidden="true" className="text-primary/50">
              &bull;
            </span>
          </span>
        ))}
      </Marquee>
    </section>
  );
};
