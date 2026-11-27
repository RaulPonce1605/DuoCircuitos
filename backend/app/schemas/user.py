import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EnergyRead(BaseModel):
    current: int
    max: int
    # Cuándo se recarga la siguiente unidad; null si está llena.
    next_refill_at: datetime | None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    display_name: str
    timezone: str
    xp_total: int
    streak_current: int
    streak_longest: int
    created_at: datetime
    energy: EnergyRead
