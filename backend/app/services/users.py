from datetime import UTC, datetime

from app.models import User
from app.schemas.user import EnergyRead, UserRead
from app.services import energy
from app.services.gamification import effective_streak


def energy_read(user: User, now: datetime) -> EnergyRead:
    current = energy.state(user, now)
    return EnergyRead(
        current=current.current, max=current.max, next_refill_at=current.next_refill_at
    )


def user_read(user: User, now: datetime | None = None) -> UserRead:
    """El usuario como lo ve la app: con la racha efectiva (rota si ya pasó más de un día) y la
    energía recargada hasta ahora."""
    now = now or datetime.now(UTC)
    return UserRead(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        timezone=user.timezone,
        xp_total=user.xp_total,
        streak_current=effective_streak(user, now),
        streak_longest=user.streak_longest,
        created_at=user.created_at,
        energy=energy_read(user, now),
    )
