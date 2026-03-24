import { useQuery } from "@tanstack/react-query";
import { isContentfulConfigured } from "@/lib/contentful";
import { fetchEngineerById } from "@/lib/team-contentful";

export function engineerMemberQueryKey(id: string | undefined) {
  return ["contentful", "engineer", id] as const;
}

export function useEngineerMember(memberId: string | undefined) {
  return useQuery({
    queryKey: engineerMemberQueryKey(memberId),
    queryFn: () => fetchEngineerById(memberId!),
    enabled: Boolean(memberId) && isContentfulConfigured(),
  });
}
