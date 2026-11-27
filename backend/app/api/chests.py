import uuid

from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.api.errors import VALIDATION_ERROR_RESPONSES, error_responses
from app.core.db import DbSession
from app.schemas.achievements import ChestRead
from app.services import chests as chest_service
from app.services.errors import InvalidToken, NodeLocked, NotAChest, NotFound

router = APIRouter(tags=["chests"], responses=VALIDATION_ERROR_RESPONSES)


@router.post(
    "/chests/{chest_id}/open",
    response_model=ChestRead,
    operation_id="openChest",
    responses=error_responses(InvalidToken, NotFound),
)
async def open_chest(chest_id: uuid.UUID, db: DbSession, user: CurrentUser) -> ChestRead:
    """Abre el cofre de un intento terminado. Abrirlo otra vez devuelve el mismo premio."""
    return await chest_service.open_chest(db, user, chest_id)


@router.post(
    "/nodes/{node_key}/chest",
    response_model=ChestRead,
    operation_id="openNodeChest",
    responses=error_responses(InvalidToken, NotFound, NodeLocked, NotAChest),
)
async def open_node_chest(node_key: str, db: DbSession, user: CurrentUser) -> ChestRead:
    """Abre el nodo cofre del camino (una vez por alumno) y lo marca como completado."""
    return await chest_service.open_node_chest(db, user, node_key)
