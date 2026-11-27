"""Tutor con IA (backend/CLAUDE.md 3.9)."""

from app.services.tutor.guard import guard_output, reveals_solution
from app.services.tutor.prompt import build_prompt
from app.services.tutor.provider import (
    TutorPrompt,
    TutorProvider,
    TutorProviderError,
    get_tutor_provider,
)

__all__ = [
    "TutorPrompt",
    "TutorProvider",
    "TutorProviderError",
    "build_prompt",
    "get_tutor_provider",
    "guard_output",
    "reveals_solution",
]
