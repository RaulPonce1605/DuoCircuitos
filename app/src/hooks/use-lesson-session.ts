import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import type { ExerciseAnswer } from "@/components/exercises/types";
import { CURRENT_USER_QUERY_KEY } from "@/hooks/use-current-user";
import { PATH_QUERY_KEY } from "@/hooks/use-path";
import {
  type CheckResult,
  type ExerciseInstance,
  type LessonAttempt,
  lessonService,
} from "@/services/lesson-service";

type Progress = LessonAttempt["progress"];

/**
 * Flujo de una lección (CLAUDE.md 1.2): el backend crea el intento y valida cada respuesta;
 * aquí solo se guarda qué ejercicio se está viendo, la respuesta armada y la retroalimentación.
 */
export function useLessonSession(lessonSlug: string) {
  const queryClient = useQueryClient();
  // Iniciar crea un intento en el backend: se pide una sola vez por pantalla (sin reintentos
  // ni recargas automáticas) y se descarta al salir.
  const attempt = useQuery({
    queryKey: ["lesson-attempt", lessonSlug],
    queryFn: () => lessonService.start(lessonSlug),
    staleTime: Infinity,
    gcTime: 0,
    retry: false,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
  });

  // `null` = todavía en el primer ejercicio del intento.
  const [current, setCurrent] = useState<ExerciseInstance | null>(null);
  const [progress, setProgress] = useState<Progress | null>(null);
  const [answer, setAnswer] = useState<ExerciseAnswer | null>(null);
  const [feedback, setFeedback] = useState<CheckResult | null>(null);

  const exercise = current ?? attempt.data?.current_exercise ?? null;

  const check = useMutation({
    mutationFn: (args: { instanceId: string; answer: ExerciseAnswer }) =>
      lessonService.check(args.instanceId, args.answer),
    onSuccess: (result) => {
      setFeedback(result);
      setProgress(result.progress);
      if (result.attempt_completed) {
        // EXP, racha y nodos desbloqueados cambiaron en el backend.
        void queryClient.invalidateQueries({ queryKey: PATH_QUERY_KEY });
        void queryClient.invalidateQueries({ queryKey: CURRENT_USER_QUERY_KEY });
      }
    },
  });

  return {
    attempt,
    exercise,
    progress: progress ?? attempt.data?.progress ?? null,
    answer,
    feedback,
    checkError: check.error,
    isChecking: check.isPending,
    setAnswer: (next: ExerciseAnswer | null) => {
      if (!feedback) {
        setAnswer(next);
      }
    },
    checkAnswer: () => {
      if (exercise && answer && !feedback && !check.isPending) {
        check.mutate({ instanceId: exercise.instance_id, answer });
      }
    },
    /** Pasa al siguiente ejercicio. Devuelve el id del intento si la lección terminó. */
    goNext: (): string | null => {
      if (!feedback) {
        return null;
      }
      if (feedback.attempt_completed || !feedback.next_exercise) {
        return attempt.data?.attempt_id ?? null;
      }
      setCurrent(feedback.next_exercise);
      setAnswer(null);
      setFeedback(null);
      check.reset();
      return null;
    },
  };
}
