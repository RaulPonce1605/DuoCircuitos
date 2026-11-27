import type { components } from "@/api/schema";
import { api } from "@/services/api-client";
import { authService } from "@/services/auth-service";

export type Chest = components["schemas"]["ChestRead"];
export type Badge = components["schemas"]["BadgeRead"];
export type Achievement = components["schemas"]["AchievementRead"];
export type Achievements = components["schemas"]["AchievementsRead"];

/** Cofres, logros y medallas: el backend sortea los premios y decide qué se gana. */
export const rewardsService = {
  openChest: (chestId: string): Promise<Chest> =>
    authService.authed(() => api.POST("/chests/{chest_id}/open", { params: { path: { chest_id: chestId } } })),

  openNodeChest: (nodeKey: string): Promise<Chest> =>
    authService.authed(() => api.POST("/nodes/{node_key}/chest", { params: { path: { node_key: nodeKey } } })),

  achievements: (): Promise<Achievements> => authService.authed(() => api.GET("/me/achievements")),
};
