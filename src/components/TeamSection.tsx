import { Link } from "react-router-dom";
import { ArrowUpRight } from "lucide-react";
import { teamMembers } from "@/lib/team-data";
import { useScrollReveal } from "@/hooks/useScrollReveal";

const TeamSection = () => {
  const ref = useScrollReveal();

  return (
    <section id="team" className="team-shell" ref={ref}>
      <div className="content-stack">
        <header className="section-block">
          <p className="kicker">The Crew</p>
          <h2 className="section-heading">Three minds, one mission.</h2>
        </header>

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
              <p className="line-clamp-3 text-sm leading-relaxed text-muted-foreground">{member.bio}</p>
              <div className="mt-6 flex items-center gap-1 text-sm font-medium text-accent opacity-0 transition-opacity duration-300 group-hover:opacity-100">
                View profile <ArrowUpRight size={14} />
              </div>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
};

export default TeamSection;
