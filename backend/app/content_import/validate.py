"""Valida el formato y la coherencia de todo el temario.

Uso (desde `backend/`):

    uv run python -m app.content_import.validate            # valida ../contenido
    uv run python -m app.content_import.validate RUTA       # valida otra carpeta

Sale con código 1 y lista los errores si algo no cumple `contenido/README.md`.
"""

import io
import itertools
import random
import re
import sys
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from pydantic import ValidationError

from app.content_import.schema import (
    CircuitDiagramExercise,
    FillPatternExercise,
    LearningPath,
    Lesson,
    LessonFrontmatter,
    MultipleChoiceExercise,
    NumericExercise,
)
from app.services.exercises.formula import Formula, FormulaError

DEFAULT_SYLLABUS_DIR = Path(__file__).resolve().parents[3] / "contenido"
PATH_FILE = "camino.yaml"
UNITS_DIR = "unidades"

_FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n?(.*)\Z", re.DOTALL)
_PLACEHOLDER = re.compile(r"\{([^{}]*)\}")
_RANDOM_SAMPLES = 200


@dataclass
class ValidationReport:
    errors: list[str] = field(default_factory=list)
    path: LearningPath | None = None
    lessons: dict[str, Lesson] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.errors

    def add(self, where: str, message: str) -> None:
        self.errors.append(f"{where}: {message}")


def validate_syllabus(root: Path) -> ValidationReport:
    report = ValidationReport()
    report.path = _load_path(root, report)
    lesson_files = _load_lessons(root, report)
    if report.path is not None:
        _check_path(report.path, lesson_files, report)
    return report


# --- Carga -----------------------------------------------------------------------------------


def _load_path(root: Path, report: ValidationReport) -> LearningPath | None:
    path_file = root / PATH_FILE
    if not path_file.is_file():
        report.add(PATH_FILE, "no existe")
        return None
    try:
        data = yaml.safe_load(path_file.read_text(encoding="utf-8"))
        return LearningPath.model_validate(data)
    except yaml.YAMLError as exc:
        report.add(PATH_FILE, f"YAML inválido: {exc}")
    except ValidationError as exc:
        _add_validation_errors(report, PATH_FILE, exc)
    return None


def _load_lessons(root: Path, report: ValidationReport) -> dict[str, Path]:
    """Carga cada lección; devuelve id → archivo de las que se pudieron leer."""
    files: dict[str, Path] = {}
    units_dir = root / UNITS_DIR
    for lesson_file in sorted(units_dir.glob("*/*.md")):
        where = lesson_file.relative_to(root).as_posix()
        lesson = _parse_lesson(lesson_file, where, report)
        if lesson is None:
            continue
        lesson_id = lesson.frontmatter.id
        if lesson_id != lesson_file.stem:
            report.add(where, f"el id '{lesson_id}' no coincide con el nombre del archivo")
        if lesson.frontmatter.unit != lesson_file.parent.name:
            report.add(
                where,
                f"'unidad' es '{lesson.frontmatter.unit}' pero el archivo está en la carpeta "
                f"'{lesson_file.parent.name}'",
            )
        if lesson_id in files:
            report.add(where, f"id de lección repetido (también en {files[lesson_id]})")
            continue
        files[lesson_id] = lesson_file
        report.lessons[lesson_id] = lesson
        _check_lesson(lesson, where, report)
    stray = [p for p in units_dir.rglob("*") if p.is_file() and p.suffix != ".md"]
    for path in stray:
        if path.name != ".gitkeep":
            report.add(path.relative_to(root).as_posix(), "archivo inesperado (solo .md)")
    return files


