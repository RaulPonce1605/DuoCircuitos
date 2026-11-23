import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.syllabus import Exercise, Lesson


class LessonAttempt(Base):
    """Un intento de lección: se crea al iniciarla y se completa al acertar todos sus ejercicios."""

    __tablename__ = "lesson_attempts"
    __table_args__ = (
        CheckConstraint("accuracy BETWEEN 0 AND 100", name="accuracy_range"),
        CheckConstraint(
            "(completed_at IS NULL) = (xp_awarded IS NULL)", name="xp_only_when_completed"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"), index=True)
    started_at: Mapped[datetime]
    completed_at: Mapped[datetime | None]
    exercise_count: Mapped[int]
    first_try_correct: Mapped[int | None]
    accuracy: Mapped[int | None]
    xp_awarded: Mapped[int | None]

    lesson: Mapped[Lesson] = relationship()
    instances: Mapped[list["ExerciseInstance"]] = relationship(
        back_populates="attempt", order_by="ExerciseInstance.position"
    )


class ExerciseInstance(Base):
    """Un ejercicio tal como se le presentó al alumno: valores sorteados y su respuesta.

    `state` guarda lo que el validador del tipo necesita para recalcular la solución
    (parámetros sorteados, orden de las opciones...). Nunca se envía completo al cliente.
    """

    __tablename__ = "exercise_instances"
    __table_args__ = (UniqueConstraint("attempt_id", "position"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    attempt_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("lesson_attempts.id", ondelete="CASCADE"), index=True
    )
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"), index=True)
    # Orden en la cola de la lección; los reintentos se agregan al final.
    position: Mapped[int]
    seed: Mapped[int] = mapped_column(BigInteger)
    state: Mapped[dict[str, Any]]
    is_retry: Mapped[bool] = mapped_column(default=False, server_default="false")
    answer: Mapped[dict[str, Any] | None]
    is_correct: Mapped[bool | None]
    answered_at: Mapped[datetime | None]

    attempt: Mapped[LessonAttempt] = relationship(back_populates="instances")
    exercise: Mapped[Exercise] = relationship()
