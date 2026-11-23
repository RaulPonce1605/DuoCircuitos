import unicodedata
from random import Random
from typing import Any

from app.content_import.schema import FillPatternExercise
from app.schemas.exercises import ExerciseAnswer, FillPatternAnswer, FillPatternPublic
from app.services.errors import InvalidAnswer
from app.services.exercises.base import CheckOutcome, ExerciseValidator
from app.services.exercises.registry import register


def normalize(text: str) -> str:
    """Sin distinguir mayúsculas ni espacios (contenido/README.md 2.2)."""
    return "".join(unicodedata.normalize("NFKC", text).casefold().split())


@register("fill_pattern")
class FillPatternValidator(ExerciseValidator[FillPatternExercise]):
    spec_model = FillPatternExercise

    def generate_state(self, spec: FillPatternExercise, rng: Random) -> dict[str, Any]:
        return {}

    def public_view(self, spec: FillPatternExercise, state: dict[str, Any]) -> FillPatternPublic:
        return FillPatternPublic(type="fill_pattern", prompt=spec.prompt)

    def check(
        self, spec: FillPatternExercise, state: dict[str, Any], answer: ExerciseAnswer
    ) -> CheckOutcome:
        if not isinstance(answer, FillPatternAnswer):
            raise InvalidAnswer
        given = normalize(answer.text)
        accepted = {normalize(option) for option in spec.accepted_answers}
        return CheckOutcome(
            correct=given != "" and given in accepted,
            correct_answer=spec.accepted_answers[0],
        )
