import { motion, type Variants } from "framer-motion";
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

const techIcons = [
  { Icon: SiReact, title: "React" },
  { Icon: SiNextdotjs, title: "Next.js" },
  { Icon: SiTypescript, title: "TypeScript" },
  { Icon: SiNodedotjs, title: "Node.js" },
  { Icon: SiDjango, title: "Django" },
  { Icon: SiFlask, title: "Flask" },
  { Icon: SiPython, title: "Python" },
  { Icon: SiRust, title: "Rust" },
  { Icon: SiSolidity, title: "Solidity" },
  { Icon: SiEthereum, title: "EVM / Ethereum" },
  { Icon: SiSolana, title: "Solana" },
  { Icon: SiMongodb, title: "MongoDB" },
  { Icon: SiPostgresql, title: "PostgreSQL" },
  { Icon: SiRedis, title: "Redis" },
  { Icon: SiGraphql, title: "GraphQL" },
  { Icon: SiLangchain, title: "LangChain" },
  { Icon: SiOpenai, title: "OpenAI" },
  { Icon: SiDocker, title: "Docker" },
  { Icon: SiAndroid, title: "Android" },
  { Icon: SiApple, title: "iOS / Apple" },
  { Icon: SiGithub, title: "GitHub" },
  { Icon: SiGithubactions, title: "GitHub Actions" },
  { Icon: SiVercel, title: "Vercel" },
  { Icon: SiKubernetes, title: "Kubernetes" },
  { Icon: SiFlutter, title: "Flutter" },
  { Icon: SiWalletconnect, title: "WalletConnect" },
  { Icon: SiCypress, title: "Cypress" },
  { Icon: SiJest, title: "Jest" },
  { Icon: SiNestjs, title: "NestJS" },
  { Icon: SiSequelize, title: "Sequelize" },
  { Icon: SiSocketdotio, title: "Socket.IO" },
  { Icon: SiReactquery, title: "TanStack Query" },
] as const;

const iconRowVariants: Variants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.015 } },
};

const iconVariants: Variants = {
  hidden: { opacity: 0, y: 10 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4 } },
};

export const TechStack = () => {
  return (
    <section className="bg-background px-6 py-24 lg:px-12">
      <div className="mx-auto max-w-7xl text-center">
        <div className="mb-12 text-sm font-light uppercase tracking-widest text-muted-foreground">
          Technologies We Master
        </div>

        <motion.div
          initial="hidden"
          whileInView="visible"
          variants={iconRowVariants}
          viewport={{ once: true }}
          className="mx-auto flex max-w-7xl flex-wrap justify-center gap-x-10 gap-y-8 text-muted-foreground/60"
        >
          {techIcons.map(({ Icon, title }) => (
            <motion.span key={title} variants={iconVariants}>
              <Icon className={TECH_ICON_CLASS} title={title} />
            </motion.span>
          ))}
        </motion.div>
      </div>
    </section>
  );
};
