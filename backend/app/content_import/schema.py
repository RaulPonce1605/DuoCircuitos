"""Modelos del temario (`contenido/`).

Los archivos usan claves en español; aquí se traducen a atributos en inglés con alias.
El formato está documentado en `contenido/README.md`.
"""

from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

ID_PATTERN = r"^[a-z0-9]+(-[a-z0-9]+)*$"

SyllabusId = Annotated[str, Field(pattern=ID_PATTERN)]
NonEmptyStr = Annotated[str, Field(min_length=1)]


class SyllabusModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True, frozen=True)


# --- camino.yaml -----------------------------------------------------------------------------


class PathNode(SyllabusModel):
    type: Literal["leccion", "repaso", "cofre", "evaluacion"] = Field(alias="tipo")
    lesson: SyllabusId | None = Field(default=None, alias="leccion")

    @model_validator(mode="after")
    def _lesson_only_on_lesson_nodes(self) -> Self:
        if self.type == "leccion" and self.lesson is None:
            raise ValueError("un nodo 'leccion' necesita el campo 'leccion'")
        if self.type != "leccion" and self.lesson is not None:
            raise ValueError(f"un nodo '{self.type}' no lleva el campo 'leccion'")
        return self


class PathUnit(SyllabusModel):
    id: SyllabusId
    title: NonEmptyStr = Field(alias="titulo")
    nodes: list[PathNode] = Field(alias="nodos", min_length=1)


class PathSection(SyllabusModel):
    id: SyllabusId
    title: NonEmptyStr = Field(alias="titulo")
    units: list[PathUnit] = Field(alias="unidades", min_length=1)


class PathStage(SyllabusModel):
    id: SyllabusId
    title: NonEmptyStr = Field(alias="titulo")
    sections: list[PathSection] = Field(alias="secciones", min_length=1)


class LearningPath(SyllabusModel):
    stages: list[PathStage] = Field(alias="etapas", min_length=1)


# --- Ejercicios ------------------------------------------------------------------------------


class ExerciseBase(SyllabusModel):
    id: SyllabusId
    prompt: NonEmptyStr = Field(alias="enunciado")
    explanation: NonEmptyStr = Field(alias="explicacion")
    hints: list[NonEmptyStr] = Field(alias="pistas", min_length=2)


class MultipleChoiceExercise(ExerciseBase):
    type: Literal["multiple_choice"] = Field(alias="tipo")
    options: list[NonEmptyStr] = Field(alias="opciones", min_length=2)
    correct: int = Field(alias="correcta", ge=0)

    @model_validator(mode="after")
    def _correct_in_range(self) -> Self:
        if self.correct >= len(self.options):
            raise ValueError(
                f"'correcta' es {self.correct} pero solo hay {len(self.options)} opciones"
            )
        if len({option.casefold() for option in self.options}) != len(self.options):
            raise ValueError("hay opciones repetidas")
        return self


class FillPatternExercise(ExerciseBase):
    type: Literal["fill_pattern"] = Field(alias="tipo")
    accepted_answers: list[NonEmptyStr] = Field(alias="respuestas_aceptadas", min_length=1)


class NumericParameter(SyllabusModel):
    min: float
    max: float
    step: float = Field(alias="paso", gt=0)

    @model_validator(mode="after")
    def _range_is_valid(self) -> Self:
        if self.min > self.max:
            raise ValueError(f"min ({self.min}) es mayor que max ({self.max})")
        steps = (self.max - self.min) / self.step
        if abs(steps - round(steps)) > 1e-6:
            raise ValueError("(max - min) debe ser múltiplo de 'paso'")
        return self

    def values(self) -> list[float]:
        count = round((self.max - self.min) / self.step)
        return [round(self.min + i * self.step, 10) for i in range(count + 1)]


class Tolerance(SyllabusModel):
    type: Literal["relativa", "absoluta"] = Field(alias="tipo")
    value: float = Field(alias="valor", gt=0)


class NumericExercise(ExerciseBase):
    type: Literal["numeric"] = Field(alias="tipo")
    parameters: dict[str, NumericParameter] = Field(alias="parametros", min_length=1)
    solution: NonEmptyStr = Field(alias="solucion")
    unit: NonEmptyStr = Field(alias="unidad")
    tolerance: Tolerance = Field(alias="tolerancia")

    @field_validator("parameters")
    @classmethod
    def _parameter_names(cls, value: dict[str, NumericParameter]) -> dict[str, NumericParameter]:
        for name in value:
            if not name.isidentifier():
                raise ValueError(f"nombre de parámetro inválido: {name!r}")
        return value


Exercise = Annotated[
    MultipleChoiceExercise | FillPatternExercise | NumericExercise,
    Field(discriminator="type"),
]


# --- Lección ---------------------------------------------------------------------------------


class LessonFrontmatter(SyllabusModel):
    id: SyllabusId
    unit: SyllabusId = Field(alias="unidad")
    title: NonEmptyStr = Field(alias="titulo")
    objectives: list[NonEmptyStr] = Field(alias="objetivos", min_length=1)
    concepts: list[NonEmptyStr] = Field(alias="conceptos", min_length=1)
    exercises: list[Exercise] = Field(alias="ejercicios", min_length=1)


class Lesson(SyllabusModel):
    frontmatter: LessonFrontmatter
    theory: str
