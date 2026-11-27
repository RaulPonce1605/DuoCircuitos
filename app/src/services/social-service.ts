import type { components } from "@/api/schema";
import { api } from "@/services/api-client";
import { authService } from "@/services/auth-service";

export type UserCard = components["schemas"]["UserCardRead"];
export type Friends = components["schemas"]["FriendsRead"];

export const socialService = {
  friends: (): Promise<Friends> => authService.authed(() => api.GET("/friends")),

  search: (query: string): Promise<UserCard[]> =>
    authService.authed(() => api.GET("/users/search", { params: { query: { q: query } } })),

  follow: (userId: string): Promise<UserCard> =>
    authService.authed(() => api.POST("/users/{user_id}/follow", { params: { path: { user_id: userId } } })),

  unfollow: (userId: string): Promise<UserCard> =>
    authService.authed(() => api.DELETE("/users/{user_id}/follow", { params: { path: { user_id: userId } } })),
};
