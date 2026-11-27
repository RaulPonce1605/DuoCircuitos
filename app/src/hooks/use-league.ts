import { useQuery } from "@tanstack/react-query";

import { leaguesService } from "@/services/leagues-service";

export const LEAGUE_QUERY_KEY = ["league"] as const;

/** La liga de esta semana con su ranking. */
export function useLeague() {
  return useQuery({ queryKey: LEAGUE_QUERY_KEY, queryFn: leaguesService.current });
}
