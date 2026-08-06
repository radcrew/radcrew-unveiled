import reImg1 from "@/assets/portfolio/real-estate-consultant/Screenshot_1.webp";
import reImg2 from "@/assets/portfolio/real-estate-consultant/Screenshot_2.webp";
import reImg3 from "@/assets/portfolio/real-estate-consultant/Screenshot_3.webp";
import reImg4 from "@/assets/portfolio/real-estate-consultant/Screenshot_4.webp";
import reImg5 from "@/assets/portfolio/real-estate-consultant/Screenshot_5.webp";
import reImg6 from "@/assets/portfolio/real-estate-consultant/Screenshot_6.webp";
import reImg7 from "@/assets/portfolio/real-estate-consultant/Screenshot_7.webp";
import cryptoPetsImg1 from "@/assets/portfolio/cryptopets/Screenshot_1.webp";
import cryptoPetsImg2 from "@/assets/portfolio/cryptopets/Screenshot_2.webp";
import cryptoPetsImg3 from "@/assets/portfolio/cryptopets/Screenshot_3.webp";
import cryptoPetsImg4 from "@/assets/portfolio/cryptopets/Screenshot_4.webp";
import cryptoPetsImg5 from "@/assets/portfolio/cryptopets/Screenshot_5.webp";
import cryptoPetsImg6 from "@/assets/portfolio/cryptopets/Screenshot_6.webp";
import cryptoPetsImg7 from "@/assets/portfolio/cryptopets/Screenshot_7.webp";
import cryptoPetsImg8 from "@/assets/portfolio/cryptopets/Screenshot_8.webp";
import cryptoPetsImg9 from "@/assets/portfolio/cryptopets/Screenshot_9.webp";
import cryptoPetsImg10 from "@/assets/portfolio/cryptopets/Screenshot_10.webp";
import forImg1 from "@/assets/portfolio/forgeng/Screenshot_1.webp";
import forImg2 from "@/assets/portfolio/forgeng/Screenshot_2.webp";
import forImg3 from "@/assets/portfolio/forgeng/Screenshot_3.webp";
import forImg4 from "@/assets/portfolio/forgeng/Screenshot_4.webp";
import forImg5 from "@/assets/portfolio/forgeng/Screenshot_5.webp";
import forImg6 from "@/assets/portfolio/forgeng/Screenshot_6.webp";
import forImg7 from "@/assets/portfolio/forgeng/Screenshot_7.webp";
import forImg8 from "@/assets/portfolio/forgeng/Screenshot_8.webp";

export type FeaturedProject = {
  title: string;
  description: string;
  tags: string[];
  image?: string;
  images?: string[];
};

export const featuredProjects: FeaturedProject[] = [
  {
    title: "Real Estate Consultant",
    description:
      "Client-facing discovery and advisory experience: property search, market context, and guided consultation flows with a polished, trustworthy UI.",
    images: [reImg1, reImg2, reImg3, reImg4, reImg5, reImg6, reImg7],
    tags: ["React", "Next.js", "Product UI", "LLM", "Fastapi", "PostgreSQL", "Prisma", "MicroService", "Github-Actions"],
  },
  {
    title: "CryptoPets",
    description:
      "Collectible pet experience on-chain: minting, trading, and profile flows with a bright, approachable UI built for mainstream Web3 onboarding.",
    images: [
      cryptoPetsImg1,
      cryptoPetsImg2,
      cryptoPetsImg3,
      cryptoPetsImg4,
      cryptoPetsImg5,
      cryptoPetsImg6,
      cryptoPetsImg7,
      cryptoPetsImg8,
      cryptoPetsImg9,
      cryptoPetsImg10,
    ],
    tags: ["React", "Web3", "NFTs", "GraphQL", "Helius", "Agentic-AI", "grpc", "React-Native", "SubGraph", "Ethereum", "Solana", "HuggingFace", "Zod", "GoLang", "Redis", "PostgreSQL"],
  },
  {
    title: "Forgeng",
    description:
      "Internal platform for developer productivity: CI/CD orchestration, service templates, and observability tooling to accelerate delivery.",
    images: [forImg1, forImg2, forImg3, forImg4, forImg5, forImg6, forImg7, forImg8],
    tags: ["TypeScript", "Node.js", "Kubernetes", "CI/CD", "Observability", "NestJS", "Passport", "PostgreSQL", "Shadcn-UI", "tailwindcss", "vitest", "NextJS", "Prisma"],
  }
];

export const faqs = [
  {
    question: "What size projects do you take on?",
    answer:
      "We partner with startups and scale-ups on projects from 3-month MVPs to multi-year embedded engagements. Quality over quantity.",
  },
  {
    question: "Do you work on fixed-price or time-and-materials contracts?",
    answer: "Both. We'll recommend the right model based on your project's scope and certainty.",
  },
  {
    question: "How quickly can you start?",
    answer: "Typically within 2 weeks of signing. We keep capacity deliberately limited to ensure exceptional execution.",
  },
  {
    question: "Do you offer post-launch support?",
    answer:
      "Yes. Our Partner phase is an ongoing embedded relationship, not just a maintenance contract. We stay and scale with you.",
  },
  {
    question: "What makes radcrew different?",
    answer: "Senior talent only. No handoffs to juniors. The people you meet are the people who build. Meticulous execution.",
  },
  {
    question: "Who actually writes the code?",
    answer:
      "The engineers you meet in the first call. We do not staff a pitch with seniors and deliver with juniors, and we do not subcontract work out.",
  },
  {
    question: "Can you work inside our existing codebase and process?",
    answer:
      "Yes. Most engagements start in a repo someone else wrote. We join your standups, your review process, and your branching model rather than asking you to adopt ours.",
  },
  {
    question: "What happens if we need to pause or stop?",
    answer:
      "You can stop at a sprint boundary. There is no lock-in clause, and everything we have built plus the documentation for it is yours on the way out.",
  },
];

