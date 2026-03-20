export interface TeamMember {
  id: string;
  name: string;
  role: string;
  shortRole: string;
  bio: string;
  skills: string[];
  experience: string;
  quote: string;
  initials: string;
}

export const teamMembers: TeamMember[] = [
  {
    id: "alex-mercer",
    name: "Alex Mercer",
    role: "Lead Engineer",
    shortRole: "Lead",
    bio: "With over 12 years in software architecture, Alex leads RadCrew's technical vision. From distributed systems at scale to developer tooling, he architects solutions that are built to last. He's shipped products used by millions and mentors the next generation of engineers.",
    skills: ["System Architecture", "DevOps & CI/CD", "TypeScript", "Rust", "Cloud Infrastructure", "Team Leadership"],
    experience: "12+ years",
    quote: "Great engineering isn't about complexity — it's about making the complex feel inevitable.",
    initials: "AM",
  },
  {
    id: "kai-nakamura",
    name: "Kai Nakamura",
    role: "Web3 / Blockchain / AI Developer",
    shortRole: "Web3 & AI",
    bio: "Kai bridges the decentralized web with intelligent systems. He's built DeFi protocols, NFT platforms, and on-chain AI agents. His deep understanding of smart contracts, consensus mechanisms, and machine learning makes him the rare engineer who can work across both paradigms.",
    skills: ["Solidity & Smart Contracts", "DeFi Protocols", "Machine Learning", "Python", "Ethereum & L2s", "Zero-Knowledge Proofs"],
    experience: "8+ years",
    quote: "The future is on-chain and autonomous — I'm here to build it.",
    initials: "KN",
  },
  {
    id: "sable-ortiz",
    name: "Sable Ortiz",
    role: "AI / LLM / Full-Stack Developer",
    shortRole: "AI & Full-Stack",
    bio: "Sable turns large language models into production-grade products. From fine-tuning open-source models to building end-to-end full-stack applications powered by AI, she ships fast and iterates faster. Her work spans RAG pipelines, agent frameworks, and polished user interfaces.",
    skills: ["LLM Fine-tuning", "RAG & Agents", "React & Next.js", "Node.js", "PostgreSQL", "Product Design"],
    experience: "7+ years",
    quote: "AI is only as good as the product it powers.",
    initials: "SO",
  },
];
