import { useParams, Link } from "react-router-dom";
import { teamMembers } from "@/lib/team-data";
import { ArrowLeft } from "lucide-react";

const TeamMember = () => {
  const { memberId } = useParams();
  const member = teamMembers.find((m) => m.id === memberId);

  if (!member) {
    return (
      <div className="min-h-screen flex items-center justify-center flex-col gap-4">
        <p className="text-muted-foreground">Member not found.</p>
        <Link to="/" className="text-accent text-sm font-medium hover:underline">← Back home</Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-24 pb-16 section-padding max-w-3xl mx-auto">
      <Link
        to="/"
        className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors mb-12"
      >
        <ArrowLeft size={16} /> Back to home
      </Link>

      <div className="reveal">
        <div className="w-20 h-20 rounded-full bg-accent/10 text-accent flex items-center justify-center text-2xl font-bold mb-8">
          {member.initials}
        </div>

        <h1 className="text-4xl md:text-5xl font-bold leading-tight mb-2">{member.name}</h1>
        <p className="text-accent font-medium mb-8">{member.role}</p>

        <blockquote className="border-l-2 border-accent pl-6 text-muted-foreground italic text-lg mb-12 leading-relaxed">
          "{member.quote}"
        </blockquote>

        <div className="space-y-8">
          <div>
            <h2 className="text-sm uppercase tracking-widest text-muted-foreground font-semibold mb-3">About</h2>
            <p className="text-foreground leading-relaxed">{member.bio}</p>
          </div>

          <div>
            <h2 className="text-sm uppercase tracking-widest text-muted-foreground font-semibold mb-3">Experience</h2>
            <p className="text-foreground">{member.experience}</p>
          </div>

          <div>
            <h2 className="text-sm uppercase tracking-widest text-muted-foreground font-semibold mb-4">Skills</h2>
            <div className="flex flex-wrap gap-2">
              {member.skills.map((skill) => (
                <span
                  key={skill}
                  className="px-3 py-1.5 text-xs font-medium rounded-full bg-secondary text-secondary-foreground"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TeamMember;
