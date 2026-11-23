from fastapi import APIRouter

from app.schemas.health import HealthRead

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthRead, operation_id="getHealth")
async def get_health() -> HealthRead:
    return HealthRead(status="ok")
