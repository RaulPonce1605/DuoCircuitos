import { useQuery } from "@tanstack/react-query";

import { rewardsService } from "@/services/rewards-service";

export const ACHIEVEMENTS_QUERY_KEY = ["achievements"] as const;

/** Logros con su progreso y medallas ganadas, calculados por el backend. */
export function useAchievements() {
  return useQuery({ queryKey: ACHIEVEMENTS_QUERY_KEY, queryFn: rewardsService.achievements });
}
