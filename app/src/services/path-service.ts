import type { components } from "@/api/schema";
import { api } from "@/services/api-client";
import { authService } from "@/services/auth-service";

export type LearningPath = components["schemas"]["PathRead"];
export type PathUnit = components["schemas"]["UnitRead"];
export type PathNode = components["schemas"]["NodeRead"];

export const pathService = {
  getPath: (): Promise<LearningPath> => authService.authed(() => api.GET("/path")),
};
