import uuid

from pydantic import BaseModel

from app.schemas.exercises import ExerciseAnswer, ExercisePublic
from app.schemas.path import NodeType
from app.schemas.user import EnergyRead


class LessonRefRead(BaseModel):
    slug: str
    title: str


class NodeRefRead(BaseModel):
    """El nodo del intento. La app arma el título de un repaso o evaluación con `unit_title`."""

    key: str
    type: NodeType
    unit_title: str


class LessonProgressRead(BaseModel):
    # Ejercicios distintos ya respondidos bien / ejercicios de la lección.
    completed: int
    total: int


class ExerciseInstanceRead(BaseModel):
    instance_id: uuid.UUID
    exercise: ExercisePublic


class LessonAttemptRead(BaseModel):
    attempt_id: uuid.UUID
    node: NodeRefRead
    # Solo en los nodos de lección; null en repaso y evaluación.
    lesson: LessonRefRead | None
    progress: LessonProgressRead
    current_exercise: ExerciseInstanceRead
    energy: EnergyRead


class CheckRequest(BaseModel):
    answer: ExerciseAnswer


class CheckResultRead(BaseModel):
    correct: bool
    # Se muestran DESPUÉS de Comprobar, nunca antes (CLAUDE.md 5.4).
    correct_answer: str
    explanation: str
    progress: LessonProgressRead
    # El siguiente ejercicio de la cola; null si la lección terminó.
    next_exercise: ExerciseInstanceRead | None
    attempt_completed: bool
    # La energía después de esta respuesta (un fallo gasta).
    energy: EnergyRead


class LessonAttemptSummaryRead(BaseModel):
    attempt_id: uuid.UUID
    node: NodeRefRead
    lesson: LessonRefRead | None
    exercise_count: int
    first_try_correct: int
    accuracy: int
    xp_awarded: int
    concepts: list[str]
    streak: int
    streak_extended: bool
