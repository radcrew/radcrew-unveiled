import { useQuery } from "@tanstack/react-query";
import { isContentfulConfigured } from "@/lib/contentful";
import { fetchEngineers } from "@/lib/team-contentful";

export const teamMembersQueryKey = ["contentful", "engineers"] as const;

export function useTeamMembers() {
  return useQuery({
    queryKey: teamMembersQueryKey,
    queryFn: fetchEngineers,
    enabled: isContentfulConfigured(),
  });
}
