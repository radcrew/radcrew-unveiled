import { Link } from "react-router-dom";
import { ArrowUpRight } from "lucide-react";
import { teamMembers } from "@/lib/team-data";
import { useScrollReveal } from "@/hooks/useScrollReveal";

const TeamSection = () => {
  const ref = useScrollReveal();

  return (
    <section
      id="team"
      className="flex min-h-screen min-h-dvh flex-col justify-center section-padding py-10 sm:py-12 md:py-14 lg:py-16"
      ref={ref}
    >
      <div className="content-max flex flex-col gap-10 md:gap-12 lg:gap-14">
        <header className="shrink-0 space-y-3 md:space-y-4">
          <p className="text-sm font-semibold uppercase tracking-widest text-accent">The Crew</p>
          <h2 className="text-3xl font-bold md:text-4xl">Three minds, one mission.</h2>
        </header>

        <div className="grid shrink-0 gap-6 md:grid-cols-3 md:gap-8">
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
      </div>
    </section>
  );
};

export default TeamSection;
