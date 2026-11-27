import uuid

from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.api.errors import VALIDATION_ERROR_RESPONSES, error_responses
from app.core.db import DbSession
from app.schemas.lessons import (
    CheckRequest,
    CheckResultRead,
    LessonAttemptRead,
    LessonAttemptSummaryRead,
)
from app.services import lessons as lesson_service
from app.services.errors import (
    AlreadyAnswered,
    AttemptNotCompleted,
    InvalidAnswer,
    InvalidToken,
    NodeLocked,
    NotCurrentExercise,
    NotEnoughEnergy,
    NotFound,
)

router = APIRouter(tags=["lessons"], responses=VALIDATION_ERROR_RESPONSES)


@router.post(
    "/lessons/{lesson_slug}/attempts",
    response_model=LessonAttemptRead,
    status_code=201,
    operation_id="startLesson",
    responses=error_responses(InvalidToken, NotFound, NodeLocked, NotEnoughEnergy),
)
async def start_lesson(lesson_slug: str, db: DbSession, user: CurrentUser) -> LessonAttemptRead:
    return await lesson_service.start_attempt(db, user, lesson_slug)


@router.post(
    "/exercise-instances/{instance_id}/check",
    response_model=CheckResultRead,
    operation_id="checkExercise",
    responses=error_responses(
        InvalidToken, NotFound, AlreadyAnswered, NotCurrentExercise, NotEnoughEnergy, InvalidAnswer
    ),
)
async def check_exercise(
    instance_id: uuid.UUID, body: CheckRequest, db: DbSession, user: CurrentUser
) -> CheckResultRead:
    return await lesson_service.check_answer(db, user, instance_id, body.answer)


@router.get(
    "/lesson-attempts/{attempt_id}/summary",
    response_model=LessonAttemptSummaryRead,
    operation_id="getLessonSummary",
    responses=error_responses(InvalidToken, NotFound, AttemptNotCompleted),
)
async def get_lesson_summary(
    attempt_id: uuid.UUID, db: DbSession, user: CurrentUser
) -> LessonAttemptSummaryRead:
    return await lesson_service.get_summary(db, user, attempt_id)
