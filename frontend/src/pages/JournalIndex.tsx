import { Link } from "react-router-dom";
import { ArrowRight } from "lucide-react";
import { Reveal } from "@components/motion/Reveal";
import { SplitText } from "@components/motion/SplitText";
import { placeholderJournal } from "@components/home/placeholder-content";
import { formatPostDate } from "@/lib/format-date";

export const JournalIndex = () => {
  return (
    <main className="min-h-[100dvh] bg-background px-6 pb-32 pt-40 lg:px-12">
      <div className="mx-auto max-w-4xl">
        <header className="mb-20 border-b border-border pb-12">
          <h1 className="mb-8 font-serif text-5xl text-foreground md:text-7xl">
            <SplitText text="Journal" />
          </h1>
          <Reveal delay={0.2}>
            <p className="max-w-2xl text-xl font-light leading-relaxed text-muted-foreground">
              Notes from the work, not the marketing.
            </p>
          </Reveal>
        </header>

        <div className="divide-y divide-border">
          {placeholderJournal.map((post, i) => (
            <Reveal key={post.slug} delay={i * 0.08}>
              <Link
                to={`/journal/${post.slug}`}
                className="group block py-12 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-4 focus-visible:ring-offset-background"
              >
                <div className="mb-4 flex flex-wrap items-center gap-4 text-xs font-light uppercase tracking-widest">
                  <span className="text-primary">{post.tag}</span>
                  <time dateTime={post.date} className="text-muted-foreground">
                    {formatPostDate(post.date)}
                  </time>
                  <span className="text-muted-foreground">{post.readingTime}</span>
                </div>
                <h2 className="mb-4 font-serif text-3xl leading-snug text-foreground transition-colors duration-500 group-hover:text-primary md:text-4xl">
                  {post.title}
                </h2>
                <p className="mb-6 font-light leading-relaxed text-muted-foreground">{post.excerpt}</p>
                <span className="inline-flex items-center gap-2 text-sm font-light uppercase tracking-widest text-primary">
                  Read
                  <ArrowRight
                    aria-hidden="true"
                    className="h-4 w-4 transition-transform duration-500 group-hover:translate-x-1"
                  />
                </span>
              </Link>
            </Reveal>
          ))}
        </div>
      </div>
    </main>
  );
};
