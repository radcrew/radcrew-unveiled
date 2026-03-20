import { Link } from "react-router-dom";
import { ArrowUpRight } from "lucide-react";
import { teamMembers } from "@/lib/team-data";
import { useScrollReveal } from "@/hooks/useScrollReveal";

const TeamSection = () => {
  const ref = useScrollReveal();

  return (
    <section id="team" className="py-24 md:py-32 section-padding max-w-6xl mx-auto" ref={ref}>
      <p className="text-accent font-semibold text-sm uppercase tracking-widest mb-3">The Crew</p>
      <h2 className="text-3xl md:text-4xl font-bold mb-16">Three minds, one mission.</h2>

      <div className="grid gap-6 md:grid-cols-3">
        {teamMembers.map((member, i) => (
          <Link
            key={member.id}
            to={`/team/${member.id}`}
            className="group relative bg-card rounded-lg p-8 border border-border hover:border-accent/40 transition-all duration-300 hover:shadow-lg hover:shadow-accent/5 active:scale-[0.98]"
            style={{ animationDelay: `${i * 100}ms` }}
          >
            <div className="w-14 h-14 rounded-full bg-accent/10 text-accent flex items-center justify-center text-lg font-bold mb-6">
              {member.initials}
            </div>
            <h3 className="text-xl font-bold mb-1">{member.name}</h3>
            <p className="text-muted-foreground text-sm mb-4">{member.shortRole}</p>
            <p className="text-muted-foreground text-sm leading-relaxed line-clamp-3">{member.bio}</p>
            <div className="mt-6 flex items-center gap-1 text-accent text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-300">
              View profile <ArrowUpRight size={14} />
            </div>
          </Link>
        ))}
      </div>
    </section>
  );
};

export default TeamSection;
