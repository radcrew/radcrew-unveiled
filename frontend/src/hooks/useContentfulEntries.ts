import { useQuery } from "@tanstack/react-query";
import type { EntriesQueries } from "contentful";
import { contentfulClient, isContentfulConfigured } from "@/lib/contentful";

type EntryQuery = EntriesQueries<undefined>;

/**
 * Fetch entries from Contentful (e.g. portfolio items, blog posts).
 *
 * @param query - Pass `{ content_type: 'yourTypeId' }` or any getEntries query.
 *
 * @example
 * const { data, isLoading } = useContentfulEntries({ content_type: 'portfolioProject' });
 */
export function useContentfulEntries(query: EntryQuery) {
  return useQuery({
    queryKey: ["contentful", "entries", query],
    queryFn: async () => {
      if (!contentfulClient) {
        throw new Error("Contentful is not configured. Copy .env.example to .env and set VITE_* variables.");
      }
      return contentfulClient.getEntries(query);
    },
    enabled: isContentfulConfigured(),
  });
}
