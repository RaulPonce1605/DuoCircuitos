import math

import pytest

from app.services.exercises.formula import Formula, FormulaError


@pytest.mark.parametrize(
    ("source", "params", "expected"),
    [
        ("V / R", {"V": 12, "R": 4}, 3.0),
        ("R1 * R2 / (R1 + R2)", {"R1": 6, "R2": 3}, 2.0),
        ("V^2 / R", {"V": 120, "R": 240}, 60.0),
        ("-x + 1", {"x": 2}, -1.0),
        ("sqrt(x) + abs(-2)", {"x": 9}, 5.0),
        ("Vs * (1 - exp(-t / (R * C)))", {"Vs": 10, "t": 1, "R": 1, "C": 1}, 10 * (1 - math.e**-1)),
        ("ln(exp(2)) + log10(100)", {}, 4.0),
        ("2 * pi", {}, 2 * math.pi),
        ("1.72e-8 * L / (A * 1e-6)", {"L": 100, "A": 1}, 1.72),
    ],
)
def test_evaluates_whitelisted_formulas(
    source: str, params: dict[str, float], expected: float
) -> None:
    assert Formula(source).evaluate(params) == pytest.approx(expected)


def test_reports_variables_without_constants() -> None:
    assert Formula("2 * pi * f * C + sqrt(L)").variables == {"f", "C", "L"}


@pytest.mark.parametrize(
    "source",
    [
        "__import__('os').system('echo hola')",
        "open('x')",
        "x.real",
        "[1, 2]",
        "x if y else z",
        "x == 1",
        "max(1, 2)",
        "sqrt(1, 2)",
        "sqrt",
        "'texto'",
        "True",
        "lambda: 1",
        "x % 2",
        "x // 2",
        "x(1)",
    ],
)
def test_rejects_anything_outside_the_whitelist(source: str) -> None:
    with pytest.raises(FormulaError):
        Formula(source)


@pytest.mark.parametrize(
    ("source", "params"),
    [
        ("1 / x", {"x": 0}),
        ("sqrt(x)", {"x": -1}),
        ("10 ^ 10 ^ 10", {}),
        ("ln(x)", {"x": 0}),
    ],
)
def test_math_errors_become_formula_errors(source: str, params: dict[str, float]) -> None:
    with pytest.raises(FormulaError):
        Formula(source).evaluate(params)


def test_missing_parameter_is_an_error() -> None:
    with pytest.raises(FormulaError, match="faltan parámetros: R"):
        Formula("V / R").evaluate({"V": 1})


def test_rejects_very_long_formulas() -> None:
    with pytest.raises(FormulaError):
        Formula("x + " * 200 + "x")
