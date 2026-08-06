/**
 * PLACEHOLDER CONTENT — every name, quote, metric and date in this file is invented.
 *
 * The companies and people here are fictional and were chosen so they cannot be
 * mistaken for real businesses: no real client is quoted, credited or implied.
 * Replace wholesale before making any claim on this content publicly.
 *
 * Real content belongs in `static-data.ts`. Keeping the two apart is what makes
 * "what still needs replacing?" a one-file answer.
 */

export type Client = { name: string; sector: string };

/** Rendered as wordmarks, not images, so there are no fabricated logo files. */
export const placeholderClients: Client[] = [
  { name: "Northwind Capital", sector: "Fintech" },
  { name: "Vireo Labs", sector: "Biotech" },
  { name: "Halcyon", sector: "Infrastructure" },
  { name: "Meridian Freight", sector: "Logistics" },
  { name: "Torchlight", sector: "Developer tools" },
  { name: "Kestrel Systems", sector: "Robotics" },
  { name: "Cobalt Exchange", sector: "Digital assets" },
  { name: "Anvil Analytics", sector: "Data" },
];

/**
 * Short strip claims for the scrolling proof band. Deliberately disjoint from
 * the `Stats` counters directly above it: the band sits within a screen of
 * them, so a shared number reads as padding rather than as reinforcement.
 */
export const placeholderProofPoints: string[] = [
  "Senior engineers only",
  "No handoffs to juniors",
  "Direct access to the people writing the code",
  "Clients across 9 countries",
  "Embedded, not outsourced",
  "We stay after launch",
];

export type PlaceholderTestimonial = {
  quote: string;
  clientName: string;
  clientRole: string;
  clientCompany: string;
};

export const placeholderTestimonials: PlaceholderTestimonial[] = [
  {
    quote:
      "They rebuilt our ingestion pipeline in six weeks and it has not paged us since. The handover documentation was better than what we write internally.",
    clientName: "Dana Whitfield",
    clientRole: "VP Engineering",
    clientCompany: "Northwind Capital",
  },
  {
    quote:
      "We came in expecting a contractor and got a team that pushed back on our architecture. The pushback was right, and it saved us a rewrite.",
    clientName: "Amos Reyes",
    clientRole: "CTO",
    clientCompany: "Vireo Labs",
  },
  {
    quote:
      "The contract audit caught two issues our previous firm signed off on. That alone paid for the engagement several times over.",
    clientName: "Priya Raman",
    clientRole: "Head of Protocol",
    clientCompany: "Cobalt Exchange",
  },
  {
    quote:
      "Most agencies disappear after launch. Ours stayed through two scaling events and a migration nobody enjoyed.",
    clientName: "Tomas Lindqvist",
    clientRole: "Founder",
    clientCompany: "Meridian Freight",
  },
  {
    quote:
      "They shipped a working retrieval prototype in nine days, then spent the next month telling us which parts of it we did not need.",
    clientName: "Grace Okonjo",
    clientRole: "Director of Product",
    clientCompany: "Anvil Analytics",
  },
  {
    quote:
      "Direct access to the people writing the code, every day. After three agencies, that was the difference.",
    clientName: "Ben Kovak",
    clientRole: "COO",
    clientCompany: "Torchlight",
  },
];

export type SpotlightMetric = { value: string; label: string };

export const placeholderSpotlight = {
  client: "Northwind Capital",
  title: "Cutting a nightly risk run from six hours to eleven minutes",
  summary:
    "Northwind's risk engine had grown into a single nightly batch that regularly overran the trading window. We rebuilt it as an incremental pipeline with checkpointing, so a failure resumes instead of restarting.",
  metrics: [
    { value: "6h to 11m", label: "Nightly risk run" },
    { value: "94%", label: "Compute cost reduction" },
    { value: "0", label: "Missed trading windows since launch" },
    { value: "9 wks", label: "Design to production" },
  ] satisfies SpotlightMetric[],
};

export type JournalPost = {
  slug: string;
  title: string;
  excerpt: string;
  date: string;
  readingTime: string;
  tag: string;
};

export const placeholderJournal: JournalPost[] = [
  {
    slug: "retrieval-is-not-a-vector-database",
    title: "Retrieval is not a vector database problem",
    excerpt:
      "Teams reach for pgvector before they have checked whether their chunks are the right size. Most retrieval failures we are asked to fix are chunking failures wearing a different hat.",
    date: "2026-07-22",
    readingTime: "8 min",
    tag: "AI Engineering",
  },
  {
    slug: "what-a-contract-audit-actually-catches",
    title: "What a contract audit actually catches",
    excerpt:
      "Reentrancy gets the attention, but the findings that cost real money are usually accounting drift and upgrade paths nobody rehearsed. A walk through the categories in order of expected loss.",
    date: "2026-06-30",
    readingTime: "12 min",
    tag: "Web3",
  },
  {
    slug: "the-cost-of-a-cold-start",
    title: "The cost of a cold start",
    excerpt:
      "Serverless makes the first request someone else's problem right up until it is your latency budget. Measuring what a cold start costs before designing around one.",
    date: "2026-06-11",
    readingTime: "6 min",
    tag: "Platform",
  },
];
