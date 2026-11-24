import type { components } from "@/api/schema";
import type { ExerciseAnswer } from "@/components/exercises/types";
import { api } from "@/services/api-client";
import { authService } from "@/services/auth-service";

export type LessonAttempt = components["schemas"]["LessonAttemptRead"];
export type CheckResult = components["schemas"]["CheckResultRead"];
export type ExerciseInstance = components["schemas"]["ExerciseInstanceRead"];
export type LessonSummary = components["schemas"]["LessonAttemptSummaryRead"];

/** La validación y el sorteo de valores son del backend; aquí solo se llama a la API. */
export const lessonService = {
  start: (lessonSlug: string): Promise<LessonAttempt> =>
    authService.authed(() =>
      api.POST("/lessons/{lesson_slug}/attempts", { params: { path: { lesson_slug: lessonSlug } } }),
    ),

  check: (instanceId: string, answer: ExerciseAnswer): Promise<CheckResult> =>
    authService.authed(() =>
      api.POST("/exercise-instances/{instance_id}/check", {
        params: { path: { instance_id: instanceId } },
        body: { answer },
      }),
    ),

  summary: (attemptId: string): Promise<LessonSummary> =>
    authService.authed(() =>
      api.GET("/lesson-attempts/{attempt_id}/summary", { params: { path: { attempt_id: attemptId } } }),
    ),
};
