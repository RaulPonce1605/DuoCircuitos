import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.core.config import ChallengeKind


class ChallengeRead(BaseModel):
    """Un desafío. La app arma el texto con i18n: `challenges.kind.<kind>` y `goal`."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    period: Literal["daily", "monthly"]
    kind: ChallengeKind
    goal: int
    progress: int
    reward_xp: int
    completed_at: datetime | None


class ChallengesRead(BaseModel):
    daily: list[ChallengeRead]
    monthly: list[ChallengeRead]
    # Cuándo cambian los desafíos: medianoche local del alumno (día siguiente / mes siguiente).
    daily_ends_at: datetime
    monthly_ends_at: datetime
