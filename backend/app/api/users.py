from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.api.errors import error_responses
from app.schemas.user import UserRead
from app.services.errors import InvalidToken

router = APIRouter(tags=["users"])


@router.get(
    "/me",
    response_model=UserRead,
    operation_id="getCurrentUser",
    responses=error_responses(InvalidToken),
)
async def get_me(user: CurrentUser) -> UserRead:
    return UserRead.model_validate(user)
