from datetime import UTC, date, datetime, timedelta

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Purchase
from app.services import auth as auth_service
from app.services import energy, shop
from app.services.errors import EnergyAlreadyFull, NotEnoughCoins, StreakFreezeLimit
from app.services.gamification import apply_streak_freezes, effective_streak

NOW = datetime(2026, 11, 26, 18, tzinfo=UTC)  # 12:00 del 26 en la Ciudad de México


async def test_overview_explains_what_cannot_be_bought(user_session: auth_service.Session) -> None:
    user = user_session.user
    user.coins = 100

    data = shop.overview(user, NOW)

    reasons = {item.id: item.unavailable_reason for item in data.items}
    # Energía llena: no tiene caso recargar. 100 monedas no alcanzan para el protector (150).
    assert reasons == {"energy_refill": "energy_already_full", "streak_freeze": "not_enough_coins"}
    assert (data.coins, data.streak_freezes, data.streak_freeze_max) == (100, 0, 2)


async def test_buy_energy_refill(db: AsyncSession, user_session: auth_service.Session) -> None:
    user = user_session.user
    user.coins = 100
    energy.spend(user, 3, NOW)
    await db.flush()  # buy() vuelve a leer al usuario para bloquearlo

    data = await shop.buy(db, user, "energy_refill", NOW)

    assert data.coins == 40
    assert data.energy.current == 5
    assert await db.scalar(select(func.count()).select_from(Purchase)) == 1
    with pytest.raises(EnergyAlreadyFull):
        await shop.buy(db, user, "energy_refill", NOW)


async def test_buy_streak_freezes_up_to_the_limit(
    db: AsyncSession, user_session: auth_service.Session
) -> None:
    user = user_session.user
    user.coins = 1000
    await db.flush()

    await shop.buy(db, user, "streak_freeze", NOW)
    data = await shop.buy(db, user, "streak_freeze", NOW)

    assert (data.streak_freezes, data.coins) == (2, 700)
    with pytest.raises(StreakFreezeLimit):
        await shop.buy(db, user, "streak_freeze", NOW)


async def test_not_enough_coins(db: AsyncSession, user_session: auth_service.Session) -> None:
    user = user_session.user
    user.coins = 10
    await db.flush()
    with pytest.raises(NotEnoughCoins):
        await shop.buy(db, user, "streak_freeze", NOW)
    assert user.coins == 10


async def test_freezes_cover_missed_days_only_if_enough(
    user_session: auth_service.Session,
) -> None:
    user = user_session.user
    user.streak_current = 6
    user.streak_longest = 6
    user.streak_last_date = date(2026, 11, 23)  # faltó el 24 y el 25
    user.streak_freezes = 1

    # Con 1 protector no alcanza para 2 días: la racha se ve rota y no se gasta nada.
    assert effective_streak(user, NOW) == 0
    assert apply_streak_freezes(user, NOW) == []
    assert user.streak_freezes == 1

    user.streak_freezes = 2
    assert effective_streak(user, NOW) == 6
    covered = apply_streak_freezes(user, NOW)
    assert covered == [date(2026, 11, 24), date(2026, 11, 25)]
    assert user.streak_freezes == 0
    assert user.streak_last_date == date(2026, 11, 25)


async def test_no_freeze_is_spent_when_nothing_was_missed(
    user_session: auth_service.Session,
) -> None:
    user = user_session.user
    user.streak_current = 3
    user.streak_longest = 3
    user.streak_last_date = NOW.date() - timedelta(days=1)
    user.streak_freezes = 2

    assert apply_streak_freezes(user, NOW) == []
    assert user.streak_freezes == 2
