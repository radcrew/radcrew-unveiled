import { Link, useParams } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { Reveal } from "@components/motion/Reveal";
import { SplitText } from "@components/motion/SplitText";
import { featuredProjects } from "@components/home/static-data";
import { placeholderCaseStudies } from "@components/home/placeholder-content";
import NotFound from "./NotFound";

const CaseStudy = () => {
  const { slug } = useParams<{ slug: string }>();
  const project = featuredProjects.find((p) => p.slug === slug);

  // Render 404 in place rather than redirecting, so the bad URL stays in the
  // address bar and NotFound logs the path that was actually requested.
  if (!project) return <NotFound />;

  const narrative = placeholderCaseStudies[project.slug];
  const sections = narrative
    ? [
        { heading: "The challenge", body: narrative.challenge },
        { heading: "Our approach", body: narrative.approach },
        { heading: "The outcome", body: narrative.outcome },
      ]
    : [];

  return (
    <main className="min-h-[100dvh] bg-background pb-32 pt-40">
      <div className="mx-auto max-w-7xl px-6 lg:px-12">
        <Reveal>
          <Link
            to="/work"
            className="mb-16 inline-flex items-center gap-2 text-sm font-light uppercase tracking-widest text-muted-foreground transition-colors hover:text-primary"
          >
            <ArrowLeft aria-hidden="true" className="h-4 w-4" />
            All work
          </Link>
        </Reveal>

        <header className="mb-20 border-b border-border pb-12">
          <h1 className="mb-8 font-serif text-5xl leading-tight text-foreground md:text-7xl">
            <SplitText text={project.title} />
          </h1>
          <Reveal delay={0.2}>
            <p className="max-w-3xl text-xl font-light leading-relaxed text-muted-foreground">{project.description}</p>
          </Reveal>
          <Reveal delay={0.3} className="mt-10 flex flex-wrap gap-3">
            {project.tags.map((tag) => (
              <span
                key={tag}
                className="border border-primary/30 px-4 py-2 text-xs font-light uppercase tracking-widest text-primary"
              >
                {tag}
              </span>
            ))}
          </Reveal>
        </header>

        {sections.length > 0 && (
          <div className="mb-24 grid gap-16 md:grid-cols-3">
            {sections.map((section, i) => (
              <Reveal key={section.heading} delay={i * 0.1}>
                <h2 className="mb-6 font-serif text-2xl text-foreground">{section.heading}</h2>
                <p className="font-light leading-relaxed text-muted-foreground">{section.body}</p>
              </Reveal>
            ))}
          </div>
        )}
      </div>

      {project.images && project.images.length > 0 && (
        <div className="mx-auto max-w-7xl space-y-12 px-6 lg:px-12">
          {project.images.map((src, i) => (
            <Reveal key={src}>
              <img
                src={src}
                alt={`${project.title} — screen ${i + 1}`}
                loading="lazy"
                decoding="async"
                className="w-full border border-border"
              />
            </Reveal>
          ))}
        </div>
      )}
    </main>
  );
};

export default CaseStudy;
