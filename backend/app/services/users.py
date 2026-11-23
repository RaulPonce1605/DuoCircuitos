from datetime import UTC, datetime

from app.models import User
from app.schemas.user import UserRead
from app.services.gamification import effective_streak


def user_read(user: User, now: datetime | None = None) -> UserRead:
    """El usuario como lo ve la app: con la racha efectiva (rota si ya pasó más de un día)."""
    read = UserRead.model_validate(user)
    return read.model_copy(
        update={"streak_current": effective_streak(user, now or datetime.now(UTC))}
    )
