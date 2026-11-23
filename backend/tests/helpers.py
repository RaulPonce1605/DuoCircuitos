"""Ayudas SOLO para pruebas: arman respuestas correctas o incorrectas leyendo la instancia de la
base, como lo haría el backend. La app nunca tiene esta información."""

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.content_import.schema import FillPatternExercise, MultipleChoiceExercise, NumericExercise
from app.models import ExerciseInstance
from app.schemas.exercises import MultipleChoicePublic
from app.services.exercises import get_validator
from app.services.exercises.numeric import correct_value
from app.services.exercises.units import format_quantity


async def answer_for(
    db: AsyncSession, instance_id: str | uuid.UUID, *, correct: bool
) -> dict[str, Any]:
    instance = await db.scalar(
        select(ExerciseInstance)
        .where(ExerciseInstance.id == uuid.UUID(str(instance_id)))
        .options(selectinload(ExerciseInstance.exercise))
        .execution_options(populate_existing=True)
    )
    assert instance is not None
    validator = get_validator(instance.exercise.type)
    spec = validator.parse_spec(instance.exercise.spec)

    if isinstance(spec, MultipleChoiceExercise):
        shown = validator.public_view(spec, instance.state)
        assert isinstance(shown, MultipleChoicePublic)
        right = shown.options.index(spec.options[spec.correct])
        option = right if correct else (right + 1) % len(shown.options)
        return {"type": "multiple_choice", "option": option}
    if isinstance(spec, FillPatternExercise):
        return {"type": "fill_pattern", "text": spec.accepted_answers[0] if correct else "zzz"}
    assert isinstance(spec, NumericExercise)
    value = correct_value(spec, instance.state) * (1 if correct else 3)
    number, unit = format_quantity(value, spec.unit).split(" ")
    return {"type": "numeric", "value": number, "unit": unit}
