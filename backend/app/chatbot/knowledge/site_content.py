"""Static marketing copy used for RAG.

Mirrors the content rendered on the public site (frontend/src/components/home),
chiefly ``home/static-data.ts`` and the section components (Hero, Stats,
Capabilities, Process, Portfolio, TechStack, Testimonial, Faq, Contact). Keep
this in sync when the site copy changes.
"""

from __future__ import annotations

from app.chatbot.knowledge.models import KnowledgeDocument


def get_static_site_documents() -> list[KnowledgeDocument]:
    return [
        KnowledgeDocument(
            id="hero",
            title="RadCrew overview",
            url="/",
            text=(
                "RadCrew is a lean, elite engineering studio for serious products — their tagline is "
                "\"We build what's next.\" "
                "They build AI/ML products and Web3 solutions on EVM and Solana, plus end-to-end web apps "
                "and APIs, from prototypes to production, for discerning clients who demand precision. "
                "The team is three senior engineers focused on velocity with quality."
            ),
        ),
        KnowledgeDocument(
            id="services",
            title="Services and capabilities",
            url="/#services",
            text=(
                "Core capabilities are organized into three areas. "
                "1) Full-stack product engineering: from scalable data pipelines to bulletproof production "
                "systems, building platforms architected to scale elegantly from day one — web apps, APIs, "
                "dashboards, and integrations. "
                "2) Web3 on EVM and Solana: secure smart contract development, complex DeFi mechanics, and "
                "full-stack dApp architecture, rigorously tested and flawlessly executed — including smart "
                "contracts and protocol UX. "
                "3) AI in the real product: embedding intelligent capabilities into existing stacks, from "
                "custom RAG pipelines to fine-tuned autonomous agents, plus production AI features."
            ),
        ),
        KnowledgeDocument(
            id="how-we-work",
            title="How RadCrew works",
            url="/#process",
            text=(
                "RadCrew's process goes from first call to production—and after—in four phases. "
                "Discover: they map the architecture, define constraints, and build the blueprint. "
                "Build: elite engineering velocity, transparent sprints, relentless precision. "
                "Ship: deploy to production, stabilize infrastructure, and hand off clean docs. "
                "Partner: a long-term embedded relationship to scale the product forward."
            ),
        ),
        KnowledgeDocument(
            id="stats",
            title="RadCrew by the numbers",
            url="/",
            text=(
                "Track record: 40+ projects shipped, 12+ happy clients, 5 years building, and a 99.9% uptime "
                "SLA."
            ),
        ),
        KnowledgeDocument(
            id="portfolio",
            title="Selected work and portfolio",
            url="/#portfolio",
            text=(
                "Featured projects. "
                "Real Estate Consultant: a client-facing discovery and advisory experience with property "
                "search, market context, and guided consultation flows in a polished, trustworthy UI "
                "(React, Next.js, product UI). "
                "CryptoPets: a collectible pet experience on-chain with minting, trading, and profile flows, "
                "built with a bright, approachable UI for mainstream Web3 onboarding (React, Web3, NFTs)."
            ),
        ),
        KnowledgeDocument(
            id="tech-stack",
            title="Technologies RadCrew works with",
            url="/",
            text=(
                "Technologies they master span frontend, backend, Web3, AI, and infrastructure: "
                "React, Next.js, TypeScript, Node.js, NestJS, Django, Flask, Python, Rust, "
                "Solidity, EVM/Ethereum, Solana, WalletConnect, "
                "MongoDB, PostgreSQL, Redis, GraphQL, Sequelize, TanStack Query, Socket.IO, "
                "LangChain, OpenAI, "
                "Docker, Kubernetes, Vercel, GitHub, GitHub Actions, "
                "Flutter, Android, iOS/Apple, and testing with Jest and Cypress."
            ),
        ),
        KnowledgeDocument(
            id="testimonial",
            title="Client testimonial",
            url="/",
            text=(
                "A client testimonial from Jordan Lee, CTO at a Series B fintech: "
                "\"An incredible partner that transformed our technical architecture from the ground up.\""
            ),
        ),
        KnowledgeDocument(
            id="faq",
            title="Frequently asked questions",
            url="/#faq",
            text=(
                "Common questions. "
                "What size projects do you take on? They partner with startups and scale-ups on projects "
                "from 3-month MVPs to multi-year embedded engagements — quality over quantity. "
                "Do you work on fixed-price or time-and-materials contracts? Both; they recommend the right "
                "model based on the project's scope and certainty. "
                "How quickly can you start? Typically within 2 weeks of signing — capacity is kept "
                "deliberately limited to ensure exceptional execution. "
                "Do you offer post-launch support? Yes — the Partner phase is an ongoing embedded "
                "relationship, not just a maintenance contract; they stay and scale with you. "
                "What makes RadCrew different? Senior talent only, no handoffs to juniors — the people you "
                "meet are the people who build, with meticulous execution."
            ),
        ),
        KnowledgeDocument(
            id="contact",
            title="Contact and response times",
            url="/#contact",
            text=(
                "Contact email is code@radcrew.org, and the official website is radcrew.org. "
                "You can start a project through the website inquiry form (which asks for a project type) or "
                "by emailing directly; they follow up to schedule a discovery call. "
                "They usually respond within one to two business days."
            ),
        ),
    ]
