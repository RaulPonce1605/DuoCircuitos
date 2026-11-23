from collections.abc import Callable
from pathlib import Path

import pytest

from app.content_import.validate import DEFAULT_SYLLABUS_DIR, main, validate_syllabus

PATH_YAML = """\
etapas:
  - id: e1-fundamentos
    titulo: Fundamentos
    secciones:
      - id: s1-magnitudes
        titulo: Magnitudes eléctricas
        unidades:
          - id: u01-ley-de-ohm
            titulo: Ley de Ohm
            nodos:
              - { tipo: leccion, leccion: ohm-01 }
              - { tipo: repaso }
              - { tipo: cofre }
              - { tipo: evaluacion }
"""

LESSON_MD = """\
---
id: ohm-01
unidad: u01-ley-de-ohm
titulo: Voltaje, corriente y resistencia
objetivos:
  - Calcular la corriente con la Ley de Ohm.
conceptos:
  - Ley de Ohm
ejercicios:
  - id: ohm-01-mc
    tipo: multiple_choice
    enunciado: "Si el voltaje se mantiene y la resistencia se duplica, la corriente…"
    opciones: ["Se duplica", "Se reduce a la mitad", "No cambia"]
    correcta: 1
    explicacion: "Con V constante, I = V / R."
    pistas:
      - "¿Qué ecuación relaciona las tres magnitudes?"
      - "Escribe I en función de V y R."
  - id: ohm-01-fill
    tipo: fill_pattern
    enunciado: "V = I · ___"
    respuestas_aceptadas: ["R"]
    explicacion: "La Ley de Ohm es V = I · R."
    pistas:
      - "Falta la magnitud que se opone al paso de la corriente."
      - "Se mide en ohms."
  - id: ohm-01-calc
    tipo: numeric
    enunciado: "Una resistencia de {R} Ω está conectada a {V} V. ¿Qué corriente circula?"
    parametros:
      V: { min: 5, max: 24, paso: 1 }
      R: { min: 100, max: 1000, paso: 50 }
    solucion: "V / R"
    unidad: A
    tolerancia: { tipo: relativa, valor: 0.02 }
    explicacion: "I = V / R."
    pistas:
      - "¿Qué magnitud te piden?"
      - "Despeja I de V = I · R."
---

La **Ley de Ohm** relaciona voltaje, corriente y resistencia.
"""

Writer = Callable[[str, str], None]


@pytest.fixture
def syllabus(tmp_path: Path) -> Path:
    (tmp_path / "camino.yaml").write_text(PATH_YAML, encoding="utf-8")
    lesson = tmp_path / "unidades" / "u01-ley-de-ohm" / "ohm-01.md"
    lesson.parent.mkdir(parents=True)
    lesson.write_text(LESSON_MD, encoding="utf-8")
    return tmp_path


def _replace(root: Path, relative: str, old: str, new: str) -> None:
    target = root / relative
    text = target.read_text(encoding="utf-8")
    assert old in text, f"{old!r} no está en {relative}"
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


def _errors(root: Path) -> str:
    return "\n".join(validate_syllabus(root).errors)


LESSON = "unidades/u01-ley-de-ohm/ohm-01.md"


def test_valid_syllabus_has_no_errors(syllabus: Path) -> None:
    report = validate_syllabus(syllabus)

    assert report.errors == []
    assert list(report.lessons) == ["ohm-01"]
    assert len(report.lessons["ohm-01"].frontmatter.exercises) == 3


def test_cli_returns_zero_for_valid_and_one_for_invalid(syllabus: Path) -> None:
    assert main([str(syllabus)]) == 0
    _replace(syllabus, LESSON, "correcta: 1", "correcta: 7")
    assert main([str(syllabus)]) == 1


