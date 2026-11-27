from datetime import UTC, datetime

from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.api.errors import VALIDATION_ERROR_RESPONSES, error_responses
from app.core.db import DbSession
from app.schemas.shop import ShopItemId, ShopRead
from app.services import shop as shop_service
from app.services.errors import (
    EnergyAlreadyFull,
    InvalidToken,
    NotEnoughCoins,
    StreakFreezeLimit,
)

router = APIRouter(tags=["shop"], responses=VALIDATION_ERROR_RESPONSES)


@router.get(
    "/shop",
    response_model=ShopRead,
    operation_id="getShop",
    responses=error_responses(InvalidToken),
)
async def get_shop(user: CurrentUser) -> ShopRead:
    """Monedas, artículos con su precio y si se pueden comprar ahora."""
    return shop_service.overview(user, datetime.now(UTC))


@router.post(
    "/shop/items/{item_id}/buy",
    response_model=ShopRead,
    operation_id="buyShopItem",
    responses=error_responses(InvalidToken, NotEnoughCoins, EnergyAlreadyFull, StreakFreezeLimit),
)
async def buy_shop_item(item_id: ShopItemId, db: DbSession, user: CurrentUser) -> ShopRead:
    """Compra un artículo: la recarga llena la energía; el protector se guarda para un día sin
    práctica."""
    return await shop_service.buy(db, user, item_id, datetime.now(UTC))
