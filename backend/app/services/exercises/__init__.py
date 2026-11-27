"""Validadores de ejercicios. Importar este paquete registra todos los tipos."""

from app.services.exercises import circuit_diagram, fill_pattern, multiple_choice, numeric
from app.services.exercises.registry import get_validator, registered_types

__all__ = [
    "circuit_diagram",
    "fill_pattern",
    "get_validator",
    "multiple_choice",
    "numeric",
    "registered_types",
]
