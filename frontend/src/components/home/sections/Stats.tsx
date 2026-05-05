import { AnimatedCounter } from "../AnimatedCounter";

export function Stats() {
  return (
    <section className="border-t border-border bg-background px-6 py-24 lg:px-12">
      <div className="mx-auto max-w-7xl">
        <div className="grid grid-cols-2 gap-12 text-center md:grid-cols-4 md:text-left">
          <div>
            <AnimatedCounter end={40} suffix="+" />
            <div className="mt-4 text-sm font-light uppercase tracking-widest text-muted-foreground">Projects Shipped</div>
          </div>
          <div>
            <AnimatedCounter end={12} suffix="+" />
            <div className="mt-4 text-sm font-light uppercase tracking-widest text-muted-foreground">Happy Clients</div>
          </div>
          <div>
            <AnimatedCounter end={5} suffix="" />
            <div className="mt-4 text-sm font-light uppercase tracking-widest text-muted-foreground">Years Building</div>
          </div>
          <div>
            <div className="font-serif text-5xl text-foreground md:text-6xl">
              99.9<span className="ml-1 text-primary">%</span>
            </div>
            <div className="mt-4 text-sm font-light uppercase tracking-widest text-muted-foreground">Uptime SLA</div>
          </div>
        </div>
      </div>
    </section>
  );
}
