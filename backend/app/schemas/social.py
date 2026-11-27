import uuid

from pydantic import BaseModel


class UserCardRead(BaseModel):
    """Otro alumno como lo ve el que pregunta. Un perfil privado sale sin nombre."""

    id: uuid.UUID
    # Null si el perfil es privado (la app muestra "Alumno anónimo").
    display_name: str | None
    xp_total: int
    streak: int
    league_tier: int
    league_tier_id: str
    is_following: bool
    follows_me: bool


class FriendsRead(BaseModel):
    following: list[UserCardRead]
    followers: list[UserCardRead]
