import { Link } from "react-router-dom";
import { ArrowRight } from "lucide-react";
import { Reveal } from "@components/motion/Reveal";
import { placeholderJournal } from "../placeholder-content";
import { formatPostDate } from "@/lib/format-date";

export const Journal = () => {
  return (
    <section id="journal" className="border-t border-border bg-background px-6 py-20 md:py-32 lg:px-12">
      <div className="mx-auto max-w-7xl">
        <Reveal className="mb-20 flex flex-col items-baseline justify-between gap-6 border-b border-border pb-8 md:flex-row">
          <h2 className="font-serif text-5xl text-foreground md:text-7xl">Journal</h2>
          <Link
            to="/journal"
            className="text-lg font-light text-muted-foreground transition-colors hover:text-primary"
          >
            All posts
          </Link>
        </Reveal>

        <div className="grid gap-12 md:grid-cols-3">
          {placeholderJournal.map((post, i) => (
            <Reveal key={post.slug} delay={i * 0.1}>
              <Link
                to={`/journal/${post.slug}`}
                className="group flex h-full flex-col border-t border-primary/20 pt-8 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-4 focus-visible:ring-offset-background"
              >
                <div className="mb-6 flex items-center gap-4 text-xs font-light uppercase tracking-widest">
                  <span className="text-primary">{post.tag}</span>
                  <span className="text-muted-foreground">{post.readingTime}</span>
                </div>
                <h3 className="mb-4 font-serif text-2xl leading-snug text-foreground transition-colors duration-500 group-hover:text-primary md:text-3xl">
                  {post.title}
                </h3>
                <p className="mb-8 flex-1 font-light leading-relaxed text-muted-foreground">{post.excerpt}</p>
                <div className="flex items-center justify-between">
                  <time dateTime={post.date} className="text-sm font-light text-muted-foreground">
                    {formatPostDate(post.date)}
                  </time>
                  <ArrowRight
                    aria-hidden="true"
                    className="h-4 w-4 text-primary transition-transform duration-500 group-hover:translate-x-1"
                  />
                </div>
              </Link>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
};
