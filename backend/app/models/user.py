import uuid
from datetime import date, datetime

from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, CreatedAtMixin


class User(CreatedAtMixin, Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("xp_total >= 0", name="xp_total_non_negative"),
        CheckConstraint("streak_current >= 0", name="streak_current_non_negative"),
        CheckConstraint("streak_longest >= streak_current", name="streak_longest_gte_current"),
        CheckConstraint("energy_used >= 0", name="energy_used_non_negative"),
        CheckConstraint("league_tier >= 0", name="league_tier_non_negative"),
        CheckConstraint("coins >= 0", name="coins_non_negative"),
        CheckConstraint("streak_freezes >= 0", name="streak_freezes_non_negative"),
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

    # Energía gastada que aún no se recarga (0 = llena). Se guarda lo gastado, no lo que queda,
    # para que cambiar ENERGY_MAX no deje a nadie con más energía que el máximo.
    energy_used: Mapped[int] = mapped_column(default=0, server_default="0")
    # Desde cuándo corre la recarga de la siguiente unidad. Solo importa si energy_used > 0.
    energy_updated_at: Mapped[datetime | None]

    # Configuración: notificaciones (se envían en la fase 3) y privacidad (ligas, amigos).
    notify_streak_reminder: Mapped[bool] = mapped_column(default=True, server_default="true")
    notify_challenges: Mapped[bool] = mapped_column(default=True, server_default="true")
    profile_public: Mapped[bool] = mapped_column(default=True, server_default="true")

    # Nivel de liga (índice en LEAGUE_TIERS). Cambia al cerrar cada semana.
    league_tier: Mapped[int] = mapped_column(default=0, server_default="0")

    # Tienda (docs/diseno/tienda.md).
    coins: Mapped[int] = mapped_column(default=0, server_default="0")
    streak_freezes: Mapped[int] = mapped_column(default=0, server_default="0")
