"""Validadores de ejercicios. Importar este paquete registra todos los tipos."""

from app.services.exercises import fill_pattern, multiple_choice, numeric
from app.services.exercises.registry import get_validator, registered_types

__all__ = ["fill_pattern", "get_validator", "multiple_choice", "numeric", "registered_types"]
