import { useQuery } from "@tanstack/react-query";

import { pathService } from "@/services/path-service";

export const PATH_QUERY_KEY = ["path"] as const;

export function usePath() {
  return useQuery({ queryKey: PATH_QUERY_KEY, queryFn: pathService.getPath });
}
