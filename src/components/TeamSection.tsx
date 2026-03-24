import { Link } from "react-router-dom";
import { ArrowUpRight } from "lucide-react";
import { useScrollReveal } from "@/hooks/useScrollReveal";
import { useTeamMembers } from "@/hooks/useTeamMembers";
import { isContentfulConfigured } from "@/lib/contentful";

const TeamSection = () => {
  const ref = useScrollReveal();
  const { data: teamMembers, isPending, isError, error } = useTeamMembers();

  const showSetupHint = !isContentfulConfigured();

  return (
    <section id="team" className="team-shell" ref={ref}>
      <div className="content-stack">
        <header className="section-block">
          <p className="kicker">The Crew</p>
          <h2 className="section-heading">Three minds, one mission.</h2>
        </header>

        {showSetupHint && (
          <p className="text-sm text-muted-foreground">
            Add <code className="rounded bg-muted px-1 py-0.5 text-xs">VITE_CONTENTFUL_SPACE_ID</code> and{" "}
            <code className="rounded bg-muted px-1 py-0.5 text-xs">VITE_CONTENTFUL_DELIVERY_TOKEN</code> to your{" "}
            <code className="rounded bg-muted px-1 py-0.5 text-xs">.env</code> to load engineers from Contentful.
          </p>
        )}

        {isPending && !showSetupHint && (
          <div className="team-grid">
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                className="team-card animate-pulse border border-border/60 bg-muted/30"
                style={{ animationDelay: `${i * 100}ms` }}
              >
                <div className="mb-4 h-14 w-14 rounded-full bg-muted" />
                <div className="mb-2 h-6 w-2/3 rounded bg-muted" />
                <div className="mb-4 h-4 w-1/2 rounded bg-muted" />
                <div className="space-y-2">
                  <div className="h-3 w-full rounded bg-muted" />
                  <div className="h-3 w-full rounded bg-muted" />
                  <div className="h-3 w-4/5 rounded bg-muted" />
                </div>
              </div>
            ))}
          </div>
        )}

        {isError && !showSetupHint && (
          <p className="text-sm text-destructive">
            {error instanceof Error ? error.message : "Could not load team from Contentful."}
          </p>
        )}

        {!isPending && !isError && teamMembers && teamMembers.length === 0 && !showSetupHint && (
          <p className="text-sm text-muted-foreground">No engineers published yet.</p>
        )}

        {!isPending && !isError && teamMembers && teamMembers.length > 0 && (
          <div className="team-grid">
            {teamMembers.map((member, i) => (
              <Link
                key={member.id}
                to={`/team/${member.id}`}
                className="group team-card"
                style={{ animationDelay: `${i * 100}ms` }}
              >
                <div className="team-avatar">{member.initials}</div>
                <h3 className="mb-1 text-xl font-bold">{member.name}</h3>
                <p className="mb-4 text-sm text-muted-foreground">{member.shortRole}</p>
                <p className="line-clamp-3 text-sm leading-relaxed text-muted-foreground">
                  {member.bio || "—"}
                </p>
                <div className="mt-6 flex items-center gap-1 text-sm font-medium text-accent opacity-0 transition-opacity duration-300 group-hover:opacity-100">
                  View profile <ArrowUpRight size={14} />
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </section>
  );
};

export default TeamSection;
