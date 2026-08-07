"""Static marketing copy used for RAG.

Mirrors the content rendered on the public site (frontend/src/components/home),
chiefly ``home/static-data.ts`` and the section components (Hero, Clients,
Stats, ProofBand, Capabilities, Spotlight, Process, Portfolio, TechStack, Team,
Testimonial, Journal, Faq, Contact). Keep this in sync when the site copy
changes.

Documents whose ids are listed in ``PLACEHOLDER_DOCUMENT_IDS`` mirror
``home/placeholder-content.ts``, where every client, quote, metric and post is
invented. They are indexed so the bot does not contradict the page it is
embedded in, but they make the bot assert those inventions in conversation.
Replace both files together.
"""

from __future__ import annotations

from app.chatbot.knowledge.models import KnowledgeDocument

#: Documents sourced from invented placeholder copy. See the module docstring.
PLACEHOLDER_DOCUMENT_IDS: frozenset[str] = frozenset(
    {"clients", "case-study-spotlight", "testimonial", "journal"}
)


def get_static_site_documents() -> list[KnowledgeDocument]:
    return [
        KnowledgeDocument(
            id="hero",
            title="RadCrew overview",
            url="/",
            text=(
                "RadCrew is a guild: several independent senior developers under one name — their "
                "tagline is \"We build what's next.\" "
                "Each works on their own and is open to work individually, so hiring one is not hiring "
                "the rest. The shared name covers the open source they write when they have free time. "
                "Between them they build AI/ML products and Web3 solutions on EVM and Solana, plus "
                "end-to-end web apps and APIs, from prototypes to production."
            ),
        ),
        KnowledgeDocument(
            id="services",
            title="Services and capabilities",
            url="/#services",
            text=(
                "The services RadCrew offers span six areas of capability. "
                "The three primary ones are: "
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
        # Split from `services` rather than appended to it: the combined text
        # exceeds MAX_CHUNK_CHARS, and static documents are kept to one chunk so
        # the in-memory and vector-store paths embed identical text.
        KnowledgeDocument(
            id="services-specialist",
            title="Specialist services",
            url="/#services",
            text=(
                "Alongside the three primary capabilities, RadCrew offers three more. "
                "Contract review and security: line-by-line review of the code that holds funds, covering "
                "accounting drift, upgrade paths, and failure modes that survive a happy-path test suite. "
                "Data platforms and pipelines: ingestion, transformation, and retrieval that stay "
                "predictable under load, built to be resumed after a failure rather than restarted. "
                "Embedded engineering: senior engineers inside your team, on your standups and in your "
                "repo, rather than a black box that returns a deliverable at the end of a quarter."
            ),
        ),
        KnowledgeDocument(
            id="how-we-work",
            title="How RadCrew works",
            url="/#process",
            text=(
                "RadCrew's process goes from first call to production—and after—in four phases. "
                "Discover: they map the architecture, define constraints, and build the blueprint, "
                "delivering an architecture review, a constraint map, and a scoped estimate. "
                "Build: elite engineering velocity, transparent sprints, relentless precision, with weekly "
                "working demos, tests written alongside the code, and work done in your repo and review "
                "process. "
                "Ship: deploy to production, stabilize infrastructure, and hand off clean docs, including "
                "runbooks, handover documentation, monitoring, and alerts. "
                "Partner: a long-term embedded relationship to scale the product forward, with embedded "
                "engineers, roadmap input, and migration and scaling support."
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
            # Not "Selected work": the lexical fallback weights title hits 2x, so
            # "work" here outscored tech-stack for "do you work with Rust?".
            title="Selected projects and case studies",
            url="/#portfolio",
            # Technology names are kept out of this document on purpose: listing
            # each project's stack here made it outrank `tech-stack` for
            # questions naming a single technology.
            # No literal "/work" path here: "work" is a common query token, and
            # the lexical fallback scored this document for unrelated questions.
            text=(
                "What RadCrew has built before: the products they have already shipped for clients. "
                "Featured projects, each shown with screenshots in the Selected Work section. "
                "Real Estate Consultant: a discovery and advisory experience with property "
                "search, market context, and guided consultation flows in a polished, trustworthy UI. "
                "CryptoPets: a collectible pet experience on-chain with minting, trading, and profile flows, "
                "built with a bright, approachable UI for mainstream Web3 onboarding. "
                "Forgeng: an internal platform for developer productivity covering CI/CD orchestration, "
                "service templates, and observability tooling to accelerate delivery."
            ),
        ),
        KnowledgeDocument(
            id="tech-stack",
            title="Technologies RadCrew works with",
            url="/",
            # Grouped by domain rather than listed flat: each name sits next to
            # words describing it, which a query naming one technology can match.
            text=(
                "The languages, frameworks, databases and platforms RadCrew works with. "
                "Programming languages: TypeScript, Python, Rust, and Solidity. "
                "Frontend: React, Next.js, TanStack Query, and Socket.IO. "
                "Backend frameworks: Node.js, NestJS, Django, and Flask. "
                "Web3 chains and tooling: EVM and Ethereum, Solana, and WalletConnect. "
                "Databases and data: PostgreSQL, MongoDB, Redis, GraphQL, and Sequelize. "
                "AI: LangChain and OpenAI. "
                "Infrastructure and CI: Docker, Kubernetes, Vercel, GitHub, and GitHub Actions. "
                "Mobile: Flutter, Android, and iOS. "
                "Testing: Jest and Cypress."
            ),
        ),
        KnowledgeDocument(
            id="testimonial",
            title="Client testimonials",
            url="/",
            # Quotes are summarised rather than reproduced in full: six verbatim
            # testimonials made this document diffuse enough that it stopped
            # ranking for "what do your clients say about you?".
            text=(
                "What clients say about RadCrew. Client testimonials, reviews, quotes and feedback from "
                "customers who have worked with them. Clients say: "
                "Dana Whitfield (VP Engineering, Northwind Capital) praises the rebuilt ingestion pipeline "
                "and the handover documentation. "
                "Amos Reyes (CTO, Vireo Labs) says they pushed back on the architecture and saved a rewrite. "
                "Priya Raman (Head of Protocol, Cobalt Exchange) says the contract audit caught two issues a "
                "previous firm had missed. "
                "Tomas Lindqvist (Founder, Meridian Freight) says they stayed through two scaling events. "
                "Grace Okonjo (Director of Product, Anvil Analytics) praises a retrieval prototype. "
                "Ben Kovak (COO, Torchlight) values direct daily access to the engineers."
            ),
        ),
        KnowledgeDocument(
            id="clients",
            # Titled by industry rather than "clients" so it does not outrank
            # `testimonial` for questions about what clients say.
            title="Industries and sectors RadCrew builds for",
            url="/",
            text=(
                "The logo wall on the site names companies across fintech (Northwind Capital), biotech (Vireo Labs), "
                "infrastructure (Halcyon), logistics (Meridian Freight), developer tools (Torchlight), "
                "robotics (Kestrel Systems), digital assets (Cobalt Exchange), and data (Anvil Analytics). "
                "The site also states: senior engineers only, no handoffs to juniors, direct access to the "
                "people writing the code, clients across 9 countries, embedded rather than outsourced, and "
                "that they stay after launch."
            ),
        ),
        KnowledgeDocument(
            id="case-study-spotlight",
            title="Case study: Northwind Capital risk pipeline",
            url="/",
            text=(
                "A featured case study for Northwind Capital: cutting a nightly risk run from six hours to "
                "eleven minutes. Their risk engine had grown into a single nightly batch that regularly "
                "overran the trading window; it was rebuilt as an incremental pipeline with checkpointing, "
                "so a failure resumes instead of restarting. "
                "Reported results: the nightly risk run went from 6 hours to 11 minutes, compute cost fell "
                "94%, there have been no missed trading windows since launch, and it took 9 weeks from "
                "design to production."
            ),
        ),
        KnowledgeDocument(
            id="journal",
            title="Journal and writing",
            url="/journal",
            text=(
                "RadCrew publishes a journal at /journal, described as notes from the work rather than "
                "marketing. Recent posts: "
                "\"Retrieval is not a vector database problem\" argues that most retrieval failures are "
                "chunking failures, because embedding models silently truncate long documents. "
                "\"What a contract audit actually catches\" argues the expensive findings are accounting "
                "drift and unrehearsed upgrade paths rather than reentrancy. "
                "\"The cost of a cold start\" argues that what matters is how often users hit a cold start, "
                "which depends on traffic shape rather than runtime."
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
        # Second half of the FAQ. Split for the same reason as
        # `services-specialist`: the full list exceeds MAX_CHUNK_CHARS.
        KnowledgeDocument(
            id="faq-working-together",
            title="Frequently asked questions about working together",
            url="/#faq",
            text=(
                "More common questions. "
                "Who actually writes the code? The engineers you meet in the first call; they do not staff a "
                "pitch with seniors and deliver with juniors, and they do not subcontract work out. "
                "Can you work inside our existing codebase and process? Yes — most engagements start in a "
                "repo someone else wrote, and they join your standups, review process, and branching model "
                "rather than asking you to adopt theirs. "
                "What happens if we need to pause or stop? You can stop at a sprint boundary; there is no "
                "lock-in clause, and everything built plus its documentation is yours on the way out."
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
        KnowledgeDocument(
            id="social-links",
            title="Social media, links, and where to find RadCrew",
            url="/#footer",
            text=(
                "RadCrew's official links: the website is radcrew.org, the contact email is code@radcrew.org, "
                "and their GitHub is github.com/radcrew. "
                "These are the only official channels listed on the site; RadCrew does not advertise other "
                "social media accounts (such as Twitter/X, LinkedIn, Discord, or Instagram)."
            ),
        ),
    ]
