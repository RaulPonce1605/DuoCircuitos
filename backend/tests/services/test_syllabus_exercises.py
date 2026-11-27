"""Todos los ejercicios del temario real funcionan con su validador, con varias semillas.

Para cada ejercicio: se genera la instancia, se comprueba que la vista pública no filtre la
solución, que la respuesta correcta se acepte (también con prefijo SI en los numéricos) y que
una respuesta incorrecta se rechace.
"""

from random import Random

import pytest

from app.content_import.schema import (
    CircuitDiagramExercise,
    FillPatternExercise,
    MultipleChoiceExercise,
    NumericExercise,
)
from app.content_import.validate import DEFAULT_SYLLABUS_DIR, validate_syllabus
from app.schemas.exercises import (
    CircuitDiagramAnswer,
    CircuitDiagramPublic,
    FillPatternAnswer,
    MultipleChoiceAnswer,
    MultipleChoicePublic,
    NumericAnswer,
)
from app.services.exercises import get_validator
from app.services.exercises.numeric import correct_value
from app.services.exercises.units import format_quantity

_REPORT = validate_syllabus(DEFAULT_SYLLABUS_DIR)
EXERCISES = [
    exercise for lesson in _REPORT.lessons.values() for exercise in lesson.frontmatter.exercises
]
SEEDS = range(15)


def test_syllabus_is_valid_and_complete() -> None:
    assert _REPORT.ok
    assert len(EXERCISES) == 55


@pytest.mark.parametrize("exercise", EXERCISES, ids=lambda e: e.id)
def test_exercise_round_trip(
    exercise: MultipleChoiceExercise
    | FillPatternExercise
    | NumericExercise
    | CircuitDiagramExercise,
) -> None:
    validator = get_validator(exercise.type)
    spec = validator.parse_spec(exercise.model_dump(mode="json", by_alias=True))

    for seed in SEEDS:
        state = validator.generate_state(spec, Random(seed))
        public = validator.public_view(spec, state)
        assert "{" not in public.prompt, "quedó un {parametro} sin sustituir"

        if isinstance(spec, MultipleChoiceExercise):
            assert isinstance(public, MultipleChoicePublic)
            right = public.options.index(spec.options[spec.correct])
            wrong = (right + 1) % len(public.options)
            ok = MultipleChoiceAnswer(type="multiple_choice", option=right)
            bad = MultipleChoiceAnswer(type="multiple_choice", option=wrong)
            assert validator.check(spec, state, ok).correct
            assert not validator.check(spec, state, bad).correct

        elif isinstance(spec, FillPatternExercise):
            for accepted in spec.accepted_answers:
                answer = FillPatternAnswer(type="fill_pattern", text=accepted.upper())
                assert validator.check(spec, state, answer).correct
            wrong_text = FillPatternAnswer(type="fill_pattern", text="respuesta-incorrecta")
            assert not validator.check(spec, state, wrong_text).correct

        elif isinstance(spec, CircuitDiagramExercise):
            assert isinstance(public, CircuitDiagramPublic)
            # Lo público trae todos los elementos y nada que diga cuáles son los correctos.
            assert {e.id for e in public.elements} == {e.id for e in spec.diagram.elements}
            assert "correct" not in public.model_dump_json()
            ok = CircuitDiagramAnswer(type="circuit_diagram", elements=list(reversed(spec.correct)))
            assert validator.check(spec, state, ok).correct
            touchable = [e.id for e in spec.diagram.elements if e.kind != "cable"]
            extra = [*spec.correct, *(i for i in touchable if i not in spec.correct)][
                : len(spec.correct) + 1
            ]
            assert not validator.check(
                spec, state, CircuitDiagramAnswer(type="circuit_diagram", elements=extra)
            ).correct
            assert not validator.check(
                spec,
                state,
                CircuitDiagramAnswer(type="circuit_diagram", elements=spec.correct[:-1]),
            ).correct

        else:
            assert isinstance(spec, NumericExercise)
            expected = correct_value(spec, state)
            assert expected > 0, "los resultados del temario son positivos"
            # La respuesta "bonita" que se muestra al alumno (3 cifras, con prefijo) se acepta.
            number, unit = format_quantity(expected, spec.unit).split(" ")
            shown = NumericAnswer(type="numeric", value=number, unit=unit)
            assert validator.check(spec, state, shown).correct, f"{number} {unit}"
            plain = NumericAnswer(type="numeric", value=repr(expected), unit=spec.unit)
            assert validator.check(spec, state, plain).correct
            off = NumericAnswer(type="numeric", value=repr(expected * 1.5), unit=spec.unit)
            assert not validator.check(spec, state, off).correct
