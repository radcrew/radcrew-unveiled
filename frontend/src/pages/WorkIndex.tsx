import { Link } from "react-router-dom";
import { ArrowRight } from "lucide-react";
import { Reveal } from "@components/motion/Reveal";
import { SplitText } from "@components/motion/SplitText";
import { featuredProjects } from "@components/home/static-data";

const WorkIndex = () => {
  return (
    <main className="min-h-[100dvh] bg-background px-6 pb-32 pt-40 lg:px-12">
      <div className="mx-auto max-w-7xl">
        <header className="mb-24 border-b border-border pb-12">
          <h1 className="mb-8 font-serif text-5xl text-foreground md:text-7xl">
            <SplitText text="Selected Work" />
          </h1>
          <Reveal delay={0.2}>
            <p className="max-w-2xl text-xl font-light leading-relaxed text-muted-foreground">
              Products we designed, built and shipped. Each one is still in production.
            </p>
          </Reveal>
        </header>

        <div className="space-y-24">
          {featuredProjects.map((project, i) => (
            <Reveal key={project.slug} delay={i * 0.08}>
              <Link
                to={`/work/${project.slug}`}
                className="group grid items-center gap-12 md:grid-cols-12 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-4 focus-visible:ring-offset-background"
              >
                <div className="md:col-span-7">
                  <div className="relative aspect-[2/1] overflow-hidden border border-border bg-muted">
                    {project.images?.[0] ? (
                      <img
                        src={project.images[0]}
                        alt=""
                        loading="lazy"
                        decoding="async"
                        className="h-full w-full object-cover transition-transform duration-1000 group-hover:scale-[1.03]"
                      />
                    ) : null}
                  </div>
                </div>
                <div className="md:col-span-5">
                  <h2 className="mb-6 font-serif text-4xl text-foreground transition-colors duration-500 group-hover:text-primary md:text-5xl">
                    {project.title}
                  </h2>
                  <p className="mb-8 font-light leading-relaxed text-muted-foreground">{project.description}</p>
                  <span className="inline-flex items-center gap-2 text-sm font-light uppercase tracking-widest text-primary">
                    Read the case study
                    <ArrowRight
                      aria-hidden="true"
                      className="h-4 w-4 transition-transform duration-500 group-hover:translate-x-1"
                    />
                  </span>
                </div>
              </Link>
            </Reveal>
          ))}
        </div>
      </div>
    </main>
  );
};

export default WorkIndex;
