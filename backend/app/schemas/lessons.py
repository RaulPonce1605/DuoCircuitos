import uuid

from pydantic import BaseModel

from app.schemas.exercises import ExerciseAnswer, ExercisePublic


class LessonRefRead(BaseModel):
    slug: str
    title: str


class LessonProgressRead(BaseModel):
    # Ejercicios distintos ya respondidos bien / ejercicios de la lección.
    completed: int
    total: int


class ExerciseInstanceRead(BaseModel):
    instance_id: uuid.UUID
    exercise: ExercisePublic


class LessonAttemptRead(BaseModel):
    attempt_id: uuid.UUID
    lesson: LessonRefRead
    progress: LessonProgressRead
    current_exercise: ExerciseInstanceRead


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


class LessonAttemptSummaryRead(BaseModel):
    attempt_id: uuid.UUID
    lesson: LessonRefRead
    exercise_count: int
    first_try_correct: int
    accuracy: int
    xp_awarded: int
    concepts: list[str]
    streak: int
    streak_extended: bool
