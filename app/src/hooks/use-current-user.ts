import { useQuery } from "@tanstack/react-query";

import { authService } from "@/services/auth-service";

export const CURRENT_USER_QUERY_KEY = ["me"] as const;

/** El usuario con su EXP y racha actualizadas desde el backend. */
export function useCurrentUser() {
  return useQuery({ queryKey: CURRENT_USER_QUERY_KEY, queryFn: authService.getCurrentUser });
}
