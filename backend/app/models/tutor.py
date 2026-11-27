import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TutorMessage(Base):
    """Conversación del tutor sobre una instancia de ejercicio. También sirve para el límite de
    peticiones: cada respuesta del tutor (`role = 'tutor'`) cuenta como una petición."""

    __tablename__ = "tutor_messages"
    __table_args__ = (
        CheckConstraint("role IN ('student', 'tutor')", name="role_valid"),
        CheckConstraint("(role = 'tutor') = (source IS NOT NULL)", name="source_only_on_tutor"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    exercise_instance_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("exercise_instances.id", ondelete="CASCADE"), index=True
    )
    role: Mapped[str] = mapped_column(String(10))
    # Vacío si el alumno solo pulsó "Pedir ayuda" sin escribir nada.
    content: Mapped[str] = mapped_column(Text)
    # Solo en las del tutor: "llm" (pasó el filtro) o "hint" (pista del temario).
    source: Mapped[str | None] = mapped_column(String(10))
    created_at: Mapped[datetime] = mapped_column(index=True)
