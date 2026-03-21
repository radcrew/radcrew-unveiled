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
  {
    id: "nft-creator-suite",
    title: "Creator NFT suite",
    achievement:
      "Minting, royalties, and secondary-market tooling with gas-aware batch flows and a polished collector-facing storefront.",
    tags: ["Web3", "EVM", "Full-stack"],
    image: portfolioDeFi,
    imageAlt: "Product screenshot placeholder: NFT creator and storefront UI",
  },
  {
    id: "bridge-ops-dashboard",
    title: "Bridge & relayer ops",
    achievement:
      "Operational dashboards for cross-chain message and liquidity flows—alerts, replay tooling, and incident-friendly runbooks.",
    tags: ["Web3", "DevOps", "Full-stack"],
    image: portfolioAi,
    imageAlt: "Product screenshot placeholder: bridge monitoring dashboard",
  },
  {
    id: "agent-support-copilot",
    title: "Support copilot (agents)",
    achievement:
      "Ticket triage, suggested replies, and policy-grounded answers wired to CRM and knowledge bases with human-in-the-loop review.",
    tags: ["AI", "Agents", "Full-stack"],
    image: portfolioSolana,
    imageAlt: "Product screenshot placeholder: AI support assistant UI",
  },
  {
    id: "realtime-collab-saas",
    title: "Realtime collaboration SaaS",
    achievement:
      "Presence, shared cursors, and conflict-safe edits at scale—WebSockets, Redis-backed rooms, and resilient reconnect UX.",
    tags: ["Full-stack", "TypeScript", "Infra"],
    image: portfolioDeFi,
    imageAlt: "Product screenshot placeholder: collaborative editor or whiteboard",
  },
  {
    id: "mobile-web3-wallet",
    title: "Mobile Web3 wallet",
    achievement:
      "Account abstraction–friendly flows, deep links to dApps, and clear signing surfaces across EVM networks from a single app shell.",
    tags: ["Web3", "Mobile", "UX"],
    image: portfolioAi,
    imageAlt: "Product screenshot placeholder: mobile wallet app",
  },
  {
    id: "ml-ops-observability",
    title: "ML pipeline observability",
    achievement:
      "Tracing for training and inference jobs, drift dashboards, and cost visibility so teams ship models with confidence.",
    tags: ["AI", "MLOps", "Full-stack"],
    image: portfolioSolana,
    imageAlt: "Product screenshot placeholder: ML monitoring dashboard",
  },
  {
    id: "dao-governance-portal",
    title: "DAO governance portal",
    achievement:
      "Proposal lifecycle, delegation, and on-chain voting with readable timelines and wallet-connected participation.",
    tags: ["Web3", "Governance", "Full-stack"],
    image: portfolioDeFi,
    imageAlt: "Product screenshot placeholder: DAO voting and proposals UI",
  },
  {
    id: "b2b-api-platform",
    title: "B2B API platform",
    achievement:
      "Key management, usage metering, and developer docs—rate limits, webhooks, and OpenAPI-first design for partner integrations.",
    tags: ["Full-stack", "APIs", "DevEx"],
    image: portfolioAi,
    imageAlt: "Product screenshot placeholder: API console and documentation",
  },
];
