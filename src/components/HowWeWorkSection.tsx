import { Search, Hammer, Rocket, Handshake } from "lucide-react";
import { useScrollReveal } from "@/hooks/useScrollReveal";

const steps = [
  {
    icon: Search,
    phase: "Discover",
    detail:
      "We align on outcomes, constraints, and risk—then propose a thin slice to validate architecture and UX early.",
  },
  {
    icon: Hammer,
    phase: "Build",
    detail:
      "Short cycles with visible progress: trunk-based flow, reviews, and demos so stakeholders aren’t guessing what’s shipping.",
  },
  {
    icon: Rocket,
    phase: "Ship",
    detail:
      "Hardening, observability, and handoff-ready docs. We care about launch day and the week after, not just the merge.",
  },
  {
    icon: Handshake,
    phase: "Partner",
    detail:
      "Stay for a phase-two roadmap or transition cleanly to your team. No black boxes—knowledge lives in the repo and runbooks.",
  },
];

const HowWeWorkSection = () => {
  const ref = useScrollReveal();

  return (
    <section id="how-we-work" className="py-24 md:py-32 section-padding" ref={ref}>
      <div className="mx-auto max-w-6xl">
        <p className="mb-3 text-sm font-semibold uppercase tracking-widest text-accent">How we work</p>
        <h2 className="mb-4 max-w-2xl text-3xl font-bold md:text-4xl">From first call to production—and after.</h2>
        <p className="mb-16 max-w-2xl text-lg text-muted-foreground leading-relaxed">
          A straightforward rhythm that keeps scope honest and velocity high, whether we’re shipping a web app, a protocol touchpoint, or AI features.
        </p>

        <ol className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
          {steps.map(({ icon: Icon, phase, detail }, i) => (
            <li key={phase} className="relative">
              <div className="mb-4 flex items-center gap-3">
                <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-accent/10 text-sm font-bold text-accent">
                  {i + 1}
                </span>
                <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-border bg-card text-accent">
                  <Icon className="h-5 w-5" strokeWidth={1.5} />
                </div>
              </div>
              <h3 className="mb-2 text-lg font-bold">{phase}</h3>
              <p className="text-sm leading-relaxed text-muted-foreground">{detail}</p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
};

export default HowWeWorkSection;
