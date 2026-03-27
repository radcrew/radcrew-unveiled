/** App shape for team / engineer profiles (filled from Contentful or other sources). */
export interface TeamMember {
  id: string;
  name: string;
  role: string;
  shortRole: string;
  bio: string;
  skills: string[];
  experience: string;
  quote: string;
  initials: string;
  website?: string;
}
