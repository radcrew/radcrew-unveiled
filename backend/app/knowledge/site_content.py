"""Static marketing copy used for RAG (parity with backend/src/knowledge/site-content.ts)."""

from __future__ import annotations

from app.models import KnowledgeDocument


def get_static_site_documents() -> list[KnowledgeDocument]:
    return [
        KnowledgeDocument(
            id="hero",
            title="RadCrew overview",
            url="/",
            text=(
                "RadCrew is a lean development agency for serious products. "
                "They build end-to-end web and APIs, on-chain systems on EVM and Solana, and AI-powered "
                "features from prototypes to production. "
                "The team is three senior engineers focused on velocity with quality."
            ),
        ),
        KnowledgeDocument(
            id="services",
            title="Services and capabilities",
            url="/#services",
            text=(
                "Core capabilities include full-stack product engineering, Web3 on EVM and Solana, and AI in "
                "real products. "
                "They deliver web apps, APIs, dashboards, integrations, smart contracts, protocol UX, agents, RAG, "
                "and production AI features."
            ),
        ),
        KnowledgeDocument(
            id="how-we-work",
            title="How RadCrew works",
            url="/#how-we-work",
            text=(
                "Delivery rhythm: Discover, Build, Ship, Partner. "
                "They align on outcomes, iterate in short cycles, harden with observability and docs, and support "
                "handoff or phase-two roadmap work."
            ),
        ),
        KnowledgeDocument(
            id="contact",
            title="Contact and response times",
            url="/#contact",
            text=(
                "Contact email is code@radcrew.org. "
                "They usually respond within one to two business days."
            ),
        ),
    ]
