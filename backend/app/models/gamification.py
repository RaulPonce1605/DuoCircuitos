import uuid
from datetime import date, datetime

from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint
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
    # De dónde salió la EXP: "lesson", "chest" o "challenge".
    source: Mapped[str] = mapped_column(String(30))
    lesson_attempt_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("lesson_attempts.id", ondelete="SET NULL"), unique=True
    )


class Chest(CreatedAtMixin, Base):
    """Un cofre del alumno. `source = 'lesson'`: el que sale al terminar un intento.
    `source = 'node'`: el nodo cofre del camino (uno por alumno y nodo). El premio se sortea al
    abrirlo y queda guardado: abrirlo otra vez no da más."""

    __tablename__ = "chests"
    __table_args__ = (
        CheckConstraint("source IN ('lesson', 'node')", name="source_valid"),
        CheckConstraint(
            "(source = 'lesson') = (lesson_attempt_id IS NOT NULL)", name="attempt_only_on_lesson"
        ),
        CheckConstraint("(source = 'node') = (node_id IS NOT NULL)", name="node_only_on_node"),
        CheckConstraint(
            "(opened_at IS NULL) = (reward_xp IS NULL) "
            "AND (opened_at IS NULL) = (reward_energy IS NULL)",
            name="reward_only_when_opened",
        ),
        UniqueConstraint("user_id", "node_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    source: Mapped[str] = mapped_column(String(10))
    lesson_attempt_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("lesson_attempts.id", ondelete="CASCADE"), unique=True
    )
    node_id: Mapped[int | None] = mapped_column(ForeignKey("nodes.id"))
    opened_at: Mapped[datetime | None]
    reward_xp: Mapped[int | None]
    reward_energy: Mapped[int | None]
    reward_coins: Mapped[int | None]


class Badge(Base):
    """Medalla: un nivel alcanzado de un logro (`achievement_id` es el id del logro en la
    configuración). Si se ganó al terminar un intento, `lesson_attempt_id` lo dice (el resumen
    la celebra)."""

    __tablename__ = "badges"
    __table_args__ = (CheckConstraint("level >= 1", name="level_positive"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    achievement_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    level: Mapped[int] = mapped_column(primary_key=True)
    earned_at: Mapped[datetime]
    lesson_attempt_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("lesson_attempts.id", ondelete="SET NULL"), index=True
    )


class Challenge(CreatedAtMixin, Base):
    """Un desafío del alumno en un periodo: diario (`period_start` = su día local) o mensual
    (el día 1 del mes). Se generan solos al leerlos o al ganar EXP; nunca se editan a mano."""

    __tablename__ = "challenges"
    __table_args__ = (
        CheckConstraint("period IN ('daily', 'monthly')", name="period_valid"),
        CheckConstraint("goal > 0", name="goal_positive"),
        CheckConstraint("progress >= 0 AND progress <= goal", name="progress_range"),
        UniqueConstraint("user_id", "period", "period_start", "kind"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    period: Mapped[str] = mapped_column(String(10))
    period_start: Mapped[date]
    kind: Mapped[str] = mapped_column(String(30))
    goal: Mapped[int]
    progress: Mapped[int] = mapped_column(default=0, server_default="0")
    reward_xp: Mapped[int]
    completed_at: Mapped[datetime | None]


class LeagueGroup(CreatedAtMixin, Base):
    """Un grupo de liga de una semana (`week_start` = lunes, UTC) en un nivel. Se cierra la
    primera vez que alguien lo consulta después de que termina la semana."""

    __tablename__ = "league_groups"
    __table_args__ = (CheckConstraint("tier >= 0", name="tier_non_negative"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    week_start: Mapped[date] = mapped_column(index=True)
    tier: Mapped[int]
    closed_at: Mapped[datetime | None]


class LeagueMember(Base):
    """Un alumno en el grupo de una semana. La EXP de la semana no se guarda aquí: se suma de
    `xp_events`. Al cerrar el grupo se guardan el lugar final y el resultado."""

    __tablename__ = "league_members"
    __table_args__ = (
        UniqueConstraint("user_id", "week_start"),
        CheckConstraint(
            "result IS NULL OR result IN ('promoted', 'stayed', 'demoted')", name="result_valid"
        ),
    )

    group_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("league_groups.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    # Repetido del grupo para que un alumno no esté en dos grupos la misma semana.
    week_start: Mapped[date]
    joined_at: Mapped[datetime]
    final_rank: Mapped[int | None]
    final_xp: Mapped[int | None]
    result: Mapped[str | None] = mapped_column(String(10))
    # Cuándo vio el alumno su resultado (la app lo anuncia una sola vez).
    result_seen_at: Mapped[datetime | None]


class Purchase(CreatedAtMixin, Base):
    """Una compra en la tienda (historial). `item` es el id del artículo en la configuración."""

    __tablename__ = "purchases"
    __table_args__ = (CheckConstraint("price > 0", name="price_positive"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    item: Mapped[str] = mapped_column(String(30))
    price: Mapped[int]


class StreakFreezeUse(Base):
    """Un día sin práctica que un protector de racha cubrió (para mostrarlo al alumno)."""

    __tablename__ = "streak_freeze_uses"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    day: Mapped[date] = mapped_column(primary_key=True)
    used_at: Mapped[datetime]
