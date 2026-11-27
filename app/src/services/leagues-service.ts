import type { components } from "@/api/schema";
import { api } from "@/services/api-client";
import { authService } from "@/services/auth-service";

export type League = components["schemas"]["LeagueRead"];
export type LeagueMember = components["schemas"]["LeagueMemberRead"];

/** Las ligas las arma y las cierra el backend; aquí solo se leen. */
export const leaguesService = {
  current: (): Promise<League> => authService.authed(() => api.GET("/leagues/current")),
};
