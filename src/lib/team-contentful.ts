import type { Entry } from "contentful";
import { contentfulClient } from "@/lib/contentful";
import type { TeamMember } from "@/lib/team-data";

/** Content type id in Contentful */
export const ENGINEERS_CONTENT_TYPE = "engineers";

/** Field ids on the `engineers` content type */
const F = {
  name: "name",
  summery: "summery",
  /** Fallback if the field was created as `summary` */
  summary: "summary",
  role: "role",
  website: "website",
} as const;

/**
 * Contentful often returns localized fields as `{ "en-US": "..." }`.
 * This normalizes to a plain string (first locale wins).
 */
function pickString(value: unknown): string {
  if (value == null) return "";
  if (typeof value === "string") return value;
  if (typeof value === "object" && !Array.isArray(value)) {
    const v = Object.values(value).find((x) => typeof x === "string");
    return typeof v === "string" ? v : "";
  }
  return String(value);
}

export function initialsFromName(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length >= 2) {
    const a = parts[0][0];
    const b = parts[parts.length - 1][0];
    if (a && b) return (a + b).toUpperCase();
  }
  const compact = name.replace(/\s/g, "");
  return compact.slice(0, 2).toUpperCase() || "?";
}

/** Short line for cards: first segment before " / " or trimmed role. */
export function shortRoleFromRole(role: string): string {
  const t = role.trim();
  if (!t) return "";
  const first = t.split(/\s*\/\s*/)[0]?.trim();
  return first && first.length <= 56 ? first : t.length > 56 ? `${t.slice(0, 53)}…` : t;
}

function readBio(fields: Record<string, unknown>): string {
  const raw = fields[F.summery] ?? fields[F.summary];
  return pickString(raw).trim();
}

export function mapEngineerEntry(entry: Entry): TeamMember {
  const fields = entry.fields as Record<string, unknown>;
  const name = pickString(fields[F.name]).trim();
  const role = pickString(fields[F.role]).trim();
  const bio = readBio(fields);
  const websiteRaw = pickString(fields[F.website]).trim();

  return {
    id: entry.sys.id,
    name: name || "Unknown",
    role: role || "Engineer",
    shortRole: shortRoleFromRole(role || "Engineer"),
    bio: bio || "",
    skills: [],
    experience: "",
    quote: "",
    initials: initialsFromName(name || "?"),
    website: websiteRaw || undefined,
  };
}

export async function fetchEngineers(): Promise<TeamMember[]> {
  if (!contentfulClient) {
    throw new Error("Contentful is not configured.");
  }
  const res = await contentfulClient.getEntries({
    content_type: ENGINEERS_CONTENT_TYPE,
    order: ["fields.name"],
  });
  return res.items.map((e) => mapEngineerEntry(e));
}

export async function fetchEngineerById(id: string): Promise<TeamMember | null> {
  if (!contentfulClient) {
    throw new Error("Contentful is not configured.");
  }
  const res = await contentfulClient.getEntries({
    content_type: ENGINEERS_CONTENT_TYPE,
    "sys.id": id,
    limit: 1,
  });
  const entry = res.items[0];
  if (!entry) return null;
  return mapEngineerEntry(entry);
}
