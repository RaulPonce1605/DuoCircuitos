"""Tienda (docs/diseno/tienda.md): monedas por recargas de energía y protectores de racha.

El backend decide precios, si se puede comprar y qué pasa al comprar (CLAUDE.md 5.4). Los precios
viven en `Settings`; los nombres de los artículos, en la app (i18n).
"""

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import Purchase, User
from app.schemas.shop import ShopItemId, ShopItemRead, ShopRead, UnavailableReason
from app.services import energy
from app.services.errors import EnergyAlreadyFull, NotEnoughCoins, StreakFreezeLimit
from app.services.users import energy_read

ITEMS: tuple[ShopItemId, ...] = ("energy_refill", "streak_freeze")


def price(item: ShopItemId) -> int:
    settings = get_settings()
    return {
        "energy_refill": settings.shop_energy_refill_price,
        "streak_freeze": settings.shop_streak_freeze_price,
    }[item]


def _blocker(user: User, item: ShopItemId, now: datetime) -> UnavailableReason | None:
    """Por qué no se puede comprar ahora, o None si se puede."""
    if item == "energy_refill" and energy.state(user, now).current >= get_settings().energy_max:
        return "energy_already_full"
    if item == "streak_freeze" and user.streak_freezes >= get_settings().streak_freeze_max:
        return "streak_freeze_limit"
    if user.coins < price(item):
        return "not_enough_coins"
    return None


def overview(user: User, now: datetime) -> ShopRead:
    return ShopRead(
        coins=user.coins,
        streak_freezes=user.streak_freezes,
        streak_freeze_max=get_settings().streak_freeze_max,
        energy=energy_read(user, now),
        items=[
            ShopItemRead(
                id=item,
                price=price(item),
                unavailable_reason=_blocker(user, item, now),
            )
            for item in ITEMS
        ],
    )


async def buy(db: AsyncSession, user: User, item: ShopItemId, now: datetime) -> ShopRead:
    # Bloquea al usuario: dos compras a la vez no deben gastar las mismas monedas.
    await db.refresh(user, with_for_update=True)
    reason = _blocker(user, item, now)
    if reason == "energy_already_full":
        raise EnergyAlreadyFull
    if reason == "streak_freeze_limit":
        raise StreakFreezeLimit
    if reason == "not_enough_coins":
        raise NotEnoughCoins
    cost = price(item)
    user.coins -= cost
    if item == "energy_refill":
        energy.refill(user, get_settings().energy_max, now)
    else:
        user.streak_freezes += 1
    db.add(Purchase(user_id=user.id, item=item, price=cost))
    await db.commit()
    return overview(user, now)
