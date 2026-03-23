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
    <section id="how-we-work" className="how-shell" ref={ref}>
      <div className="content-stack-wide">
        <header className="section-block">
          <p className="kicker">How we work</p>
          <h2 className="section-heading max-w-2xl lg:max-w-3xl">From first call to production—and after.</h2>
          <p className="section-prose">
            A straightforward rhythm that keeps scope honest and velocity high, whether we’re shipping a web app, a
            protocol touchpoint, or AI features.
          </p>
        </header>

        <ol className="how-step-grid">
          {steps.map(({ icon: Icon, phase, detail }, i) => (
            <li key={phase} className="relative flex min-h-0 flex-col">
              <div className="mb-4 flex flex-wrap items-center gap-3">
                <span className="step-num">{i + 1}</span>
                <div className="step-icon">
                  <Icon className="h-5 w-5" strokeWidth={1.5} />
                </div>
              </div>
              <h3 className="mb-2 text-lg font-bold">{phase}</h3>
              <p className="muted-p flex-1">{detail}</p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
};

export default HowWeWorkSection;
