import uuid

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, CreatedAtMixin


class XpEvent(CreatedAtMixin, Base):
    """Cada vez que un usuario gana EXP. Las ligas y los desafíos suman estos eventos por
    periodo; `users.xp_total` es el acumulado para no sumarlos en cada lectura."""

    __tablename__ = "xp_events"
    __table_args__ = (CheckConstraint("amount > 0", name="amount_positive"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    amount: Mapped[int]
    # De dónde salió la EXP: "lesson" (fase 1); "chest", "challenge"... en la fase 2.
    source: Mapped[str] = mapped_column(String(30))
    lesson_attempt_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("lesson_attempts.id", ondelete="SET NULL"), unique=True
    )
