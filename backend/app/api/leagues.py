from datetime import UTC, datetime

from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.api.errors import error_responses
from app.core.db import DbSession
from app.schemas.leagues import LeagueRead
from app.services import leagues as league_service
from app.services.errors import InvalidToken

router = APIRouter(tags=["leagues"])


@router.get(
    "/leagues/current",
    response_model=LeagueRead,
    operation_id="getCurrentLeague",
    responses=error_responses(InvalidToken),
)
async def get_current_league(db: DbSession, user: CurrentUser) -> LeagueRead:
    """La liga de esta semana con su ranking. Cierra las semanas pasadas que sigan abiertas y
    anuncia (una vez) cómo le fue al alumno en la última."""
    return await league_service.overview(db, user, datetime.now(UTC))
