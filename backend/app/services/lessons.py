"""Iniciar una lección y comprobar respuestas (CLAUDE.md 1.2 y docs/diseno/exp-y-racha.md).

- Al iniciar se crea un intento con una instancia por ejercicio; los valores se sortean aquí.
- Las respuestas se validan aquí con el validador del tipo; el cliente nunca recibe la solución
  antes de Comprobar.
- Un fallo vuelve a encolar el ejercicio al final (los numéricos con valores nuevos).
- Al responder bien el último pendiente se entregan EXP, precisión, racha y progreso.
"""

import secrets
import uuid
from datetime import UTC, datetime
from random import Random

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Exercise, ExerciseInstance, LessonAttempt, Node, NodeProgress, User
from app.schemas.exercises import ExerciseAnswer
from app.schemas.lessons import (
    CheckResultRead,
    ExerciseInstanceRead,
    LessonAttemptRead,
    LessonAttemptSummaryRead,
    LessonProgressRead,
    LessonRefRead,
)
from app.services import gamification
from app.services import path as path_service
from app.services.errors import (
    AlreadyAnswered,
    AttemptNotCompleted,
    NotCurrentExercise,
    NotFound,
)
from app.services.exercises import get_validator


async def start_attempt(db: AsyncSession, user: User, lesson_slug: str) -> LessonAttemptRead:
    lesson = await path_service.get_unlocked_lesson(db, user, lesson_slug)
    exercises = list(
        await db.scalars(
            select(Exercise)
            .where(Exercise.lesson_id == lesson.id, Exercise.archived.is_(False))
            .order_by(Exercise.position)
        )
    )
    if not exercises:  # pragma: no cover - el validador del temario exige al menos uno
        raise NotFound
    attempt = LessonAttempt(
        user_id=user.id,
        lesson_id=lesson.id,
        started_at=datetime.now(UTC),
        exercise_count=len(exercises),
    )
    db.add(attempt)
    await db.flush()
    instances = [
        _new_instance(attempt, exercise, position, is_retry=False)
        for position, exercise in enumerate(exercises)
    ]
    db.add_all(instances)
    await db.commit()
    return LessonAttemptRead(
        attempt_id=attempt.id,
        lesson=LessonRefRead(slug=lesson.slug, title=lesson.title),
        progress=LessonProgressRead(completed=0, total=attempt.exercise_count),
        current_exercise=_instance_read(instances[0], exercises[0]),
    )


