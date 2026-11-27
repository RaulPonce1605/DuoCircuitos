"""Filtro de salida del tutor (backend/CLAUDE.md 3.9). Nunca se desactiva.

Toda respuesta del LLM pasa por aquí. Si revela la solución de la instancia (el resultado en
cualquier prefijo SI y dentro de la tolerancia, la opción correcta o la palabra del patrón), se
descarta y se devuelve la siguiente pista del temario.
"""

from dataclasses import dataclass
from typing import Any, Literal

from app.services.exercises import get_validator

# Una respuesta más larga que esto no es "una pista corta": algo salió mal.
MAX_REPLY_CHARS = 1200


@dataclass(frozen=True)
class GuardedReply:
    text: str
    source: Literal["llm", "hint"]


def reveals_solution(
    exercise_type: str, spec: dict[str, Any], state: dict[str, Any], text: str
) -> bool:
    validator = get_validator(exercise_type)
    return bool(validator.solution_spans(validator.parse_spec(spec), state, text))


def guard_output(
    raw: str | None,
    *,
    exercise_type: str,
    spec: dict[str, Any],
    state: dict[str, Any],
    fallback: str,
) -> GuardedReply:
    text = (raw or "").strip()
    if (
        not text
        or len(text) > MAX_REPLY_CHARS
        or reveals_solution(exercise_type, spec, state, text)
    ):
        return GuardedReply(text=fallback, source="hint")
    return GuardedReply(text=text, source="llm")
