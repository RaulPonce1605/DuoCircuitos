import type { components } from "@/api/schema";
import { api } from "@/services/api-client";
import { authService } from "@/services/auth-service";

export type Challenge = components["schemas"]["ChallengeRead"];
export type Challenges = components["schemas"]["ChallengesRead"];

/** Los desafíos los genera y los avanza el backend; aquí solo se leen. */
export const challengesService = {
  list: (): Promise<Challenges> => authService.authed(() => api.GET("/challenges")),
};
