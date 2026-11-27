"""Prueba obligatoria 2 (backend/CLAUDE.md 3.9): el filtro de salida bloquea al proveedor falso
que intenta filtrar la respuesta, en cualquier forma, y deja pasar las pistas normales."""

from typing import Any

import pytest

from app.content_import.schema import (
    FillPatternExercise,
    MultipleChoiceExercise,
    NumericExercise,
)
from app.services.tutor import guard_output

FALLBACK = "PISTA DEL TEMARIO"
PISTAS = ["Usa la Ley de Ohm.", "Despeja I de V = I · R."]

# I = V / R = 12 V / 500 Ω = 0.024 A = 24 mA
NUMERIC = NumericExercise.model_validate(
    {
        "id": "ohm-corriente",
        "tipo": "numeric",
        "enunciado": "Un resistor de {R} Ω está conectado a {V} V. ¿Qué corriente pasa?",
        "parametros": {
            "V": {"min": 6, "max": 24, "paso": 6},
            "R": {"min": 100, "max": 1000, "paso": 100},
        },
        "solucion": "V / R",
        "unidad": "A",
        "tolerancia": {"tipo": "relativa", "valor": 0.02},
        "explicacion": "I = V / R",
        "pistas": PISTAS,
    }
).model_dump(mode="json", by_alias=True)
NUMERIC_STATE = {"params": {"V": 12, "R": 500}}

# Con este orden la opción correcta ("Ohm") se muestra en la posición B.
MULTIPLE_CHOICE = MultipleChoiceExercise.model_validate(
    {
        "id": "unidad-resistencia",
        "tipo": "multiple_choice",
        "enunciado": "¿En qué unidad se mide la resistencia eléctrica?",
        "opciones": ["Volt", "Ampere", "Ohm", "Watt"],
        "correcta": 2,
        "explicacion": "La resistencia se mide en ohms.",
        "pistas": ["Piensa qué mide cada opción.", "Lleva el apellido de un físico alemán."],
    }
).model_dump(mode="json", by_alias=True)
MULTIPLE_CHOICE_STATE = {"order": [0, 2, 1, 3]}  # Volt, Ohm, Ampere, Watt

FILL_PATTERN = FillPatternExercise.model_validate(
    {
        "id": "conductancia",
        "tipo": "fill_pattern",
        "enunciado": "Completa la definición de conductancia: G = 1 / ___",
        "respuestas_aceptadas": ["R", "resistencia"],
        "explicacion": "G = 1 / R",
        "pistas": ["Es lo contrario de la oposición al paso de la corriente.", "Se mide en ohms."],
    }
).model_dump(mode="json", by_alias=True)


def _guard(raw: str, exercise_type: str, spec: dict[str, Any], state: dict[str, Any]) -> str:
    reply = guard_output(
        raw, exercise_type=exercise_type, spec=spec, state=state, fallback=FALLBACK
    )
    assert (reply.source == "hint") == (reply.text == FALLBACK)
    return reply.text


@pytest.mark.parametrize(
    "leak",
    [
        "0.024 A",
        "La corriente es de 24 mA.",
        "I = 0,024 A",
        "Te debe dar 2.4e-2 A",
        "Son 24 × 10⁻³ A",
        "24 x 10^-3 A",
        "24000 µA",
        "24000 uA",
        "La corriente vale 24.",  # sin unidad: podría ser 24 mA
        "Resultado: 0.0241",  # dentro de la tolerancia del 2 %
        "Más o menos 23.8 mA",
        "Ya casi:\n1. Divide.\n2. Te da 24 mA.",
    ],
)
def test_blocks_the_numeric_result_in_any_form(leak: str) -> None:
    assert _guard(leak, "numeric", NUMERIC, NUMERIC_STATE) == FALLBACK


@pytest.mark.parametrize(
    "hint",
    [
        "Usa la Ley de Ohm: divide el voltaje entre la resistencia.",
        "Tienes 12 V y 500 Ω. ¿Qué fórmula relaciona esas magnitudes?",
        "1. Identifica V.\n2. Identifica R.\n3. Despeja I.",
        "Revisa las unidades: el resultado sale en amperes, pero puedes usar mA.",
        "Si el resultado te sale de 6 A, revisa los ceros de la resistencia.",
    ],
)
def test_lets_numeric_hints_through(hint: str) -> None:
    assert _guard(hint, "numeric", NUMERIC, NUMERIC_STATE) == hint


@pytest.mark.parametrize(
    "leak",
    [
        "La respuesta es la B",
        "la respuesta es la b",
        "Es la B.",
        "Elige B",
        "Opción B",
        "inciso b",
        "La opción correcta es la b)",
        "B) es la buena",
        "Opción 2",
        "Se mide en ohms.",
        "La respuesta es Ohm",
        "OHM",
    ],
)
def test_blocks_the_correct_option(leak: str) -> None:
    assert _guard(leak, "multiple_choice", MULTIPLE_CHOICE, MULTIPLE_CHOICE_STATE) == FALLBACK


@pytest.mark.parametrize(
    "hint",
    [
        "Piensa qué magnitud mide cada una de las opciones.",
        "El volt mide voltaje, así que esa no es.",
        "A la resistencia se le opone la corriente... ¿qué unidad viene de un apellido?",
        "La opción A mide voltaje.",
    ],
)
def test_lets_multiple_choice_hints_through(hint: str) -> None:
    assert _guard(hint, "multiple_choice", MULTIPLE_CHOICE, MULTIPLE_CHOICE_STATE) == hint


@pytest.mark.parametrize(
    "leak",
    ["G = 1 / R", "g=1/r", "Va la resistencia.", "Es la RESISTENCIA", "La Resistencia."],
)
def test_blocks_the_fill_pattern_answer(leak: str) -> None:
    assert _guard(leak, "fill_pattern", FILL_PATTERN, {}) == FALLBACK


@pytest.mark.parametrize(
    "hint",
    [
        "La conductancia es lo contrario de la oposición al paso de la corriente.",
        "Recuerda que R se mide en ohms y G en siemens.",
    ],
)
def test_lets_fill_pattern_hints_through(hint: str) -> None:
    assert _guard(hint, "fill_pattern", FILL_PATTERN, {}) == hint


@pytest.mark.parametrize("raw", [None, "", "   ", "x" * 5000])
def test_empty_or_huge_replies_fall_back_to_the_hint(raw: str | None) -> None:
    reply = guard_output(
        raw, exercise_type="numeric", spec=NUMERIC, state=NUMERIC_STATE, fallback=FALLBACK
    )
    assert reply.text == FALLBACK
    assert reply.source == "hint"