@pytest.mark.parametrize(
    ("relative", "old", "new", "expected"),
    [
        ("camino.yaml", "leccion: ohm-01", "leccion: ohm-99", "'ohm-99', que no existe"),
        ("camino.yaml", "{ tipo: cofre }", "{ tipo: tesoro }", "nodos.2.tipo"),
        ("camino.yaml", "{ tipo: cofre }", "{ tipo: cofre, leccion: ohm-01 }", "no lleva"),
        ("camino.yaml", "id: u01-ley-de-ohm", "id: U01 Ley", "id"),
        (LESSON, "id: ohm-01\n", "id: ohm-02\n", "no coincide con el nombre del archivo"),
        (LESSON, "unidad: u01-ley-de-ohm", "unidad: u02-otra", "carpeta"),
        (LESSON, "correcta: 1", "correcta: 3", "solo hay 3 opciones"),
        (LESSON, '      - "Se mide en ohms."\n', "", "pistas"),
        (LESSON, 'solucion: "V / R"', 'solucion: "V / Rx"', "'Rx', que no está"),
        (LESSON, 'solucion: "V / R"', 'solucion: "eval(V)"', "función no permitida"),
        (LESSON, 'solucion: "V / R"', 'solucion: "V / (R - 100)"', "con "),
        (LESSON, "{ min: 5, max: 24, paso: 1 }", "{ min: 5, max: 24, paso: 0 }", "paso"),
        (LESSON, "{ min: 5, max: 24, paso: 1 }", "{ min: 5, max: 24, paso: 2 }", "múltiplo"),
        (LESSON, "{ min: 5, max: 24, paso: 1 }", "{ min: 30, max: 24, paso: 1 }", "mayor"),
        (LESSON, "valor: 0.02", "valor: 0", "tolerancia"),
        (LESSON, "    unidad: A\n", "", "unidad"),
        (LESSON, "de {R} Ω", "de R Ω", "'R' no aparece en el enunciado"),
        (LESSON, "de {R} Ω", "de {R} Ω y {X}", "{X}, que no está"),
        (LESSON, '    explicacion: "I = V / R."\n', "", "explicacion"),
        (
            LESSON,
            "Escribe I en función de V y R.",
            "Se reduce a la mitad.",
            "contiene la respuesta",
        ),
        (LESSON, "tipo: fill_pattern", "tipo: dibujo", "tipo"),
        (LESSON, "id: ohm-01-fill", "id: ohm-01-mc", "ejercicio repetido"),
        (LESSON, "La **Ley de Ohm** relaciona voltaje, corriente y resistencia.\n", "", "teoría"),
        (LESSON, "objetivos:", "objetivo:", "objetivos"),
    ],
)
def test_detects_invalid_syllabus(
    syllabus: Path, relative: str, old: str, new: str, expected: str
) -> None:
    _replace(syllabus, relative, old, new)

    assert expected in _errors(syllabus)


def test_lesson_missing_from_path_is_reported(syllabus: Path) -> None:
    extra = syllabus / "unidades" / "u01-ley-de-ohm" / "ohm-02.md"
    extra.write_text(LESSON_MD.replace("id: ohm-01\n", "id: ohm-02\n"), encoding="utf-8")

    assert "no aparece en camino.yaml" in _errors(syllabus)


def test_review_before_first_lesson_is_reported(syllabus: Path) -> None:
    _replace(
        syllabus,
        "camino.yaml",
        "- { tipo: leccion, leccion: ohm-01 }\n              - { tipo: repaso }",
        "- { tipo: repaso }\n              - { tipo: leccion, leccion: ohm-01 }",
    )

    assert "repaso antes de su primera lección" in _errors(syllabus)


def test_missing_frontmatter_is_reported(syllabus: Path) -> None:
    (syllabus / LESSON).write_text("# Sin frontmatter\n", encoding="utf-8")

    assert "falta el frontmatter" in _errors(syllabus)


def test_missing_path_file_is_reported(tmp_path: Path) -> None:
    assert "camino.yaml: no existe" in _errors(tmp_path)


@pytest.mark.skipif(
    not (DEFAULT_SYLLABUS_DIR / "camino.yaml").is_file(), reason="el temario aún no existe"
)
def test_real_syllabus_is_valid() -> None:
    report = validate_syllabus(DEFAULT_SYLLABUS_DIR)

    assert report.errors == []
