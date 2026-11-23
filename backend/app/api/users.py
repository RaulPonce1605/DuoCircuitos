from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.api.errors import error_responses
from app.schemas.user import UserRead
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
