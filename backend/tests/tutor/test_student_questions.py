"""Las preguntas típicas de alumnos (preguntas_alumnos.yaml) contra el tutor, con un ejercicio de
cada tipo del temario real y un proveedor FALSO que "se deja convencer": si la pregunta intenta
sacar la respuesta, responde con la solución, y el filtro debe bloquearla."""

from datetime import UTC, datetime
from pathlib import Path
from random import Random
from typing import Any

import pytest
import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.content_import.schema import (
    CircuitDiagramExercise,
    FillPatternExercise,
    MultipleChoiceExercise,
    NumericExercise,
)
from app.core.config import get_settings
from app.models import Exercise, ExerciseInstance, LessonAttempt, Node, User
from app.services.auth import Session
from app.services.exercises import get_validator
from app.services.exercises.numeric import correct_value
from app.services.exercises.units import format_quantity
from app.services.tutor import TutorPrompt
from app.services.tutor import service as tutor_service
from tests.helpers import FakeTutorProvider

QUESTIONS: list[dict[str, Any]] = yaml.safe_load(
    (Path(__file__).parent / "preguntas_alumnos.yaml").read_text(encoding="utf-8")
)["preguntas"]
BENIGN = "Empieza por identificar qué magnitudes te dan y cuál te piden."
TYPES = ["numeric", "multiple_choice", "fill_pattern", "circuit_diagram"]


def test_question_list_has_both_kinds() -> None:
    kinds = [question["intenta_sacar_respuesta"] for question in QUESTIONS]
    assert kinds.count(True) >= 10
    assert kinds.count(False) >= 10


def _solution_text(exercise: Exercise, state: dict[str, Any]) -> str:
    """Lo que diría un modelo que sí regala la respuesta."""
    validator = get_validator(exercise.type)
    spec = validator.parse_spec(exercise.spec)
    if isinstance(spec, NumericExercise):
        return f"El resultado es {format_quantity(correct_value(spec, state), spec.unit)}."
    if isinstance(spec, MultipleChoiceExercise):
        letter = "ABCDEFGH"[[int(i) for i in state["order"]].index(spec.correct)]
        return f"La respuesta es la {letter}: {spec.options[spec.correct]}."
    if isinstance(spec, CircuitDiagramExercise):
        return f"Toca {' y '.join(spec.correct_labels())}."
    assert isinstance(spec, FillPatternExercise)
    return f"Va la palabra {spec.accepted_answers[-1]}."


async def _instance(db: AsyncSession, user: User, exercise_type: str) -> ExerciseInstance:
    exercise = await db.scalar(
        select(Exercise)
        .where(Exercise.type == exercise_type)
        .order_by(Exercise.id)
        .limit(1)
        .options(selectinload(Exercise.lesson))
    )
    assert exercise is not None
    node_id = await db.scalar(select(Node.id).where(Node.lesson_id == exercise.lesson_id))
    assert node_id is not None
    attempt = LessonAttempt(
        user_id=user.id,
        node_id=node_id,
        lesson_id=exercise.lesson_id,
        started_at=datetime.now(UTC),
        exercise_count=1,
    )
    db.add(attempt)
    await db.flush()
    validator = get_validator(exercise.type)
    instance = ExerciseInstance(
        attempt_id=attempt.id,
        exercise_id=exercise.id,
        exercise=exercise,
        position=0,
        seed=7,
        state=validator.generate_state(validator.parse_spec(exercise.spec), Random(7)),
    )
    db.add(instance)
    await db.flush()
    return instance


@pytest.mark.usefixtures("syllabus")
@pytest.mark.parametrize("exercise_type", TYPES)
async def test_every_student_question(
    db: AsyncSession,
    user_session: Session,
    exercise_type: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(get_settings(), "tutor_requests_per_exercise", 1000)
    monkeypatch.setattr(get_settings(), "tutor_requests_per_hour", 1000)
    user = user_session.user
    instance = await _instance(db, user, exercise_type)
    leak = _solution_text(instance.exercise, instance.state)

    current: dict[str, Any] = {}

    def _reply(_: TutorPrompt) -> str:
        return leak if current["intenta_sacar_respuesta"] else BENIGN

    provider = FakeTutorProvider(_reply)
    for question in QUESTIONS:
        current.update(question)
        reply = await tutor_service.ask(db, user, instance.id, question["texto"] or None, provider)
        if question["intenta_sacar_respuesta"]:
            assert reply.source == "hint", question["texto"]
            assert reply.reply in instance.exercise.hints
        else:
            assert reply.source == "llm", question["texto"]
            assert reply.reply == BENIGN
        # La pregunta del alumno nunca entra al system prompt, solo como mensaje de usuario.
        if question["texto"]:
            assert question["texto"] not in provider.prompts[-1].system
