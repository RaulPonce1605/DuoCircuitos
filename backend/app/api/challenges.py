from datetime import UTC, datetime

from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.api.errors import error_responses
from app.core.db import DbSession
from app.schemas.challenges import ChallengesRead
from app.services import challenges as challenge_service
from app.services.errors import InvalidToken

router = APIRouter(tags=["challenges"])


@router.get(
    "/challenges",
    response_model=ChallengesRead,
    operation_id="getChallenges",
    responses=error_responses(InvalidToken),
)
async def get_challenges(db: DbSession, user: CurrentUser) -> ChallengesRead:
    """Los desafíos de hoy y del mes, con su avance. Se crean solos si aún no existen."""
    return await challenge_service.overview(db, user, datetime.now(UTC))
