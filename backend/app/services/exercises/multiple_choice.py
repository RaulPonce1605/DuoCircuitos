from random import Random
from typing import Any

from app.content_import.schema import MultipleChoiceExercise
from app.schemas.exercises import ExerciseAnswer, MultipleChoiceAnswer, MultipleChoicePublic
from app.services.errors import InvalidAnswer
from app.services.exercises.base import CheckOutcome, ExerciseValidator
from app.services.exercises.registry import register


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

    @staticmethod
    def _order(spec: MultipleChoiceExercise, state: dict[str, Any]) -> list[int]:
        order = [int(i) for i in state.get("order", [])]
        if sorted(order) != list(range(len(spec.options))):
            # El temario cambió el número de opciones después de crear la instancia.
            return list(range(len(spec.options)))
        return order
