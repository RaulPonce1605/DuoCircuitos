"""Ejercicios de cálculo con valores sorteados (backend/CLAUDE.md 3.8).

El backend sortea los parámetros, los guarda en la instancia y, al Comprobar, recalcula el
resultado con la fórmula del temario (evaluador seguro, sin `eval`). La respuesta del alumno se
convierte a la unidad base con su prefijo SI y se compara con tolerancia, nunca con `==`.
"""

import math
import re
from random import Random
from typing import Any

from app.content_import.schema import NumericExercise
from app.schemas.exercises import ExerciseAnswer, NumericAnswer, NumericPublic
from app.services.errors import InvalidAnswer
from app.services.exercises.base import CheckOutcome, ExerciseValidator
from app.services.exercises.formula import Formula
from app.services.exercises.registry import register
from app.services.exercises.text_match import quantity_spans
from app.services.exercises.units import (
    InvalidQuantity,
    format_number,
    format_quantity,
    parse_quantity,
)

_PLACEHOLDER = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")


def params_of(spec: NumericExercise, state: dict[str, Any]) -> dict[str, float]:
    params = state.get("params", {})
    return {name: float(params[name]) for name in spec.parameters}


def correct_value(spec: NumericExercise, state: dict[str, Any]) -> float:
    return Formula(spec.solution).evaluate(params_of(spec, state))


def is_within_tolerance(given: float, expected: float, spec: NumericExercise) -> bool:
    """±tolerancia respecto al valor ESPERADO (no simétrica como `math.isclose`, que usa el
    mayor de los dos y aceptaría de más). El factor 1 + 1e-9 absorbe redondeos de punto
    flotante justo en el límite."""
    tolerance = spec.tolerance.value
    allowed = tolerance * abs(expected) if spec.tolerance.type == "relativa" else tolerance
    return math.isfinite(given) and abs(given - expected) <= allowed * (1 + 1e-9)


@register("numeric")
class NumericValidator(ExerciseValidator[NumericExercise]):
    spec_model = NumericExercise

    def generate_state(self, spec: NumericExercise, rng: Random) -> dict[str, Any]:
        return {
            "params": {name: rng.choice(param.values()) for name, param in spec.parameters.items()}
        }

    def public_view(self, spec: NumericExercise, state: dict[str, Any]) -> NumericPublic:
        params = params_of(spec, state)
        prompt = _PLACEHOLDER.sub(lambda m: format_number(params[m.group(1)]), spec.prompt)
        return NumericPublic(type="numeric", prompt=prompt, unit=spec.unit)

    def check(
        self, spec: NumericExercise, state: dict[str, Any], answer: ExerciseAnswer
    ) -> CheckOutcome:
        if not isinstance(answer, NumericAnswer):
            raise InvalidAnswer
        expected = correct_value(spec, state)
        display = format_quantity(expected, spec.unit)
        try:
            given = parse_quantity(answer.value, answer.unit, spec.unit)
        except InvalidQuantity:
            # Un número ilegible o una unidad de otra magnitud cuenta como respuesta incorrecta.
            return CheckOutcome(correct=False, correct_answer=display)
        return CheckOutcome(
            correct=is_within_tolerance(given, expected, spec), correct_answer=display
        )

    def solution_spans(
        self, spec: NumericExercise, state: dict[str, Any], text: str
    ) -> list[tuple[int, int]]:
        """El resultado en cualquier prefijo SI y dentro de la tolerancia ("0.024 A", "24 mA")."""
        expected = correct_value(spec, state)
        return quantity_spans(
            text, spec.unit, lambda value: is_within_tolerance(value, expected, spec)
        )
