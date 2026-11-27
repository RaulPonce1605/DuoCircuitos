import { useMutation, useQueryClient } from "@tanstack/react-query";

import { ACHIEVEMENTS_QUERY_KEY } from "@/hooks/use-achievements";
import { CHALLENGES_QUERY_KEY } from "@/hooks/use-challenges";
import { LEAGUE_QUERY_KEY } from "@/hooks/use-league";
import { CURRENT_USER_QUERY_KEY } from "@/hooks/use-current-user";
import { PATH_QUERY_KEY } from "@/hooks/use-path";
import { rewardsService } from "@/services/rewards-service";

export type ChestTarget = { kind: "attempt"; chestId: string } | { kind: "node"; nodeKey: string };

/** Abrir un cofre: del intento recién terminado o el nodo cofre del camino. */
export function useOpenChest(target: ChestTarget) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () =>
      target.kind === "attempt" ? rewardsService.openChest(target.chestId) : rewardsService.openNodeChest(target.nodeKey),
    onSuccess: () => {
      // EXP, energía, medallas y (en el cofre del camino) el nodo completado cambiaron.
      void queryClient.invalidateQueries({ queryKey: CURRENT_USER_QUERY_KEY });
      void queryClient.invalidateQueries({ queryKey: ACHIEVEMENTS_QUERY_KEY });
      void queryClient.invalidateQueries({ queryKey: CHALLENGES_QUERY_KEY });
      void queryClient.invalidateQueries({ queryKey: LEAGUE_QUERY_KEY });
      if (target.kind === "node") {
        void queryClient.invalidateQueries({ queryKey: PATH_QUERY_KEY });
      }
    },
  });
}
