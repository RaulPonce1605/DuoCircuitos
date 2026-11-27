import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser
from app.api.errors import VALIDATION_ERROR_RESPONSES, error_responses
from app.core.db import DbSession
from app.schemas.tutor import TutorReplyRead, TutorRequest
from app.services.errors import (
    AlreadyAnswered,
    InvalidToken,
    NotFound,
    TutorExerciseLimit,
    TutorRateLimited,
)
from app.services.tutor import TutorProvider, get_tutor_provider
from app.services.tutor import service as tutor_service

router = APIRouter(tags=["tutor"], responses=VALIDATION_ERROR_RESPONSES)

Provider = Annotated[TutorProvider | None, Depends(get_tutor_provider)]


@router.post(
    "/exercise-instances/{instance_id}/tutor",
    response_model=TutorReplyRead,
    operation_id="askTutor",
    responses=error_responses(
        InvalidToken, NotFound, AlreadyAnswered, TutorRateLimited, TutorExerciseLimit
    ),
)
async def ask_tutor(
    instance_id: uuid.UUID,
    body: TutorRequest,
    db: DbSession,
    user: CurrentUser,
    provider: Provider,
) -> TutorReplyRead:
    return await tutor_service.ask(db, user, instance_id, body.message, provider)
