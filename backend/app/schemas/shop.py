from typing import Literal

from pydantic import BaseModel

from app.schemas.user import EnergyRead

ShopItemId = Literal["energy_refill", "streak_freeze"]
UnavailableReason = Literal["not_enough_coins", "energy_already_full", "streak_freeze_limit"]


class ShopItemRead(BaseModel):
    """Un artículo. La app lo nombra con i18n: `shop.items.<id>`."""

    id: ShopItemId
    price: int
    # Null si se puede comprar ahora; si no, el motivo (la app lo explica).
    unavailable_reason: UnavailableReason | None


class ShopRead(BaseModel):
    coins: int
    streak_freezes: int
    streak_freeze_max: int
    energy: EnergyRead
    items: list[ShopItemRead]
