import { useQuery } from "@tanstack/react-query";
import axios from "axios";

import { resumeApi } from "@/api/resumeApi";

/**
 * Wraps GET /resume/me. A 404 here means "no resume uploaded yet," which
 * is a normal, expected state - not a real error - so it's surfaced
 * through `hasNoResume` instead of `isError`.
 */
export function useMyResume() {
  const query = useQuery({
    queryKey: ["resume", "me"],
    queryFn: resumeApi.getMyResume,
    retry: (failureCount, error) => {
      if (axios.isAxiosError(error) && error.response?.status === 404) return false;
      return failureCount < 1;
    },
  });

  const hasNoResume = axios.isAxiosError(query.error) && query.error.response?.status === 404;

  return { ...query, hasNoResume };
}
