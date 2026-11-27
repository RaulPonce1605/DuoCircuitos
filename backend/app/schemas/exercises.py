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


DiagramElementKind = Literal[
    "wire",
    "resistor",
    "capacitor",
    "inductor",
    "voltage_source",
    "current_source",
    "ammeter",
    "voltmeter",
    "switch",
    "lamp",
]


class GridPoint(BaseModel):
    """Punto de la cuadrícula del diagrama: x a la derecha, y hacia abajo."""

    x: int
    y: int


class DiagramElementPublic(BaseModel):
    id: str
    kind: DiagramElementKind
    # Siempre horizontal o vertical. En las fuentes, `end` es el lado + (o hacia donde va la
    # corriente).
    start: GridPoint
    end: GridPoint
    # Null solo en los cables, que no se pueden tocar.
    label: str | None


class DiagramNodePublic(BaseModel):
    point: GridPoint
    label: str


class CircuitDiagramPublic(BaseModel):
    type: Literal["circuit_diagram"]
    prompt: str
    elements: list[DiagramElementPublic]
    nodes: list[DiagramNodePublic]


ExercisePublic = Annotated[
    MultipleChoicePublic | FillPatternPublic | NumericPublic | CircuitDiagramPublic,
    Field(discriminator="type"),
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


class CircuitDiagramAnswer(BaseModel):
    type: Literal["circuit_diagram"]
    # Los ids de los elementos que tocó el alumno (el orden no importa).
    elements: list[Annotated[str, Field(max_length=40)]] = Field(max_length=30)


ExerciseAnswer = Annotated[
    MultipleChoiceAnswer | FillPatternAnswer | NumericAnswer | CircuitDiagramAnswer,
    Field(discriminator="type"),
]