async def check_answer(
    db: AsyncSession, user: User, instance_id: uuid.UUID, answer: ExerciseAnswer
) -> CheckResultRead:
    instance = await db.scalar(
        select(ExerciseInstance)
        .join(LessonAttempt)
        .where(ExerciseInstance.id == instance_id, LessonAttempt.user_id == user.id)
        .options(selectinload(ExerciseInstance.exercise))
    )
    if instance is None:
        raise NotFound  # no existe o es de otro usuario: misma respuesta
    # Serializa las respuestas de un mismo intento (doble clic, dos pestañas).
    attempt = await db.scalar(
        select(LessonAttempt)
        .where(LessonAttempt.id == instance.attempt_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    if attempt is None:  # pragma: no cover - la instancia acaba de encontrarse con su intento
        raise NotFound
    await db.refresh(instance)
    if instance.answered_at is not None:
        raise AlreadyAnswered
    current = await _current_instance(db, attempt.id)
    if current is None or current.id != instance.id:
        raise NotCurrentExercise

    exercise = instance.exercise
    validator = get_validator(exercise.type)
    outcome = validator.check(validator.parse_spec(exercise.spec), instance.state, answer)

    now = datetime.now(UTC)
    instance.answer = answer.model_dump(mode="json")
    instance.is_correct = outcome.correct
    instance.answered_at = now
    if not outcome.correct:
        retry_position = await _next_position(db, attempt.id)
        db.add(_new_instance(attempt, exercise, retry_position, is_retry=True))
    await db.flush()

    next_instance = await _current_instance(db, attempt.id)
    if next_instance is None:
        await _complete(db, user, attempt, now)
    progress = LessonProgressRead(
        completed=await _solved_count(db, attempt.id), total=attempt.exercise_count
    )
    await db.commit()
    return CheckResultRead(
        correct=outcome.correct,
        correct_answer=outcome.correct_answer,
        explanation=exercise.explanation,
        progress=progress,
        next_exercise=(
            _instance_read(next_instance, next_instance.exercise) if next_instance else None
        ),
        attempt_completed=next_instance is None,
    )


async def get_summary(
    db: AsyncSession, user: User, attempt_id: uuid.UUID
) -> LessonAttemptSummaryRead:
    attempt = await db.scalar(
        select(LessonAttempt)
        .where(LessonAttempt.id == attempt_id, LessonAttempt.user_id == user.id)
        .options(selectinload(LessonAttempt.lesson))
    )
    if attempt is None:
        raise NotFound
    if (
        attempt.completed_at is None
        or attempt.xp_awarded is None
        or attempt.accuracy is None
        or attempt.first_try_correct is None
    ):
        raise AttemptNotCompleted
    return LessonAttemptSummaryRead(
        attempt_id=attempt.id,
        lesson=LessonRefRead(slug=attempt.lesson.slug, title=attempt.lesson.title),
        exercise_count=attempt.exercise_count,
        first_try_correct=attempt.first_try_correct,
        accuracy=attempt.accuracy,
        xp_awarded=attempt.xp_awarded,
        concepts=list(attempt.lesson.concepts),
        streak=gamification.effective_streak(user, datetime.now(UTC)),
        streak_extended=bool(attempt.streak_extended),
    )


# --- Internos --------------------------------------------------------------------------------


def _new_instance(
    attempt: LessonAttempt, exercise: Exercise, position: int, *, is_retry: bool
) -> ExerciseInstance:
    validator = get_validator(exercise.type)
    seed = secrets.randbits(63)  # cabe en BIGINT; con la semilla se reproduce el sorteo
    state = validator.generate_state(validator.parse_spec(exercise.spec), Random(seed))  # noqa: S311
    return ExerciseInstance(
        id=uuid.uuid4(),
        attempt_id=attempt.id,
        exercise_id=exercise.id,
        exercise=exercise,
        position=position,
        seed=seed,
        state=state,
        is_retry=is_retry,
    )


def _instance_read(instance: ExerciseInstance, exercise: Exercise) -> ExerciseInstanceRead:
    validator = get_validator(exercise.type)
    public = validator.public_view(validator.parse_spec(exercise.spec), instance.state)
    return ExerciseInstanceRead(instance_id=instance.id, exercise=public)


async def _current_instance(db: AsyncSession, attempt_id: uuid.UUID) -> ExerciseInstance | None:
    return await db.scalar(
        select(ExerciseInstance)
        .where(ExerciseInstance.attempt_id == attempt_id, ExerciseInstance.answered_at.is_(None))
        .order_by(ExerciseInstance.position)
        .limit(1)
        .options(selectinload(ExerciseInstance.exercise))
    )


async def _next_position(db: AsyncSession, attempt_id: uuid.UUID) -> int:
    last = await db.scalar(
        select(func.max(ExerciseInstance.position)).where(ExerciseInstance.attempt_id == attempt_id)
    )
    return (last or 0) + 1


async def _solved_count(db: AsyncSession, attempt_id: uuid.UUID) -> int:
    solved = await db.scalar(
        select(func.count(func.distinct(ExerciseInstance.exercise_id))).where(
            ExerciseInstance.attempt_id == attempt_id, ExerciseInstance.is_correct.is_(True)
        )
    )
    return int(solved or 0)


async def _complete(db: AsyncSession, user: User, attempt: LessonAttempt, now: datetime) -> None:
    first_try_correct = await db.scalar(
        select(func.count()).where(
            ExerciseInstance.attempt_id == attempt.id,
            ExerciseInstance.is_retry.is_(False),
            ExerciseInstance.is_correct.is_(True),
        )
    )
    # Bloquea al usuario: dos lecciones que terminan a la vez no deben pisarse la EXP ni la racha.
    await db.refresh(user, with_for_update=True)
    rewards = await gamification.award_lesson_completion(
        db, user, attempt, int(first_try_correct or 0), now
    )
    node = await db.scalar(select(Node).where(Node.lesson_id == attempt.lesson_id))
    if node is None:  # pragma: no cover - toda lección del temario tiene su nodo
        return
    progress = await db.get(NodeProgress, (user.id, node.id), with_for_update=True)
    if progress is None:
        db.add(
            NodeProgress(
                user_id=user.id,
                node_id=node.id,
                first_completed_at=now,
                last_completed_at=now,
                times_completed=1,
                best_accuracy=rewards.accuracy,
            )
        )
    else:
        progress.last_completed_at = now
        progress.times_completed += 1
        progress.best_accuracy = max(progress.best_accuracy or 0, rewards.accuracy)
    await db.flush()
