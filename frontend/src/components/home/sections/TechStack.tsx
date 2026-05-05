import {
  SiAndroid,
  SiApple,
  SiCypress,
  SiDjango,
  SiDocker,
  SiEthereum,
  SiFlask,
  SiFlutter,
  SiGithub,
  SiGithubactions,
  SiGraphql,
  SiJest,
  SiKubernetes,
  SiLangchain,
  SiMongodb,
  SiNestjs,
  SiNextdotjs,
  SiNodedotjs,
  SiOpenai,
  SiPostgresql,
  SiPython,
  SiReact,
  SiReactquery,
  SiRedis,
  SiRust,
  SiSequelize,
  SiSocketdotio,
  SiSolidity,
  SiSolana,
  SiTypescript,
  SiVercel,
  SiWalletconnect,
} from "react-icons/si";

/** Shared sizing / hover for Simple Icons in the “Technologies We Master” row */
const TECH_ICON_CLASS = "h-9 w-9 transition-colors duration-300 hover:text-primary md:h-10 md:w-10";

export function TechStack() {
  return (
    <section className="bg-background px-6 py-24 lg:px-12">
      <div className="mx-auto max-w-7xl text-center">
        <div className="mb-12 text-sm font-light uppercase tracking-widest text-muted-foreground">
          Technologies We Master
        </div>

        <div className="mx-auto flex max-w-7xl flex-wrap justify-center gap-x-10 gap-y-8 text-muted-foreground/60">
          <SiReact className={TECH_ICON_CLASS} title="React" />
          <SiNextdotjs className={TECH_ICON_CLASS} title="Next.js" />
          <SiTypescript className={TECH_ICON_CLASS} title="TypeScript" />
          <SiNodedotjs className={TECH_ICON_CLASS} title="Node.js" />
          <SiDjango className={TECH_ICON_CLASS} title="Django" />
          <SiFlask className={TECH_ICON_CLASS} title="Flask" />
          <SiPython className={TECH_ICON_CLASS} title="Python" />
          <SiRust className={TECH_ICON_CLASS} title="Rust" />
          <SiSolidity className={TECH_ICON_CLASS} title="Solidity" />
          <SiEthereum className={TECH_ICON_CLASS} title="EVM / Ethereum" />
          <SiSolana className={TECH_ICON_CLASS} title="Solana" />
          <SiMongodb className={TECH_ICON_CLASS} title="MongoDB" />
          <SiPostgresql className={TECH_ICON_CLASS} title="PostgreSQL" />
          <SiRedis className={TECH_ICON_CLASS} title="Redis" />
          <SiGraphql className={TECH_ICON_CLASS} title="GraphQL" />
          <SiLangchain className={TECH_ICON_CLASS} title="LangChain" />
          <SiOpenai className={TECH_ICON_CLASS} title="OpenAI" />
          <SiDocker className={TECH_ICON_CLASS} title="Docker" />
          <SiAndroid className={TECH_ICON_CLASS} title="Android" />
          <SiApple className={TECH_ICON_CLASS} title="iOS / Apple" />
          <SiGithub className={TECH_ICON_CLASS} title="GitHub" />
          <SiGithubactions className={TECH_ICON_CLASS} title="GitHub Actions" />
          <SiVercel className={TECH_ICON_CLASS} title="Vercel" />
          <SiKubernetes className={TECH_ICON_CLASS} title="Kubernetes" />
          <SiFlutter className={TECH_ICON_CLASS} title="Flutter" />
          <SiWalletconnect className={TECH_ICON_CLASS} title="WalletConnect" />
          <SiCypress className={TECH_ICON_CLASS} title="Cypress" />
          <SiJest className={TECH_ICON_CLASS} title="Jest" />
          <SiNestjs className={TECH_ICON_CLASS} title="NestJS" />
          <SiSequelize className={TECH_ICON_CLASS} title="Sequelize" />
          <SiSocketdotio className={TECH_ICON_CLASS} title="Socket.IO" />
          <SiReactquery className={TECH_ICON_CLASS} title="TanStack Query" />
        </div>
      </div>
    </section>
  );
}
