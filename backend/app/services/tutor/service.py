"""Tutor con IA: "Pedir ayuda" durante un ejercicio (CLAUDE.md 1.4, backend/CLAUDE.md 3.9).

    prompt = build_prompt(...)              solo temario, sin la solución
    raw = await provider.complete(prompt)   el adaptador del proveedor configurado
    guard_output(raw, ..., fallback=pista)  si revela la solución, va la pista del temario

Sin proveedor configurado (o si falla) el tutor responde con la siguiente pista del temario.
Cada respuesta cuenta para el límite por hora y por ejercicio.
"""

import logging
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.models import Exercise, ExerciseInstance, LessonAttempt, TutorMessage, User
from app.schemas.tutor import TutorReplyRead
from app.services.errors import AlreadyAnswered, NotFound, TutorExerciseLimit, TutorRateLimited
from app.services.tutor.guard import guard_output
from app.services.tutor.prompt import TutorTurn, build_prompt
from app.services.tutor.provider import TutorProvider, TutorProviderError

logger = logging.getLogger(__name__)


async def ask(
    db: AsyncSession,
    user: User,
    instance_id: uuid.UUID,
    message: str | None,
    provider: TutorProvider | None,
    now: datetime | None = None,
) -> TutorReplyRead:
    now = now or datetime.now(UTC)
    settings = get_settings()
    instance = await db.scalar(
        select(ExerciseInstance)
        .join(LessonAttempt)
        .where(ExerciseInstance.id == instance_id, LessonAttempt.user_id == user.id)
        .options(selectinload(ExerciseInstance.exercise).selectinload(Exercise.lesson))
    )
    if instance is None:
        raise NotFound  # no existe o es de otro usuario
    if instance.answered_at is not None:
        raise AlreadyAnswered  # la ayuda es para el ejercicio que se está resolviendo

    used_this_hour = await _tutor_replies(db, user.id, since=now - timedelta(hours=1))
    if used_this_hour >= settings.tutor_requests_per_hour:
        raise TutorRateLimited
    history = await _history(db, instance.id)
    level = sum(1 for turn in history if turn.role == "tutor")
    if level >= settings.tutor_requests_per_exercise:
        raise TutorExerciseLimit

    exercise = instance.exercise
    hints = list(exercise.hints)
    fallback = hints[min(level, len(hints) - 1)]
    text = message.strip() if message else None

    raw: str | None = None
    if provider is not None:
        prompt = build_prompt(
            exercise_type=exercise.type,
            spec=exercise.spec,
            state=instance.state,
            lesson_title=exercise.lesson.title,
            concepts=list(exercise.lesson.concepts),
            theory=exercise.lesson.theory,
            hints=hints,
            history=history,
            message=text,
        )
        try:
            raw = await provider.complete(prompt)
        except TutorProviderError:
            logger.warning("el proveedor del tutor no respondió; se usa la pista del temario")
    reply = guard_output(
        raw,
        exercise_type=exercise.type,
        spec=exercise.spec,
        state=instance.state,
        fallback=fallback,
    )

    db.add_all(
        [
            TutorMessage(
                user_id=user.id,
                exercise_instance_id=instance.id,
                role="student",
                content=text or "",
                created_at=now,
            ),
            TutorMessage(
                user_id=user.id,
                exercise_instance_id=instance.id,
                role="tutor",
                content=reply.text,
                source=reply.source,
                created_at=now,
            ),
        ]
    )
    await db.commit()
    return TutorReplyRead(
        reply=reply.text,
        source=reply.source,
        help_level=level + 1,
        remaining_requests=max(
            0,
            min(
                settings.tutor_requests_per_hour - used_this_hour - 1,
                settings.tutor_requests_per_exercise - level - 1,
            ),
        ),
    )


async def _tutor_replies(db: AsyncSession, user_id: uuid.UUID, *, since: datetime) -> int:
    count = await db.scalar(
        select(func.count()).where(
            TutorMessage.user_id == user_id,
            TutorMessage.role == "tutor",
            TutorMessage.created_at > since,
        )
    )
    return int(count or 0)


async def _history(db: AsyncSession, instance_id: uuid.UUID) -> list[TutorTurn]:
    rows = await db.scalars(
        select(TutorMessage)
        .where(TutorMessage.exercise_instance_id == instance_id)
        # Mismo `created_at` para la pregunta y su respuesta: la del alumno va primero.
        .order_by(TutorMessage.created_at, TutorMessage.role)
    )
    return [
        TutorTurn(role="student" if row.role == "student" else "tutor", content=row.content)
        for row in rows
    ]
