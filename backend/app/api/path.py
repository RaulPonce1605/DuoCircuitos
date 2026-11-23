from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.api.errors import error_responses
from app.core.db import DbSession
from app.schemas.path import PathRead
from app.services import path as path_service
from app.services.errors import InvalidToken

router = APIRouter(tags=["path"])


@router.get(
    "/path",
    response_model=PathRead,
    operation_id="getPath",
    responses=error_responses(InvalidToken),
)
async def get_path(db: DbSession, user: CurrentUser) -> PathRead:
    return await path_service.get_path(db, user)
