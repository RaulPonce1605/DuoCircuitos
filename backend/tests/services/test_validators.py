from random import Random
from typing import Any

import pytest

from app.content_import.schema import (
    FillPatternExercise,
    MultipleChoiceExercise,
    NumericExercise,
)
from app.schemas.exercises import (
    FillPatternAnswer,
    MultipleChoiceAnswer,
    MultipleChoicePublic,
    NumericAnswer,
    NumericPublic,
)
from app.services.errors import InvalidAnswer, UnknownExerciseType
from app.services.exercises import get_validator, registered_types
from app.services.exercises.registry import register

COMMON = {"explicacion": "e", "pistas": ["a", "b"]}

MC = MultipleChoiceExercise.model_validate(
    COMMON
    | {
        "id": "mc",
        "tipo": "multiple_choice",
        "enunciado": "¿Cómo se conecta un amperímetro?",
        "opciones": ["En paralelo", "En serie", "No importa"],
        "correcta": 1,
    }
)
FILL = FillPatternExercise.model_validate(
    COMMON
    | {
        "id": "fill",
        "tipo": "fill_pattern",
        "enunciado": "V = I · ___",
        "respuestas_aceptadas": ["R", "Resistencia"],
    }
)
NUM = NumericExercise.model_validate(
    COMMON
    | {
        "id": "num",
        "tipo": "numeric",
        "enunciado": "Un resistor de {R} Ω se conecta a {V} V. ¿Qué corriente circula?",
        "parametros": {
            "V": {"min": 5, "max": 5, "paso": 1},
            "R": {"min": 220, "max": 220, "paso": 10},
        },
        "solucion": "V / R",
        "unidad": "A",
        "tolerancia": {"tipo": "relativa", "valor": 0.02},
    }
)


def test_registry_has_the_three_mvp_types() -> None:
    assert registered_types() == {"multiple_choice", "fill_pattern", "numeric"}


def test_unknown_type_raises() -> None:
    with pytest.raises(UnknownExerciseType):
        get_validator("circuit_diagram")


def test_cannot_register_a_type_twice() -> None:
    with pytest.raises(ValueError, match="ya hay un validador"):

        @register("numeric")  # type: ignore[type-var]
        class Duplicate:  # pragma: no cover - nunca se instancia
            pass


# --- Opción múltiple -------------------------------------------------------------------------


def _mc_state(seed: int) -> dict[str, Any]:
    return get_validator("multiple_choice").generate_state(MC, Random(seed))


def test_mc_public_view_is_a_shuffle_without_the_answer() -> None:
    validator = get_validator("multiple_choice")
    public = validator.public_view(MC, _mc_state(1))

    assert isinstance(public, MultipleChoicePublic)
    assert sorted(public.options) == sorted(MC.options)
    assert "correct" not in public.model_dump()


def test_mc_shuffle_is_reproducible_and_varies() -> None:
    validator = get_validator("multiple_choice")
    assert _mc_state(7) == _mc_state(7)
    orders = {tuple(validator.generate_state(MC, Random(s))["order"]) for s in range(30)}
    assert len(orders) > 1


@pytest.mark.parametrize("seed", range(10))
def test_mc_check_maps_the_shown_index(seed: int) -> None:
    validator = get_validator("multiple_choice")
    state = _mc_state(seed)
    shown = validator.public_view(MC, state)
    assert isinstance(shown, MultipleChoicePublic)
    right = shown.options.index("En serie")

    for index in range(len(shown.options)):
        outcome = validator.check(
            MC, state, MultipleChoiceAnswer(type="multiple_choice", option=index)
        )
        assert outcome.correct is (index == right)
        assert outcome.correct_answer == "En serie"


def test_mc_out_of_range_or_wrong_type_is_invalid() -> None:
    validator = get_validator("multiple_choice")
    with pytest.raises(InvalidAnswer):
        validator.check(MC, _mc_state(0), MultipleChoiceAnswer(type="multiple_choice", option=3))
    with pytest.raises(InvalidAnswer):
        validator.check(MC, _mc_state(0), FillPatternAnswer(type="fill_pattern", text="x"))


# --- Completar patrón ------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "correct"),
    [
        ("R", True),
        ("r", True),
        ("  R ", True),
        ("resistencia", True),
        ("RESIS TENCIA", True),
        ("I", False),
        ("", False),
        ("   ", False),
        ("Resistencias", False),
    ],
)
def test_fill_pattern(text: str, correct: bool) -> None:
    validator = get_validator("fill_pattern")
    outcome = validator.check(FILL, {}, FillPatternAnswer(type="fill_pattern", text=text))
    assert outcome.correct is correct
    assert outcome.correct_answer == "R"


# --- Numérico --------------------------------------------------------------------------------


def _num_state() -> dict[str, Any]:
    return get_validator("numeric").generate_state(NUM, Random(0))


def test_numeric_public_view_substitutes_params_and_hides_solution() -> None:
    public = get_validator("numeric").public_view(NUM, _num_state())

    assert isinstance(public, NumericPublic)
    assert public.prompt == "Un resistor de 220 Ω se conecta a 5 V. ¿Qué corriente circula?"
    assert public.unit == "A"
    dumped = str(public.model_dump())
    assert "V / R" not in dumped and "0.0227" not in dumped


@pytest.mark.parametrize(
    ("value", "unit", "correct"),
    [
        ("0.0227", "A", True),
        ("22.7", "mA", True),
        ("22,7", "mA", True),
        ("2.27e-2", "A", True),
        ("23", "mA", True),  # 1.2 % de error, dentro de ±2 %
        ("24", "mA", False),  # 5.6 % de error
        ("22.7", "A", False),  # prefijo olvidado: 1000 veces más
        ("22.7", "mV", False),  # otra magnitud
        ("hola", "mA", False),
        ("", "mA", False),
    ],
)
def test_numeric_check(value: str, unit: str, correct: bool) -> None:
    outcome = get_validator("numeric").check(
        NUM, _num_state(), NumericAnswer(type="numeric", value=value, unit=unit)
    )
    assert outcome.correct is correct
    assert outcome.correct_answer == "22.7 mA"


def test_numeric_tolerance_boundaries() -> None:
    validator = get_validator("numeric")
    expected = 5 / 220

    def check(value: float) -> bool:
        answer = NumericAnswer(type="numeric", value=repr(value), unit="A")
        return validator.check(NUM, _num_state(), answer).correct

    assert check(expected * 1.0199)
    assert check(expected * 0.9801)
    assert not check(expected * 1.0201)
    assert not check(expected * 0.9799)


def test_numeric_absolute_tolerance() -> None:
    spec = NUM.model_copy(
        update={"tolerance": NUM.tolerance.model_copy(update={"type": "absoluta", "value": 0.001})}
    )
    validator = get_validator("numeric")
    state = validator.generate_state(spec, Random(0))

    def check(value: str) -> bool:
        answer = NumericAnswer(type="numeric", value=value, unit="A")
        return validator.check(spec, state, answer).correct

    assert check("0.0235")  # 0.0227 + 0.0008
    assert not check("0.0240")  # 0.0227 + 0.0013


def test_numeric_wrong_answer_type_is_invalid() -> None:
    with pytest.raises(InvalidAnswer):
        get_validator("numeric").check(
            NUM, _num_state(), MultipleChoiceAnswer(type="multiple_choice", option=0)
        )
