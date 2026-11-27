import type { components } from "@/api/schema";
import { api } from "@/services/api-client";
import { authService } from "@/services/auth-service";

export type TutorReply = components["schemas"]["TutorReplyRead"];

/** El tutor vive en el backend: él arma el prompt, llama al LLM y filtra la respuesta. */
export const tutorService = {
  ask: (instanceId: string, message: string | null): Promise<TutorReply> =>
    authService.authed(() =>
      api.POST("/exercise-instances/{instance_id}/tutor", {
        params: { path: { instance_id: instanceId } },
        body: { message },
      }),
    ),
};
