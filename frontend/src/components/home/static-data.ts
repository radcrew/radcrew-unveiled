import reImg1 from "@/assets/portfolio/real-estate-consultant/img1.png";
import reImg2 from "@/assets/portfolio/real-estate-consultant/img2.png";
import reImg3 from "@/assets/portfolio/real-estate-consultant/img3.png";
import reImg4 from "@/assets/portfolio/real-estate-consultant/img4.png";
import reImg5 from "@/assets/portfolio/real-estate-consultant/img5.png";
import cryptoPetsImg1 from "@/assets/portfolio/cryptopets/img1.png";
import cryptoPetsImg2 from "@/assets/portfolio/cryptopets/img2.png";
import cryptoPetsImg3 from "@/assets/portfolio/cryptopets/img3.png";
import cryptoPetsImg4 from "@/assets/portfolio/cryptopets/img4.png";
import forImg1 from "@/assets/portfolio/forgeng/img1.png";
import forImg2 from "@/assets/portfolio/forgeng/img2.png";
import forImg3 from "@/assets/portfolio/forgeng/img3.png";
import ceoImg from "@/assets/team/ceo.png";
import jesusImg from "@/assets/team/jesus-monroig.png";
import designImg from "@/assets/team/design.png";

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
    images: [reImg1, reImg2, reImg3, reImg4, reImg5],
    tags: ["React", "Next.js", "Product UI", "LLM", "Fastapi", "PostgreSQL", "Prisma", "MicroService", "Github-Actions"],
  },
  {
    title: "CryptoPets",
    description:
      "Collectible pet experience on-chain: minting, trading, and profile flows with a bright, approachable UI built for mainstream Web3 onboarding.",
    images: [cryptoPetsImg1, cryptoPetsImg2, cryptoPetsImg3, cryptoPetsImg4],
    tags: ["React", "Web3", "NFTs", "GraphQL", "Helius", "Agentic-AI", "grpc", "React-Native", "SubGraph", "Ethereum", "Solana", "HuggingFace", "Zod", "GoLang", "Redis", "PostgreSQL"],
  },
  {
    title: "Forgeng",
    description:
      "Internal platform for developer productivity: CI/CD orchestration, service templates, and observability tooling to accelerate delivery.",
    images: [forImg1, forImg2, forImg3],
    tags: ["TypeScript", "Node.js", "Kubernetes", "CI/CD", "Observability", "NestJS", "Passport", "PostgreSQL", "Shadcn-UI", "tailwindcss", "vitest", "NextJS", "Prisma"],
  }
];

export const teamMembers = [
  { name: "Hector Rosado", role: "CEO & Founder", image: ceoImg },
  { name: "Jesus Monroig", role: "Full Stack | Web3 Engineer", image: jesusImg },
  { name: "Jorge Benitez", role: "Full Stack | AI Engineer", image: designImg },
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
];

export type Testimonial = {
  quote: string;
  clientName: string;
  clientRole: string;
  clientCompany: string;
};

/** Add more entries here to enable the rotating carousel in Testimonial.tsx. */
export const testimonials: Testimonial[] = [
  {
    quote: "An incredible partner that transformed our technical architecture from the ground up.",
    clientName: "Jordan Lee",
    clientRole: "CTO",
    clientCompany: "Series B Fintech",
  },
];
