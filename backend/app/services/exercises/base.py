"""Interfaz común de los validadores de ejercicios (backend/CLAUDE.md 3.7)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from random import Random
from typing import Any, ClassVar

from pydantic import BaseModel

from app.schemas.exercises import ExerciseAnswer, ExercisePublic


@dataclass(frozen=True)
class CheckOutcome:
    correct: bool
    # La respuesta correcta lista para mostrar después de Comprobar ("22.7 mA", "En serie...").
    correct_answer: str


class ExerciseValidator[SpecT: BaseModel](ABC):
    """Un validador por tipo. Trabaja sobre el `spec` (el ejercicio del temario) y el `state`
    guardado de la instancia, así que el resultado es reproducible y no depende del cliente."""

    type_id: ClassVar[str]
    spec_model: type[SpecT]

    def parse_spec(self, spec: dict[str, Any]) -> SpecT:
        return self.spec_model.model_validate(spec)

    @abstractmethod
    def generate_state(self, spec: SpecT, rng: Random) -> dict[str, Any]:
        """Sortea lo que varía entre instancias (parámetros, orden de opciones). Debe ser JSON."""

    @abstractmethod
    def public_view(self, spec: SpecT, state: dict[str, Any]) -> ExercisePublic:
        """Lo que ve el alumno. Nunca incluye la solución."""

    @abstractmethod
    def check(self, spec: SpecT, state: dict[str, Any], answer: ExerciseAnswer) -> CheckOutcome:
        """Valida la respuesta. Lanza `InvalidAnswer` si no es del tipo esperado."""

    @abstractmethod
    def solution_spans(
        self, spec: SpecT, state: dict[str, Any], text: str
    ) -> list[tuple[int, int]]:
        """Dónde revela `text` la solución de esta instancia (backend/CLAUDE.md 3.9).

        El tutor lo usa para tachar la solución del material del prompt y para bloquear las
        respuestas del LLM que la contengan. Ante la duda, mejor detectar de más.
        """
