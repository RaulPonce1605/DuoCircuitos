import type { components } from "@/api/schema";

type Schemas = components["schemas"];

/** Lo que ve el alumno (sin solución) y lo que responde, tal como los define el backend. */
export type ExercisePublic =
  | Schemas["MultipleChoicePublic"]
  | Schemas["FillPatternPublic"]
  | Schemas["NumericPublic"]
  | Schemas["CircuitDiagramPublic"];
export type ExerciseAnswer = Schemas["CheckRequest"]["answer"];
export type ExerciseType = ExercisePublic["type"];

export type ExerciseOf<T extends ExerciseType> = Extract<ExercisePublic, { type: T }>;
export type AnswerOf<T extends ExerciseType> = Extract<ExerciseAnswer, { type: T }>;

/**
 * Contrato de un componente de ejercicio: muestra el ejercicio y avisa la respuesta armada
 * (o `null` si aún está incompleta). NO valida: eso lo hace el backend al Comprobar.
 */
export type ExerciseComponentProps<T extends ExerciseType> = {
  exercise: ExerciseOf<T>;
  onAnswerChange: (answer: AnswerOf<T> | null) => void;
  /** Después de Comprobar ya no se puede cambiar la respuesta. */
  disabled: boolean;
};