def _parse_lesson(lesson_file: Path, where: str, report: ValidationReport) -> Lesson | None:
    match = _FRONTMATTER.match(lesson_file.read_text(encoding="utf-8"))
    if match is None:
        report.add(where, "falta el frontmatter YAML entre líneas '---'")
        return None
    raw_frontmatter, theory = match.groups()
    try:
        data = yaml.safe_load(raw_frontmatter)
        frontmatter = LessonFrontmatter.model_validate(data)
    except yaml.YAMLError as exc:
        report.add(where, f"YAML inválido: {exc}")
        return None
    except ValidationError as exc:
        _add_validation_errors(report, where, exc)
        return None
    return Lesson(frontmatter=frontmatter, theory=theory.strip())


def _add_validation_errors(report: ValidationReport, where: str, exc: ValidationError) -> None:
    for error in exc.errors():
        location = ".".join(str(part) for part in error["loc"]) or "(raíz)"
        report.add(where, f"{location}: {error['msg']}")


# --- Reglas de una lección -------------------------------------------------------------------


def _check_lesson(lesson: Lesson, where: str, report: ValidationReport) -> None:
    if not lesson.theory:
        report.add(where, "falta la teoría en el cuerpo de la lección")
    duplicated = _duplicates(exercise.id for exercise in lesson.frontmatter.exercises)
    for exercise_id in duplicated:
        report.add(where, f"id de ejercicio repetido: {exercise_id}")
    for exercise in lesson.frontmatter.exercises:
        exercise_where = f"{where} [{exercise.id}]"
        if isinstance(exercise, NumericExercise):
            _check_numeric(exercise, exercise_where, report)
        else:
            if _PLACEHOLDER.search(exercise.prompt):
                report.add(exercise_where, "solo los ejercicios 'numeric' usan {parametros}")
            if isinstance(exercise, MultipleChoiceExercise):
                _check_hints_hide(
                    exercise.hints, [exercise.options[exercise.correct]], exercise_where, report
                )
            elif isinstance(exercise, CircuitDiagramExercise):
                labels = exercise.correct_labels()
                _check_hints_hide(exercise.hints, labels, exercise_where, report)
                for label in labels:
                    if _contains_word(exercise.prompt, label):
                        report.add(exercise_where, f"el enunciado ya dice la respuesta '{label}'")
            elif isinstance(exercise, FillPatternExercise):
                _check_hints_hide(exercise.hints, exercise.accepted_answers, exercise_where, report)
                for answer in exercise.accepted_answers:
                    if _contains_word(exercise.prompt, answer):
                        report.add(exercise_where, f"el enunciado ya dice la respuesta '{answer}'")


def _contains_word(text: str, answer: str) -> bool:
    """¿Aparece la respuesta como palabra completa? Las de una letra ("R") no cuentan: aparecen
    en cualquier texto."""
    word = answer.strip()
    if len(word) < 2:
        return False
    return re.search(rf"(?<!\w){re.escape(word)}(?!\w)", text, re.IGNORECASE) is not None


def _check_hints_hide(
    hints: list[str], answers: list[str], where: str, report: ValidationReport
) -> None:
    """Ninguna pista puede contener la respuesta como palabra completa."""
    for answer in answers:
        for number, hint in enumerate(hints, start=1):
            if _contains_word(hint, answer):
                report.add(where, f"la pista {number} contiene la respuesta '{answer}'")


def _check_numeric(exercise: NumericExercise, where: str, report: ValidationReport) -> None:
    try:
        formula = Formula(exercise.solution)
    except FormulaError as exc:
        report.add(where, f"solucion: {exc}")
        return

    params = set(exercise.parameters)
    for name in sorted(formula.variables - params):
        report.add(where, f"la solución usa '{name}', que no está en 'parametros'")
    placeholders = set(_PLACEHOLDER.findall(exercise.prompt))
    for name in sorted(placeholders - params):
        report.add(where, f"el enunciado usa {{{name}}}, que no está en 'parametros'")
    for name in sorted(params - placeholders):
        report.add(where, f"el parámetro '{name}' no aparece en el enunciado como {{{name}}}")
    if formula.variables - params:
        return

    for values in _parameter_samples(exercise):
        try:
            formula.evaluate(values)
        except FormulaError as exc:
            shown = ", ".join(f"{k}={v:g}" for k, v in values.items())
            report.add(where, f"con {shown}: {exc}")
            return


