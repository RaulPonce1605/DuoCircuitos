"""Modelos ORM. Importa aquí cada modelo nuevo para que Alembic lo detecte."""

from app.models.attempt import ExerciseInstance, LessonAttempt
from app.models.auth import RefreshToken
from app.models.base import Base
from app.models.gamification import (
    Badge,
    Challenge,
    Chest,
    LeagueGroup,
    LeagueMember,
    Purchase,
    StreakFreezeUse,
    XpEvent,
)
from app.models.progress import NodeProgress
from app.models.syllabus import Exercise, Lesson, Node, Section, Stage, Unit
from app.models.tutor import TutorMessage
from app.models.user import User

__all__ = [
    "Badge",
    "Base",
    "Challenge",
    "Chest",
    "Exercise",
    "ExerciseInstance",
    "LeagueGroup",
    "LeagueMember",
    "Lesson",
    "LessonAttempt",
    "Node",
    "NodeProgress",
    "Purchase",
    "RefreshToken",
    "Section",
    "Stage",
    "StreakFreezeUse",
    "TutorMessage",
    "Unit",
    "User",
    "XpEvent",
]
