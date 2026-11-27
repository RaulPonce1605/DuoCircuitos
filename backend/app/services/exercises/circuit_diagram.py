"""Identificar elementos en un diagrama de circuito (CLAUDE.md 1.3, contenido/README.md).

El alumno toca uno o varios elementos del diagrama; es correcto si tocó exactamente los de
`correctos` (el orden no importa). El diagrama público trae todos los elementos sin decir cuáles
son los correctos.
"""

from random import Random
from typing import Any

from app.content_import.schema import CircuitDiagramExercise, DiagramKind
from app.schemas.exercises import (
    CircuitDiagramAnswer,
    CircuitDiagramPublic,
    DiagramElementKind,
    DiagramElementPublic,
    DiagramNodePublic,
    ExerciseAnswer,
    GridPoint,
)
from app.services.errors import InvalidAnswer
from app.services.exercises.base import CheckOutcome, ExerciseValidator
from app.services.exercises.registry import register
from app.services.exercises.text_match import phrase_spans


def _point(point: tuple[int, int]) -> GridPoint:
    return GridPoint(x=point[0], y=point[1])


# El temario usa nombres en español; la API, en inglés (CLAUDE.md 5.1).
KIND_IN_API: dict[DiagramKind, DiagramElementKind] = {
    "cable": "wire",
    "resistor": "resistor",
    "capacitor": "capacitor",
    "inductor": "inductor",
    "fuente_voltaje": "voltage_source",
    "fuente_corriente": "current_source",
    "amperimetro": "ammeter",
    "voltimetro": "voltmeter",
    "interruptor": "switch",
    "foco": "lamp",
}


@register("circuit_diagram")
class CircuitDiagramValidator(ExerciseValidator[CircuitDiagramExercise]):
    spec_model = CircuitDiagramExercise

    def generate_state(self, spec: CircuitDiagramExercise, rng: Random) -> dict[str, Any]:
        return {}

    def public_view(
        self, spec: CircuitDiagramExercise, state: dict[str, Any]
    ) -> CircuitDiagramPublic:
        return CircuitDiagramPublic(
            type="circuit_diagram",
            prompt=spec.prompt,
            elements=[
                DiagramElementPublic(
                    id=element.id,
                    kind=KIND_IN_API[element.kind],
                    start=_point(element.start),
                    end=_point(element.end),
                    label=element.label,
                )
                for element in spec.diagram.elements
            ],
            nodes=[
                DiagramNodePublic(point=_point(node.point), label=node.label)
                for node in spec.diagram.nodes
            ],
        )

    def check(
        self, spec: CircuitDiagramExercise, state: dict[str, Any], answer: ExerciseAnswer
    ) -> CheckOutcome:
        if not isinstance(answer, CircuitDiagramAnswer):
            raise InvalidAnswer
        touchable = {e.id for e in spec.diagram.elements if e.kind != "cable"}
        chosen = set(answer.elements)
        if not chosen <= touchable:
            raise InvalidAnswer  # ids que no existen o cables: no viene de la app
        labels = spec.correct_labels()
        display = labels[0] if len(labels) == 1 else ", ".join(labels[:-1]) + f" y {labels[-1]}"
        return CheckOutcome(correct=chosen == set(spec.correct), correct_answer=display)

    def solution_spans(
        self, spec: CircuitDiagramExercise, state: dict[str, Any], text: str
    ) -> list[tuple[int, int]]:
        """Las etiquetas de los elementos correctos ("R2", "C1")."""
        return [
            span
            for label in spec.correct_labels()
            for span in phrase_spans(text, label, plural=False)
        ]
