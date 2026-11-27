from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel


class LeagueMemberRead(BaseModel):
    rank: int
    # Null si el alumno tiene el perfil privado (la app muestra "Alumno anónimo").
    display_name: str | None
    # EXP ganada esta semana.
    xp: int
    is_me: bool
    # Si la semana terminara ahora: sube, baja o se queda (null).
    zone: Literal["promotion", "demotion"] | None


class LeagueResultRead(BaseModel):
    """Cómo le fue en la última semana cerrada. Se anuncia una sola vez."""

    week_start: date
    # El nivel en el que compitió esa semana.
    tier: int
    result: Literal["promoted", "stayed", "demoted"]
    final_rank: int
    final_xp: int


class LeagueRead(BaseModel):
    # Índice del nivel en `tiers`; la app traduce el nombre con `leagues.tiers.<tier_id>`.
    tier: int
    tier_id: str
    tiers: list[str]
    week_start: date
    # Cuándo cierra la semana (lunes 00:00 UTC).
    ends_at: datetime
    # Se entra a la liga al ganar EXP por primera vez en la semana.
    joined: bool
    members: list[LeagueMemberRead]
    group_size: int
    last_result: LeagueResultRead | None
