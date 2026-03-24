import { type ContentfulClientApi, createClient } from "contentful";

/**
 * Contentful Delivery API client (read-only).
 * Tokens prefixed with VITE_ are embedded in the client bundle—anyone can read them.
 * Use a Delivery token with only the permissions you need; for secrets, call Contentful from a backend.
 */
function createContentfulClient(): ContentfulClientApi<undefined> | null {
  const space = import.meta.env.VITE_CONTENTFUL_SPACE_ID;
  const accessToken = import.meta.env.VITE_CONTENTFUL_DELIVERY_TOKEN;
  const environment = import.meta.env.VITE_CONTENTFUL_ENVIRONMENT ?? "master";

  if (!space || !accessToken) {
    return null;
  }

  return createClient({
    space,
    accessToken,
    environment,
  });
}

export const contentfulClient = createContentfulClient();

export function isContentfulConfigured(): boolean {
  return contentfulClient !== null;
}
