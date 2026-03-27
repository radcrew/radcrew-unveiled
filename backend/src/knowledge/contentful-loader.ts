import { createClient, type EntrySkeletonType } from "contentful";
import type { AppConfig } from "../config.js";
import type { KnowledgeDocument } from "../types.js";

type GenericSkeleton = EntrySkeletonType<Record<string, unknown>, string>;

function pickString(value: unknown): string {
  if (value == null) return "";
  if (typeof value === "string") return value;
  if (typeof value === "object" && !Array.isArray(value)) {
    const firstString = Object.values(value).find((part) => typeof part === "string");
    return typeof firstString === "string" ? firstString : "";
  }
  return String(value);
}

function fieldsToText(fields: Record<string, unknown>): string {
  return Object.values(fields)
    .map((field) => pickString(field).trim())
    .filter(Boolean)
    .join(" ");
}

export async function loadContentfulDocuments(config: AppConfig): Promise<KnowledgeDocument[]> {
  if (!config.CONTENTFUL_SPACE_ID || !config.CONTENTFUL_DELIVERY_TOKEN) {
    return [];
  }

  const client = createClient({
    space: config.CONTENTFUL_SPACE_ID,
    accessToken: config.CONTENTFUL_DELIVERY_TOKEN,
    environment: config.CONTENTFUL_ENVIRONMENT,
  });

  const entries = await client.getEntries<GenericSkeleton>({
    limit: 100,
    include: 0,
  });

  return entries.items.flatMap((entry): KnowledgeDocument[] => {
    const fields = entry.fields as Record<string, unknown>;
    const text = fieldsToText(fields);
    if (!text) return [];

    const title =
      pickString(fields.title) ||
      pickString(fields.name) ||
      pickString(fields.heading) ||
      `Contentful entry ${entry.sys.id}`;

    return [
      {
        id: `contentful:${entry.sys.id}`,
        title,
        text,
        url: `https://app.contentful.com/spaces/${config.CONTENTFUL_SPACE_ID}/entries/${entry.sys.id}`,
      },
    ];
  });
}
