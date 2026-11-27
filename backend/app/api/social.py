import uuid
from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser
from app.api.errors import VALIDATION_ERROR_RESPONSES, error_responses
from app.core.db import DbSession
from app.schemas.social import FriendsRead, UserCardRead
from app.services import social as social_service
from app.services.errors import CannotFollowSelf, InvalidToken, NotFound

router = APIRouter(tags=["social"], responses=VALIDATION_ERROR_RESPONSES)


@router.get(
    "/friends",
    response_model=FriendsRead,
    operation_id="getFriends",
    responses=error_responses(InvalidToken),
)
async def get_friends(db: DbSession, user: CurrentUser) -> FriendsRead:
    """A quiénes sigo y quiénes me siguen."""
    return await social_service.friends(db, user)


@router.get(
    "/users/search",
    response_model=list[UserCardRead],
    operation_id="searchUsers",
    responses=error_responses(InvalidToken),
)
async def search_users(
    q: Annotated[str, Query(max_length=50)], db: DbSession, user: CurrentUser
) -> list[UserCardRead]:
    """Busca perfiles públicos por nombre (mínimo 2 letras)."""
    return await social_service.search(db, user, q)


@router.post(
    "/users/{user_id}/follow",
    response_model=UserCardRead,
    operation_id="followUser",
    responses=error_responses(InvalidToken, NotFound, CannotFollowSelf),
)
async def follow_user(user_id: uuid.UUID, db: DbSession, user: CurrentUser) -> UserCardRead:
    return await social_service.follow(db, user, user_id)


@router.delete(
    "/users/{user_id}/follow",
    response_model=UserCardRead,
    operation_id="unfollowUser",
    responses=error_responses(InvalidToken, NotFound),
)
async def unfollow_user(user_id: uuid.UUID, db: DbSession, user: CurrentUser) -> UserCardRead:
    return await social_service.unfollow(db, user, user_id)
