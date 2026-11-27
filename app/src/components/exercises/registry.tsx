import type { ComponentType } from "react";

import { CircuitDiagram } from "@/components/exercises/circuit_diagram/circuit-diagram";
import { FillPattern } from "@/components/exercises/fill_pattern/fill-pattern";
import { MultipleChoice } from "@/components/exercises/multiple_choice/multiple-choice";
import { NumericAnswer } from "@/components/exercises/numeric/numeric-answer";
import type { ExerciseComponentProps, ExerciseType } from "@/components/exercises/types";

/**
 * Un componente por tipo (app/CLAUDE.md 4.5). Agregar un tipo = agregar su componente aquí;
 * si falta uno, TypeScript no compila. La pantalla de lección nunca hace `switch` por tipo.
 */
export const exerciseRegistry: { [T in ExerciseType]: ComponentType<ExerciseComponentProps<T>> } = {
  multiple_choice: MultipleChoice,
  fill_pattern: FillPattern,
  numeric: NumericAnswer,
  circuit_diagram: CircuitDiagram,
};

/** Renderiza el componente que corresponde al tipo del ejercicio. */
export function ExerciseRenderer<T extends ExerciseType>(props: ExerciseComponentProps<T> & { type: T }) {
  const Component: ComponentType<ExerciseComponentProps<T>> = exerciseRegistry[props.type];
  return <Component exercise={props.exercise} onAnswerChange={props.onAnswerChange} disabled={props.disabled} />;
}
