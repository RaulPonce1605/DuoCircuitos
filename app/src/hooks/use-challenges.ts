import { useQuery } from "@tanstack/react-query";

import { challengesService } from "@/services/challenges-service";

export const CHALLENGES_QUERY_KEY = ["challenges"] as const;

/** Desafíos de hoy y del mes con su avance. */
export function useChallenges() {
  return useQuery({ queryKey: CHALLENGES_QUERY_KEY, queryFn: challengesService.list });
}
