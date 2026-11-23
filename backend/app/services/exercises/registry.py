"""Registro de validadores por id de tipo. Es el único lugar que despacha por tipo de ejercicio."""

from collections.abc import Callable
from typing import Any

from app.services.errors import UnknownExerciseType
from app.services.exercises.base import ExerciseValidator

_REGISTRY: dict[str, ExerciseValidator[Any]] = {}


def register[V: type[ExerciseValidator[Any]]](type_id: str) -> Callable[[V], V]:
    def decorator(cls: V) -> V:
        if type_id in _REGISTRY:
            raise ValueError(f"ya hay un validador registrado para {type_id!r}")
        cls.type_id = type_id
        _REGISTRY[type_id] = cls()
        return cls

    return decorator


def get_validator(type_id: str) -> ExerciseValidator[Any]:
    try:
        return _REGISTRY[type_id]
    except KeyError as exc:
        raise UnknownExerciseType(type_id) from exc


def registered_types() -> frozenset[str]:
    return frozenset(_REGISTRY)
