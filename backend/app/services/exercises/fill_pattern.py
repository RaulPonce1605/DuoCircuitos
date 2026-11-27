import unicodedata
from collections.abc import Iterable
from random import Random
from typing import Any

from app.content_import.schema import FillPatternExercise
from app.schemas.exercises import ExerciseAnswer, FillPatternAnswer, FillPatternPublic
from app.services.errors import InvalidAnswer
from app.services.exercises.base import CheckOutcome, ExerciseValidator
from app.services.exercises.registry import register
from app.services.exercises.text_match import glued_spans, phrase_spans

BLANK = "___"
# Palabras del enunciado pegadas al hueco que forman el patrón completado ("1/" + "R").
_CONTEXT_CHARS = 6
# Respuestas más cortas ("R", "63") solo se buscan dentro del patrón: sueltas son ambiguas.
_MIN_WORD_LENGTH = 3


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

    def solution_spans(
        self, spec: FillPatternExercise, state: dict[str, Any], text: str
    ) -> list[tuple[int, int]]:
        """Una respuesta aceptada como palabra (si no es muy corta) o el patrón ya completado
        ("G = 1 / R", "63 %"), que atrapa también las respuestas de una o dos letras."""
        before, _, after = spec.prompt.partition(BLANK)
        before_context = _context(reversed(before.split()), reverse=True)
        after_context = _context(after.split(), reverse=False).rstrip(".,;:")
        spans: list[tuple[int, int]] = []
        for answer in spec.accepted_answers:
            if len(normalize(answer)) >= _MIN_WORD_LENGTH:
                spans.extend(phrase_spans(text, answer))
            if BLANK in spec.prompt:
                if before_context:
                    spans.extend(glued_spans(text, [before_context, answer]))
                if after_context:
                    spans.extend(glued_spans(text, [answer, after_context]))
        return spans


def _context(tokens: Iterable[str], *, reverse: bool) -> str:
    """Palabras completas pegadas al hueco, hasta `_CONTEXT_CHARS` caracteres sin espacios."""
    taken: list[str] = []
    for token in tokens:
        if sum(map(len, taken)) + len(token) > _CONTEXT_CHARS:
            break
        taken.append(token)
    return "".join(reversed(taken) if reverse else taken)
