import type { components } from "@/api/schema";
import { api } from "@/services/api-client";
import { authService, type User } from "@/services/auth-service";

export type UserUpdate = components["schemas"]["UserUpdate"];

/** Configuración del usuario: el backend valida y guarda; aquí solo se manda lo que cambió. */
export const userService = {
  update: (changes: UserUpdate): Promise<User> => authService.authed(() => api.PATCH("/me", { body: changes })),
};
