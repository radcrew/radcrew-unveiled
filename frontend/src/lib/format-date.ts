const postDateFormatter = new Intl.DateTimeFormat("en-GB", {
  day: "numeric",
  month: "short",
  year: "numeric",
});

/** Formats an ISO `YYYY-MM-DD` date for display on journal listings and posts. */
export function formatPostDate(isoDate: string): string {
  return postDateFormatter.format(new Date(isoDate));
}
