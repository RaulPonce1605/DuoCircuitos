"""Contrato público de los ejercicios: lo que ve el alumno y lo que responde.

Los schemas públicos NUNCA incluyen la solución, la opción correcta ni las respuestas aceptadas
(CLAUDE.md 5.4). Cada tipo tiene su par `XPublic` / `XAnswer`; para agregar un tipo se agrega su
par aquí y su validador en `services/exercises/` (backend/CLAUDE.md 3.7).
"""

from typing import Annotated, Literal

from pydantic import BaseModel, Field

# --- Lo que ve el alumno ---------------------------------------------------------------------


class MultipleChoicePublic(BaseModel):
    type: Literal["multiple_choice"]
    prompt: str
    # En el orden en que se muestran (barajadas por instancia).
    options: list[str]


class FillPatternPublic(BaseModel):
    type: Literal["fill_pattern"]
    prompt: str


class NumericPublic(BaseModel):
    type: Literal["numeric"]
    # Enunciado con los valores sorteados ya sustituidos.
    prompt: str
    # Unidad SI base del resultado (A, V, Ω...). El alumno puede responder con prefijo (mA, kΩ).
    unit: str


ExercisePublic = Annotated[
    MultipleChoicePublic | FillPatternPublic | NumericPublic, Field(discriminator="type")
]


# --- Lo que responde el alumno ---------------------------------------------------------------


class MultipleChoiceAnswer(BaseModel):
    type: Literal["multiple_choice"]
    # Índice de la opción elegida, en el orden en que se le mostraron.
    option: int = Field(ge=0, le=50)


class FillPatternAnswer(BaseModel):
    type: Literal["fill_pattern"]
    text: str = Field(max_length=200)


class NumericAnswer(BaseModel):
    type: Literal["numeric"]
    # Texto tal como lo escribió el alumno ("22.7", "2,5", "1.2e-3"); el backend lo interpreta.
    value: str = Field(max_length=40)
    # Unidad con prefijo opcional ("mA", "kΩ", "A"). Vacía = unidad base.
    unit: str = Field(default="", max_length=10)


ExerciseAnswer = Annotated[
    MultipleChoiceAnswer | FillPatternAnswer | NumericAnswer, Field(discriminator="type")
]
