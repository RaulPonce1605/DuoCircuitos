import i18n from "@/i18n";
import type { LessonAttempt } from "@/services/lesson-service";

type AttemptRef = Pick<LessonAttempt, "node" | "lesson">;

/** Título de un intento: el de la lección, o "Repaso: Ley de Ohm" para repaso y evaluación. */
export function attemptTitle({ node, lesson }: AttemptRef): string {
  if (lesson) {
    return lesson.title;
  }
  return i18n.t(`summary.nodeTitle.${node.type}`, { unit: node.unit_title });
}
