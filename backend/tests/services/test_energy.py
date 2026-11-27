from datetime import UTC, datetime, timedelta

import pytest

from app.models import User
from app.services import energy
from app.services.errors import NotEnoughEnergy

NOW = datetime(2026, 11, 26, 12, 0, tzinfo=UTC)
PERIOD = timedelta(minutes=30)  # ENERGY_REFILL_MINUTES por defecto


def _user(used: int = 0, updated_at: datetime | None = None) -> User:
    return User(energy_used=used, energy_updated_at=updated_at)


def test_a_new_user_has_full_energy() -> None:
    state = energy.state(_user(), NOW)
    assert (state.current, state.max, state.next_refill_at) == (5, 5, None)


def test_spending_starts_the_refill_clock() -> None:
    user = _user()
    energy.spend(user, 1, NOW)

    state = energy.state(user, NOW)
    assert state.current == 4
    assert state.next_refill_at == NOW + PERIOD


def test_refills_one_unit_per_period_and_keeps_the_partial_progress() -> None:
    user = _user()
    energy.spend(user, 3, NOW)

    assert energy.state(user, NOW + PERIOD - timedelta(seconds=1)).current == 2
    assert energy.state(user, NOW + PERIOD).current == 3
    later = energy.state(user, NOW + 2 * PERIOD + timedelta(minutes=10))
    assert later.current == 4
    assert later.next_refill_at == NOW + 3 * PERIOD

    # Gastar a la mitad de un periodo no reinicia el reloj de la unidad que ya venía.
    energy.spend(user, 1, NOW + PERIOD + timedelta(minutes=10))
    assert energy.state(user, NOW + 2 * PERIOD).current == 3


def test_full_after_enough_time_and_never_above_max() -> None:
    user = _user()
    energy.spend(user, 2, NOW)

    state = energy.state(user, NOW + 10 * PERIOD)
    assert (state.current, state.next_refill_at) == (5, None)


def test_never_goes_below_zero_and_require_blocks() -> None:
    user = _user()
    energy.spend(user, 99, NOW)

    assert energy.state(user, NOW).current == 0
    with pytest.raises(NotEnoughEnergy):
        energy.require(user, NOW)
    energy.require(user, NOW + PERIOD)  # ya se recargó una


def test_refill_gives_energy_back() -> None:
    user = _user()
    energy.spend(user, 4, NOW)
    energy.refill(user, 2, NOW + timedelta(minutes=5))

    assert energy.state(user, NOW + timedelta(minutes=5)).current == 3
    energy.refill(user, 10, NOW + timedelta(minutes=5))
    assert user.energy_used == 0
    assert user.energy_updated_at is None


def test_lowering_the_max_does_not_leave_more_than_max(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.core.config import get_settings

    user = _user(used=4, updated_at=NOW)
    monkeypatch.setattr(get_settings(), "energy_max", 3)
    assert energy.state(user, NOW).current == 0
    assert energy.state(user, NOW + PERIOD).current == 1
