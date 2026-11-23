"""Modelos ORM. Importa aquí cada modelo nuevo para que Alembic lo detecte."""

from app.models.attempt import ExerciseInstance, LessonAttempt
from app.models.auth import RefreshToken
from app.models.base import Base
from app.models.gamification import XpEvent
from app.models.progress import NodeProgress
from app.models.syllabus import Exercise, Lesson, Node, Section, Stage, Unit
from app.models.user import User

__all__ = [
    "Base",
    "Exercise",
    "ExerciseInstance",
    "Lesson",
    "LessonAttempt",
    "Node",
    "NodeProgress",
    "RefreshToken",
    "Section",
    "Stage",
    "Unit",
    "User",
    "XpEvent",
]
