import { Parallax } from "@components/motion/Parallax";
import { Reveal } from "@components/motion/Reveal";
import { placeholderSpotlight } from "../placeholder-content";
import { Grain } from "../Grain";

export const Spotlight = () => {
  const { client, title, summary, metrics } = placeholderSpotlight;

  return (
    <section className="relative overflow-hidden bg-foreground px-6 py-20 text-background antialiased md:py-32 lg:px-12">
      <Grain />
      <div className="relative z-10 mx-auto grid max-w-7xl gap-16 md:grid-cols-12">
        <div className="md:col-span-6">
          <Reveal>
            <p className="mb-8 text-sm font-light uppercase tracking-widest text-background/50">
              Case study &mdash; {client}
            </p>
            <h2 className="mb-8 font-serif text-4xl leading-tight md:text-6xl">{title}</h2>
            <p className="max-w-xl text-lg font-light leading-relaxed text-background/70">{summary}</p>
          </Reveal>
        </div>

        <div className="md:col-span-6">
          <Parallax distance={40}>
            <dl className="grid grid-cols-2 gap-x-8 gap-y-14">
              {/* `flex-col-reverse` shows the value above its label while the DOM keeps
                  the label first, so the pair still reads as "label: value". */}
              {metrics.map((metric, i) => (
                <Reveal key={metric.label} delay={i * 0.08} className="flex flex-col-reverse">
                  <dt className="mt-4 text-sm font-light uppercase tracking-widest text-background/50">
                    {metric.label}
                  </dt>
                  <dd className="font-serif text-5xl text-background md:text-6xl">{metric.value}</dd>
                </Reveal>
              ))}
            </dl>
          </Parallax>
        </div>
      </div>
    </section>
  );
};
