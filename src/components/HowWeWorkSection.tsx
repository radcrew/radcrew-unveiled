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
    <section
      id="how-we-work"
      className="flex min-h-screen min-h-dvh flex-col justify-center section-padding py-10 sm:py-12 md:py-14 lg:py-16"
      ref={ref}
    >
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-10 md:gap-12 lg:gap-14 xl:gap-16">
        <header className="shrink-0 space-y-3 md:space-y-4">
          <p className="text-sm font-semibold uppercase tracking-widest text-accent">How we work</p>
          <h2 className="max-w-2xl text-3xl font-bold md:text-4xl lg:max-w-3xl">
            From first call to production—and after.
          </h2>
          <p className="max-w-2xl text-base leading-relaxed text-muted-foreground md:text-lg lg:max-w-3xl">
            A straightforward rhythm that keeps scope honest and velocity high, whether we’re shipping a web app, a
            protocol touchpoint, or AI features.
          </p>
        </header>

        <ol className="grid grid-cols-1 gap-8 sm:grid-cols-2 sm:gap-x-8 sm:gap-y-10 lg:grid-cols-4 lg:gap-6 lg:gap-y-8 xl:gap-8">
          {steps.map(({ icon: Icon, phase, detail }, i) => (
            <li key={phase} className="relative flex min-h-0 flex-col">
              <div className="mb-4 flex flex-wrap items-center gap-3">
                <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-accent/10 text-sm font-bold text-accent">
                  {i + 1}
                </span>
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-border bg-card text-accent">
                  <Icon className="h-5 w-5" strokeWidth={1.5} />
                </div>
              </div>
              <h3 className="mb-2 text-lg font-bold">{phase}</h3>
              <p className="flex-1 text-sm leading-relaxed text-muted-foreground">{detail}</p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
};

export default HowWeWorkSection;
