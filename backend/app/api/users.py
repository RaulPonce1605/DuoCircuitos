from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.api.errors import error_responses
from app.core.db import DbSession
from app.schemas.achievements import AchievementsRead
from app.schemas.user import UserRead
from app.services import achievements as achievement_service
from app.services.errors import InvalidToken
from app.services.users import user_read

router = APIRouter(tags=["users"])


@router.get(
    "/me",
    response_model=UserRead,
    operation_id="getCurrentUser",
    responses=error_responses(InvalidToken),
)
async def get_me(user: CurrentUser) -> UserRead:
    return user_read(user)


@router.get(
    "/me/achievements",
    response_model=AchievementsRead,
    operation_id="getAchievements",
    responses=error_responses(InvalidToken),
)
async def get_achievements(db: DbSession, user: CurrentUser) -> AchievementsRead:
    """Los logros con su progreso y las medallas ganadas."""
    return await achievement_service.overview(db, user)
