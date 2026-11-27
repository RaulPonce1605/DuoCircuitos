"""Energía (docs/diseno/energia.md). El backend es la fuente de verdad (CLAUDE.md 5.4).

- Cada respuesta incorrecta gasta `ENERGY_COST_PER_MISTAKE`.
- Se recarga una unidad cada `ENERGY_REFILL_MINUTES`, hasta `ENERGY_MAX`. No hay tareas
  programadas: la recarga se calcula al leer, a partir de `energy_updated_at`.
- Sin energía no se puede empezar una lección ni responder un ejercicio.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta

from app.core.config import get_settings
from app.models import User
from app.services.errors import NotEnoughEnergy


@dataclass(frozen=True)
class EnergyState:
    current: int
    max: int
    # Cuándo llega la siguiente unidad; None si está llena.
    next_refill_at: datetime | None


def _refill_period() -> timedelta:
    return timedelta(minutes=get_settings().energy_refill_minutes)


def _settle(user: User, now: datetime) -> None:
    """Aplica en la fila la recarga acumulada hasta `now`, sin perder la fracción en curso."""
    settings = get_settings()
    user.energy_used = min(user.energy_used or 0, settings.energy_max)
    if user.energy_used == 0:
        user.energy_updated_at = None
        return
    if user.energy_updated_at is None:  # no debería pasar: la recarga empieza a contar ya
        user.energy_updated_at = now
        return
    period = _refill_period()
    elapsed = max(timedelta(0), now - user.energy_updated_at)
    refilled = int(elapsed // period)
    if refilled >= user.energy_used:
        user.energy_used = 0
        user.energy_updated_at = None
    elif refilled > 0:
        user.energy_used -= refilled
        user.energy_updated_at += refilled * period


def state(user: User, now: datetime) -> EnergyState:
    """La energía como la ve el alumno ahora (no modifica la fila)."""
    settings = get_settings()
    used = min(user.energy_used or 0, settings.energy_max)
    if used == 0:
        return EnergyState(
            current=settings.energy_max, max=settings.energy_max, next_refill_at=None
        )
    period = _refill_period()
    since = user.energy_updated_at or now
    elapsed = max(timedelta(0), now - since)
    refilled = int(elapsed // period)
    if refilled >= used:
        return EnergyState(
            current=settings.energy_max, max=settings.energy_max, next_refill_at=None
        )
    return EnergyState(
        current=settings.energy_max - used + refilled,
        max=settings.energy_max,
        next_refill_at=since + (refilled + 1) * period,
    )


def require(user: User, now: datetime) -> None:
    """Lanza `NotEnoughEnergy` si el alumno no tiene energía para practicar."""
    if state(user, now).current <= 0:
        raise NotEnoughEnergy


def spend(user: User, amount: int, now: datetime) -> None:
    """Gasta energía (sin bajar de 0). La fila del usuario debe estar bloqueada."""
    if amount <= 0:
        return
    _settle(user, now)
    if user.energy_used == 0:
        user.energy_updated_at = now  # la recarga empieza a contar desde el primer gasto
    user.energy_used = min(get_settings().energy_max, user.energy_used + amount)


def refill(user: User, amount: int, now: datetime) -> None:
    """Devuelve energía (premios de cofres). La fila del usuario debe estar bloqueada."""
    if amount <= 0:
        return
    _settle(user, now)
    user.energy_used = max(0, user.energy_used - amount)
    if user.energy_used == 0:
        user.energy_updated_at = None
