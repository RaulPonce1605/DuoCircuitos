import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.common import DisplayName, Timezone


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
    # Configuración (docs/diseno/perfil-y-configuracion.md).
    notify_streak_reminder: bool
    notify_challenges: bool
    profile_public: bool
    # Nivel de liga (índice en LEAGUE_TIERS) y su id para traducir el nombre.
    league_tier: int
    league_tier_id: str
    # Tienda: monedas y protectores de racha guardados.
    coins: int
    streak_freezes: int


class UserUpdate(BaseModel):
    """Lo que el alumno puede cambiar en Configuración. Solo se cambia lo que se manda."""

    model_config = ConfigDict(extra="forbid")

    display_name: DisplayName | None = None
    timezone: Timezone | None = None
    notify_streak_reminder: bool | None = None
    notify_challenges: bool | None = None
    profile_public: bool | None = None
