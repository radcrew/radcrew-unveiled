import { useParams, Link } from "react-router-dom";
import { ArrowLeft, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useEngineerMember } from "@/hooks/useEngineerMember";
import { isContentfulConfigured } from "@/lib/contentful";

const TeamMember = () => {
  const { memberId } = useParams();
  const { data: member, isPending, isError, error } = useEngineerMember(memberId);

  if (!isContentfulConfigured()) {
    return (
      <div className="team-member-not-found">
        <p className="text-muted-foreground">Contentful is not configured.</p>
        <Button variant="link" asChild className="h-auto p-0 text-sm font-medium text-accent">
          <Link to="/">← Back home</Link>
        </Button>
      </div>
    );
  }

  if (isPending) {
    return (
      <div className="team-member-root">
        <div className="content-max section-padding w-full">
          <div className="w-full max-w-3xl animate-pulse pt-16 text-left">
            <div className="mb-8 h-5 w-32 rounded bg-muted" />
            <div className="mb-8 h-20 w-20 rounded-full bg-muted" />
            <div className="mb-4 h-10 w-3/4 rounded bg-muted" />
            <div className="mb-8 h-5 w-48 rounded bg-muted" />
            <div className="space-y-3">
              <div className="h-4 w-full rounded bg-muted" />
              <div className="h-4 w-full rounded bg-muted" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="team-member-not-found">
        <p className="text-destructive">{error instanceof Error ? error.message : "Something went wrong."}</p>
        <Button variant="link" asChild className="h-auto p-0 text-sm font-medium text-accent">
          <Link to="/">← Back home</Link>
        </Button>
      </div>
    );
  }

  if (!member) {
    return (
      <div className="team-member-not-found">
        <p className="text-muted-foreground">Member not found.</p>
        <Button variant="link" asChild className="h-auto p-0 text-sm font-medium text-accent">
          <Link to="/">← Back home</Link>
        </Button>
      </div>
    );
  }

  const hasQuote = Boolean(member.quote?.trim());
  const hasExperience = Boolean(member.experience?.trim());
  const hasSkills = member.skills.length > 0;

  return (
    <div className="team-member-root">
      <div className="content-max section-padding w-full">
        <div className="w-full max-w-3xl pt-16 text-left">
          <Button variant="ghost" asChild className="back-link h-auto justify-start gap-2 px-0 font-normal hover:bg-transparent">
            <Link to="/">
              <ArrowLeft size={16} /> Back to home
            </Link>
          </Button>

          <div className="reveal">
            <div className="mb-8 flex h-20 w-20 items-center justify-center rounded-full bg-accent/10 text-2xl font-bold text-accent">
              {member.initials}
            </div>

            <h1 className="mb-2 text-3xl font-bold leading-tight md:text-4xl">{member.name}</h1>
            <div className="mb-8 space-y-4">
              <p className="font-medium text-accent">{member.role}</p>
              {member.website && (
                <p>
                  <Button variant="link" asChild className="profile-external-link h-auto gap-2 p-0">
                    <a href={member.website} target="_blank" rel="noopener noreferrer">
                      Profile & work
                      <ExternalLink className="h-4 w-4 opacity-70" aria-hidden />
                    </a>
                  </Button>
                </p>
              )}
            </div>

            {hasQuote && (
              <blockquote className="mb-12 border-l-2 border-accent pl-6 text-lg italic leading-relaxed text-muted-foreground">
                &ldquo;{member.quote}&rdquo;
              </blockquote>
            )}

            <div className="space-y-8 text-left">
              <div>
                <h2 className="kicker mb-3">About</h2>
                <p className="leading-relaxed text-foreground">{member.bio || "—"}</p>
              </div>

              {hasExperience && (
                <div>
                  <h2 className="kicker mb-3">Experience</h2>
                  <p className="text-foreground">{member.experience}</p>
                </div>
              )}

              {hasSkills && (
                <div>
                  <h2 className="kicker mb-4">Skills</h2>
                  <div className="flex flex-wrap gap-2">
                    {member.skills.map((skill) => (
                      <span
                        key={skill}
                        className="rounded-full bg-secondary px-3 py-1.5 text-xs font-medium text-secondary-foreground"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TeamMember;
