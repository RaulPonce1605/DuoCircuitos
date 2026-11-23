import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class NodeProgress(Base):
    """Nodos que un usuario ya completó. Si no hay fila, el nodo no está completado."""

    __tablename__ = "node_progress"
    __table_args__ = (
        CheckConstraint("best_accuracy BETWEEN 0 AND 100", name="best_accuracy_range"),
        CheckConstraint("times_completed >= 1", name="times_completed_positive"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    node_id: Mapped[int] = mapped_column(ForeignKey("nodes.id"), primary_key=True)
    first_completed_at: Mapped[datetime]
    last_completed_at: Mapped[datetime]
    times_completed: Mapped[int] = mapped_column(default=1, server_default="1")
    best_accuracy: Mapped[int | None]
