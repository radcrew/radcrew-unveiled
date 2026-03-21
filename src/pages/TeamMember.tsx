import { useParams, Link } from "react-router-dom";
import { teamMembers } from "@/lib/team-data";
import { ArrowLeft, ExternalLink } from "lucide-react";

const TeamMember = () => {
  const { memberId } = useParams();
  const member = teamMembers.find((m) => m.id === memberId);

  if (!member) {
    return (
      <div className="content-max section-padding flex min-h-screen min-h-dvh flex-col items-center justify-center gap-4">
        <p className="text-muted-foreground">Member not found.</p>
        <Link to="/" className="text-accent text-sm font-medium hover:underline">← Back home</Link>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen min-h-dvh flex-col justify-center py-10 sm:py-12 md:py-14 lg:py-16">
      <div className="content-max section-padding w-full">
        <div className="mx-auto max-w-3xl pt-16">
        <Link
          to="/"
          className="mb-12 inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
        >
          <ArrowLeft size={16} /> Back to home
        </Link>

        <div className="reveal">
        <div className="w-20 h-20 rounded-full bg-accent/10 text-accent flex items-center justify-center text-2xl font-bold mb-8">
          {member.initials}
        </div>

        <h1 className="text-4xl md:text-5xl font-bold leading-tight mb-2">{member.name}</h1>
        <div className="mb-8 space-y-4">
          <p className="text-accent font-medium">{member.role}</p>
          {member.website && (
            <p>
              <a
                href={member.website}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-sm font-medium text-foreground underline-offset-4 transition-colors hover:text-accent hover:underline"
              >
                Profile & work
                <ExternalLink className="h-4 w-4 opacity-70" aria-hidden />
              </a>
            </p>
          )}
        </div>

        <blockquote className="border-l-2 border-accent pl-6 text-muted-foreground italic text-lg mb-12 leading-relaxed">
          "{member.quote}"
        </blockquote>

          <div className="space-y-8">
            <div>
              <h2 className="mb-3 text-sm font-semibold uppercase tracking-widest text-muted-foreground">About</h2>
              <p className="leading-relaxed text-foreground">{member.bio}</p>
            </div>

            <div>
              <h2 className="mb-3 text-sm font-semibold uppercase tracking-widest text-muted-foreground">Experience</h2>
              <p className="text-foreground">{member.experience}</p>
            </div>

            <div>
              <h2 className="mb-4 text-sm font-semibold uppercase tracking-widest text-muted-foreground">Skills</h2>
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
          </div>
        </div>
        </div>
      </div>
    </div>
  );
};

export default TeamMember;
