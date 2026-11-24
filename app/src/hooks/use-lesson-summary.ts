import { useQuery } from "@tanstack/react-query";

import { lessonService } from "@/services/lesson-service";

export function useLessonSummary(attemptId: string) {
  return useQuery({
    queryKey: ["lesson-summary", attemptId],
    queryFn: () => lessonService.summary(attemptId),
    staleTime: Infinity,
  });
}
