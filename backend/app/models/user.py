import uuid
from datetime import date

from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, CreatedAtMixin


class User(CreatedAtMixin, Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("xp_total >= 0", name="xp_total_non_negative"),
        CheckConstraint("streak_current >= 0", name="streak_current_non_negative"),
        CheckConstraint("streak_longest >= streak_current", name="streak_longest_gte_current"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    # Siempre en minúsculas; lo normaliza el servicio de auth.
    email: Mapped[str] = mapped_column(String(320), unique=True)
    display_name: Mapped[str] = mapped_column(String(50))
    password_hash: Mapped[str] = mapped_column(String(255))
    # Zona horaria IANA (America/Mexico_City): define el "día" de la racha.
    timezone: Mapped[str] = mapped_column(String(64), default="UTC", server_default="UTC")

    xp_total: Mapped[int] = mapped_column(default=0, server_default="0")
    streak_current: Mapped[int] = mapped_column(default=0, server_default="0")
    streak_longest: Mapped[int] = mapped_column(default=0, server_default="0")
    # Último día local en que terminó una lección (para calcular la racha).
    streak_last_date: Mapped[date | None]
