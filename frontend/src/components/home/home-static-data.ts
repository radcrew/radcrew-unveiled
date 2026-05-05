import reImg1 from "@/assets/portfolio/real-estate-consultant/img1.png";
import reImg2 from "@/assets/portfolio/real-estate-consultant/img2.png";
import reImg3 from "@/assets/portfolio/real-estate-consultant/img3.png";
import reImg4 from "@/assets/portfolio/real-estate-consultant/img4.png";
import reImg5 from "@/assets/portfolio/real-estate-consultant/img5.png";
import cryptoPetsImg1 from "@/assets/portfolio/cryptopets/img1.png";
import cryptoPetsImg2 from "@/assets/portfolio/cryptopets/img2.png";
import ceoImg from "@/assets/team/ceo.png";
import jesusImg from "@/assets/team/jesus-monroig.png";
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
];

export const homeTeam = [
  { name: "Hector Rosado", role: "CEO & Founder", image: ceoImg },
  { name: "Jesus Monroig", role: "Full Stack | Web3 Engineer", image: jesusImg },
  { name: "Jorge Benitez", role: "Full Stack | AI Engineer", image: designImg },
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
