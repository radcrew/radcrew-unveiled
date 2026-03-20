import portfolioDeFi from "@/assets/workspace-1.jpg";
import portfolioAi from "@/assets/workspace-2.jpg";
import portfolioSolana from "@/assets/workspace-3.jpg";

/** Replace images in `src/assets/` and update copy to match real client work. */
export interface PortfolioProject {
  id: string;
  title: string;
  achievement: string;
  tags: string[];
  image: string;
  imageAlt: string;
}

export const portfolioProjects: PortfolioProject[] = [
  {
    id: "defi-analytics",
    title: "Multi-chain DeFi analytics",
    achievement:
      "Unified dashboards and APIs for positions and risk across EVM deployments—shipped with strict observability and upgrade paths.",
    tags: ["Web3", "EVM", "Full-stack"],
    image: portfolioDeFi,
    imageAlt: "Product screenshot placeholder: DeFi analytics interface",
  },
  {
    id: "enterprise-rag",
    title: "Enterprise RAG assistant",
    achievement:
      "Grounded LLM Q&A over private docs with citations, access control, and eval hooks—integrated into the customer’s existing stack.",
    tags: ["AI", "Full-stack", "RAG"],
    image: portfolioAi,
    imageAlt: "Product screenshot placeholder: AI assistant and knowledge UI",
  },
  {
    id: "solana-trading",
    title: "Solana trading experience",
    achievement:
      "End-to-end flow from wallet to settlement with performance-focused UX and on-chain program integration.",
    tags: ["Solana", "Web3", "UX"],
    image: portfolioSolana,
    imageAlt: "Product screenshot placeholder: trading or wallet product UI",
  },
];
