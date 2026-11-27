import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from app.core.config import AchievementMetric
from app.schemas.user import EnergyRead


class BadgeRead(BaseModel):
    """Una medalla ganada. La app la nombra con i18n: `achievements.<achievement_id>`."""

    achievement_id: str
    level: int
    # El umbral de ese nivel (p. ej. 7 para "7 días de racha").
    threshold: int
    earned_at: datetime


class AchievementRead(BaseModel):
    id: str
    metric: AchievementMetric
    # Valor actual de la métrica (lecciones completadas, racha más larga...).
    value: int
    thresholds: list[int]
    # Niveles alcanzados (0 = ninguno).
    level: int
    # El siguiente umbral; null si ya alcanzó todos.
    next_threshold: int | None


class AchievementsRead(BaseModel):
    achievements: list[AchievementRead]
    # Las medallas ganadas, de la más reciente a la más antigua.
    badges: list[BadgeRead]


class ChestRewardRead(BaseModel):
    xp: int
    energy: int
    coins: int


class ChestRead(BaseModel):
    id: uuid.UUID
    source: Literal["lesson", "node"]
    # Null mientras no se abre.
    reward: ChestRewardRead | None
    # Medallas que se ganaron al abrirlo (vacío si ya estaba abierto).
    new_badges: list[BadgeRead]
    energy: EnergyRead
