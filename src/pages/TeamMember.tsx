import { useParams, Link } from "react-router-dom";
import { teamMembers } from "@/lib/team-data";
import { ArrowLeft, ExternalLink } from "lucide-react";

const TeamMember = () => {
  const { memberId } = useParams();
  const member = teamMembers.find((m) => m.id === memberId);

  if (!member) {
    return (
      <div className="team-member-not-found">
        <p className="text-muted-foreground">Member not found.</p>
        <Link to="/" className="text-sm font-medium text-accent hover:underline">
          ← Back home
        </Link>
      </div>
    );
  }

  return (
    <div className="team-member-root">
      <div className="content-max section-padding w-full">
        <div className="mx-auto max-w-3xl pt-16">
          <Link to="/" className="back-link">
            <ArrowLeft size={16} /> Back to home
          </Link>

          <div className="reveal">
            <div className="mb-8 flex h-20 w-20 items-center justify-center rounded-full bg-accent/10 text-2xl font-bold text-accent">
              {member.initials}
            </div>

            <h1 className="mb-2 text-4xl font-bold leading-tight md:text-5xl">{member.name}</h1>
            <div className="mb-8 space-y-4">
              <p className="font-medium text-accent">{member.role}</p>
              {member.website && (
                <p>
                  <a
                    href={member.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="profile-external-link"
                  >
                    Profile & work
                    <ExternalLink className="h-4 w-4 opacity-70" aria-hidden />
                  </a>
                </p>
              )}
            </div>

            <blockquote className="mb-12 border-l-2 border-accent pl-6 text-lg italic leading-relaxed text-muted-foreground">
              "{member.quote}"
            </blockquote>

            <div className="space-y-8">
              <div>
                <h2 className="muted-label mb-3">About</h2>
                <p className="leading-relaxed text-foreground">{member.bio}</p>
              </div>

              <div>
                <h2 className="muted-label mb-3">Experience</h2>
                <p className="text-foreground">{member.experience}</p>
              </div>

              <div>
                <h2 className="muted-label mb-4">Skills</h2>
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
