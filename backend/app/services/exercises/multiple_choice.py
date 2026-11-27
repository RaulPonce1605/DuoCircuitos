import re
from random import Random
from typing import Any

from app.content_import.schema import MultipleChoiceExercise
from app.schemas.exercises import ExerciseAnswer, MultipleChoiceAnswer, MultipleChoicePublic
from app.services.errors import InvalidAnswer
from app.services.exercises.base import CheckOutcome, ExerciseValidator
from app.services.exercises.registry import register
from app.services.exercises.text_match import phrase_spans


@register("multiple_choice")
class MultipleChoiceValidator(ExerciseValidator[MultipleChoiceExercise]):
    """Baraja las opciones en cada instancia; el alumno responde con el índice que vio."""

    spec_model = MultipleChoiceExercise

    def generate_state(self, spec: MultipleChoiceExercise, rng: Random) -> dict[str, Any]:
        order = list(range(len(spec.options)))
        rng.shuffle(order)
        return {"order": order}

    def public_view(
        self, spec: MultipleChoiceExercise, state: dict[str, Any]
    ) -> MultipleChoicePublic:
        return MultipleChoicePublic(
            type="multiple_choice",
            prompt=spec.prompt,
            options=[spec.options[i] for i in self._order(spec, state)],
        )

    def check(
        self, spec: MultipleChoiceExercise, state: dict[str, Any], answer: ExerciseAnswer
    ) -> CheckOutcome:
        if not isinstance(answer, MultipleChoiceAnswer):
            raise InvalidAnswer
        order = self._order(spec, state)
        if answer.option >= len(order):
            raise InvalidAnswer
        return CheckOutcome(
            correct=order[answer.option] == spec.correct,
            correct_answer=spec.options[spec.correct],
        )

    def solution_spans(
        self, spec: MultipleChoiceExercise, state: dict[str, Any], text: str
    ) -> list[tuple[int, int]]:
        """El texto de la opción correcta, o su letra/número en el orden mostrado ("la B")."""
        position = self._order(spec, state).index(spec.correct)
        upper = chr(ord("A") + position)
        # Después de "opción"/"inciso" la letra puede ir en minúscula; la "a" sola no, porque
        # es la preposición más común del español.
        any_case = upper if position == 0 else f"[{upper}{upper.lower()}]"
        number = position + 1
        spans = phrase_spans(text, spec.options[spec.correct])
        patterns = [
            # "opción B", "inciso b", "la respuesta es la b", "respuesta: (B)"
            r"(?i:(?<!\w)(?:opci[oó]n|inciso|letra|respuesta|alternativa)(?:\s+correcta)?"
            rf"(?:\s+es)?(?:\s+la)?\s*[:\-]?\s*\(?){any_case}\)?(?!\w)",
            rf"(?i:(?<!\w)(?:opci[oó]n|inciso|alternativa|n[uú]mero))\s*#?\s*{number}(?!\d)",
            # "la B", "es la B", "elige B": aquí solo en mayúscula.
            rf"(?<!\w)(?i:la|es|elige|escoge|marca)\s+\(?{upper}\)?(?!\w)",
            rf"(?<![\w(]){upper}\)",  # "B)"
        ]
        for pattern in patterns:
            spans.extend(match.span() for match in re.finditer(pattern, text))
        return spans

    @staticmethod
    def _order(spec: MultipleChoiceExercise, state: dict[str, Any]) -> list[int]:
        order = [int(i) for i in state.get("order", [])]
        if sorted(order) != list(range(len(spec.options))):
            # El temario cambió el número de opciones después de crear la instancia.
            return list(range(len(spec.options)))
        return order