def _parameter_samples(exercise: NumericExercise) -> list[dict[str, float]]:
    """Todas las esquinas del rango (min/max) más muestras al azar reproducibles."""
    names = list(exercise.parameters)
    ranges = [exercise.parameters[name].values() for name in names]
    corners = itertools.product(*[(r[0], r[-1]) for r in ranges])
    samples = [dict(zip(names, corner, strict=True)) for corner in corners]
    rng = random.Random(exercise.id)  # noqa: S311 - no es criptografía, solo muestreo
    samples.extend(
        {name: rng.choice(values) for name, values in zip(names, ranges, strict=True)}
        for _ in range(_RANDOM_SAMPLES)
    )
    return samples


# --- Reglas del camino -----------------------------------------------------------------------


def _check_path(
    path: LearningPath, lesson_files: dict[str, Path], report: ValidationReport
) -> None:
    stage_ids = [stage.id for stage in path.stages]
    sections = [section for stage in path.stages for section in stage.sections]
    units = [unit for section in sections for unit in section.units]
    for label, ids in (
        ("etapa", stage_ids),
        ("sección", [section.id for section in sections]),
        ("unidad", [unit.id for unit in units]),
    ):
        for duplicated in _duplicates(ids):
            report.add(PATH_FILE, f"id de {label} repetido: {duplicated}")

    referenced: Counter[str] = Counter()
    for unit in units:
        lesson_nodes = [node.lesson for node in unit.nodes if node.lesson is not None]
        if not lesson_nodes:
            report.add(PATH_FILE, f"la unidad '{unit.id}' no tiene ninguna lección")
        first_lesson = (
            next(i for i, n in enumerate(unit.nodes) if n.type == "leccion") if lesson_nodes else 0
        )
        for node in unit.nodes[:first_lesson]:
            if node.type in ("repaso", "evaluacion"):
                report.add(
                    PATH_FILE,
                    f"la unidad '{unit.id}' tiene un {node.type} antes de su primera lección",
                )
        for lesson_id in lesson_nodes:
            referenced[lesson_id] += 1
            lesson = report.lessons.get(lesson_id)
            if lesson_id not in lesson_files:
                report.add(
                    PATH_FILE, f"la unidad '{unit.id}' usa la lección '{lesson_id}', que no existe"
                )
            elif lesson is not None and lesson.frontmatter.unit != unit.id:
                report.add(
                    PATH_FILE,
                    f"la lección '{lesson_id}' está en la unidad '{unit.id}' pero declara "
                    f"'unidad: {lesson.frontmatter.unit}'",
                )

    for lesson_id, count in sorted(referenced.items()):
        if count > 1:
            report.add(PATH_FILE, f"la lección '{lesson_id}' aparece {count} veces en el camino")
    for lesson_id, lesson_file in sorted(lesson_files.items()):
        if lesson_id not in referenced:
            report.add(lesson_file.name, "la lección no aparece en camino.yaml")


def _duplicates(values: Iterable[str]) -> list[str]:
    counts = Counter(values)
    return sorted(value for value, count in counts.items() if count > 1)


# --- CLI -------------------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    root = Path(args[0]) if args else DEFAULT_SYLLABUS_DIR
    report = validate_syllabus(root)
    if not report.ok:
        print(f"El temario en {root} tiene {len(report.errors)} error(es):")
        for error in report.errors:
            print(f"  - {error}")
        return 1
    exercises = sum(len(lesson.frontmatter.exercises) for lesson in report.lessons.values())
    print(f"Temario válido: {len(report.lessons)} lecciones, {exercises} ejercicios.")
    return 0


if __name__ == "__main__":
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")  # la consola de Windows no usa UTF-8
    sys.exit(main())
