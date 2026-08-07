import { Link, useParams } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { Reveal } from "@components/motion/Reveal";
import { placeholderJournal } from "@components/home/placeholder-content";
import { formatPostDate } from "@/lib/format-date";
import NotFound from "./NotFound";

const JournalPost = () => {
  const { slug } = useParams<{ slug: string }>();
  const post = placeholderJournal.find((p) => p.slug === slug);

  if (!post) return <NotFound />;

  return (
    <main className="min-h-[100dvh] bg-background px-6 pb-32 pt-40 lg:px-12">
      <article className="mx-auto max-w-2xl">
        <Reveal>
          <Link
            to="/journal"
            className="mb-16 inline-flex items-center gap-2 text-sm font-light uppercase tracking-widest text-muted-foreground transition-colors hover:text-primary"
          >
            <ArrowLeft aria-hidden="true" className="h-4 w-4" />
            All posts
          </Link>
        </Reveal>

        <header className="mb-16">
          <div className="mb-6 flex flex-wrap items-center gap-4 text-xs font-light uppercase tracking-widest">
            <span className="text-primary">{post.tag}</span>
            <time dateTime={post.date} className="text-muted-foreground">
              {formatPostDate(post.date)}
            </time>
            <span className="text-muted-foreground">{post.readingTime}</span>
          </div>
          <h1 className="font-serif text-4xl leading-tight text-foreground md:text-6xl">{post.title}</h1>
        </header>

        <div className="space-y-8">
          {post.body.map((paragraph) => (
            <p key={paragraph.slice(0, 48)} className="text-lg font-light leading-relaxed text-muted-foreground">
              {paragraph}
            </p>
          ))}
        </div>
      </article>
    </main>
  );
};

export default JournalPost;
