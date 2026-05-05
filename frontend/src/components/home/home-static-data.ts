import portalImg from "@/assets/portfolio/portal.png";
import apiImg from "@/assets/portfolio/api.png";
import defiImg from "@/assets/portfolio/defi.png";
import ragImg from "@/assets/portfolio/rag.png";
import scienceImg from "@/assets/portfolio/science.png";
import reImg1 from "@/assets/portfolio/real-estate-consultant/img1.png";
import reImg2 from "@/assets/portfolio/real-estate-consultant/img2.png";
import reImg3 from "@/assets/portfolio/real-estate-consultant/img3.png";
import reImg4 from "@/assets/portfolio/real-estate-consultant/img4.png";
import reImg5 from "@/assets/portfolio/real-estate-consultant/img5.png";
import cryptoPetsImg1 from "@/assets/portfolio/cryptopets/img1.png";
import cryptoPetsImg2 from "@/assets/portfolio/cryptopets/img2.png";
import ceoImg from "@/assets/team/ceo.png";
import ctoImg from "@/assets/team/cto.png";
import designImg from "@/assets/team/design.png";

export type HomeProject = {
  title: string;
  description: string;
  tags: string[];
  image?: string;
  images?: string[];
};

export const homeProjects: HomeProject[] = [
  {
    title: "Real Estate Consultant",
    description:
      "Client-facing discovery and advisory experience: property search, market context, and guided consultation flows with a polished, trustworthy UI.",
    images: [reImg1, reImg2, reImg3, reImg4, reImg5],
    tags: ["React", "Next.js", "Product UI"],
  },
  {
    title: "CryptoPets",
    description:
      "Collectible pet experience on-chain: minting, trading, and profile flows with a bright, approachable UI built for mainstream Web3 onboarding.",
    images: [cryptoPetsImg1, cryptoPetsImg2],
    tags: ["React", "Web3", "NFTs"],
  },
  {
    title: "Governance Portal",
    description:
      "End-to-end platform for DAO governance and on-chain voting. Architected for uncompromising security and high throughput.",
    image: portalImg,
    tags: ["Solana", "Next.js", "Rust"],
  },
  {
    title: "B2B API Platform",
    description:
      "Key management and judge ranking infrastructure for enterprise. High availability, low latency, globally distributed.",
    image: apiImg,
    tags: ["Node.js", "Redis", "EVM"],
  },
  {
    title: "Multi-chain DeFi Analytics",
    description:
      "Unified dashboard aggregating yield opportunities across protocols. Real-time data processing and execution.",
    image: defiImg,
    tags: ["React", "GraphQL", "Web3"],
  },
  {
    title: "Enterprise RAG Assistant",
    description:
      "Private LLM Q&A over internal documentation with strict RBAC. Built for legal and compliance teams.",
    image: ragImg,
    tags: ["Python", "OpenAI", "Vector DB"],
  },
  {
    title: "Science Trail",
    description:
      "End-to-end experiment tracking platform for biotech researchers. Compliant data custody and modern workflows.",
    image: scienceImg,
    tags: ["React", "Django", "PostgreSQL"],
  },
];

export const homeTeam = [
  { name: "Alex Vance", role: "Managing Partner", image: ceoImg },
  { name: "Sarah Chen", role: "Head of Engineering", image: ctoImg },
  { name: "Marcus Reid", role: "Lead Architect", image: designImg },
];

export const homeFaqs = [
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

export const homeTestimonial = {
  quote: "An incredible partner that transformed our technical architecture from the ground up.",
  clientName: "Jordan Lee",
  clientRole: "CTO",
  clientCompany: "Series B Fintech",
};
