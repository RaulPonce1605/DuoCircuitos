"""Evaluador seguro de las fórmulas `solucion` del temario.

Nunca usa `eval`/`exec`: parsea la fórmula a un AST de Python y solo acepta una lista blanca
de nodos, operadores, funciones y constantes. Todo se calcula con `float`, así que una potencia
enorme lanza `OverflowError` en lugar de crear enteros gigantes.
"""

import ast
import math
from collections.abc import Callable, Mapping

FUNCTIONS: dict[str, Callable[[float], float]] = {
    "sqrt": math.sqrt,
    "abs": abs,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "atan": math.atan,
    "log10": math.log10,
    "ln": math.log,
    "exp": math.exp,
}
CONSTANTS: dict[str, float] = {"pi": math.pi}

_BINARY_OPS: dict[type[ast.operator], Callable[[float, float], float]] = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
    ast.Pow: math.pow,
}
_UNARY_OPS: dict[type[ast.unaryop], Callable[[float], float]] = {
    ast.USub: lambda a: -a,
    ast.UAdd: lambda a: a,
}

MAX_FORMULA_LENGTH = 500


class FormulaError(ValueError):
    """La fórmula usa algo fuera de la lista blanca o no se puede evaluar."""


class Formula:
    """Fórmula ya validada; se puede evaluar muchas veces con distintos parámetros."""

    def __init__(self, source: str) -> None:
        if len(source) > MAX_FORMULA_LENGTH:
            raise FormulaError(f"la fórmula tiene más de {MAX_FORMULA_LENGTH} caracteres")
        try:
            tree = ast.parse(source.replace("^", "**"), mode="eval")
        except SyntaxError as exc:
            raise FormulaError(f"sintaxis inválida: {source!r}") from exc
        self.source = source
        self._body = tree.body
        self.variables: frozenset[str] = frozenset(_collect_variables(self._body))

    def evaluate(self, params: Mapping[str, float]) -> float:
        missing = self.variables - params.keys()
        if missing:
            raise FormulaError(f"faltan parámetros: {', '.join(sorted(missing))}")
        try:
            result = _eval(self._body, params)
        except (ArithmeticError, ValueError) as exc:
            raise FormulaError(f"no se puede evaluar {self.source!r}: {exc}") from exc
        if not math.isfinite(result):
            raise FormulaError(f"el resultado de {self.source!r} no es finito")
        return result


def _collect_variables(node: ast.expr) -> set[str]:
    """Valida el árbol completo y devuelve los nombres de parámetros que usa."""
    match node:
        case ast.Constant(value=value):
            if isinstance(value, bool) or not isinstance(value, int | float):
                raise FormulaError(f"constante no permitida: {value!r}")
            return set()
        case ast.Name(id=name):
            if name in FUNCTIONS:
                raise FormulaError(f"la función {name} necesita paréntesis")
            return set() if name in CONSTANTS else {name}
        case ast.BinOp(left=left, op=op, right=right):
            if type(op) not in _BINARY_OPS:
                raise FormulaError(f"operador no permitido: {type(op).__name__}")
            return _collect_variables(left) | _collect_variables(right)
        case ast.UnaryOp(op=op, operand=operand):
            if type(op) not in _UNARY_OPS:
                raise FormulaError(f"operador no permitido: {type(op).__name__}")
            return _collect_variables(operand)
        case ast.Call(func=ast.Name(id=name), args=[arg], keywords=[]):
            if name not in FUNCTIONS:
                raise FormulaError(f"función no permitida: {name}")
            return _collect_variables(arg)
        case _:
            raise FormulaError(f"expresión no permitida: {ast.dump(node)[:60]}")


def _eval(node: ast.expr, params: Mapping[str, float]) -> float:
    match node:
        case ast.Constant(value=int() | float() as value):
            return float(value)
        case ast.Name(id=name):
            return CONSTANTS[name] if name in CONSTANTS else float(params[name])
        case ast.BinOp(left=left, op=op, right=right):
            return _BINARY_OPS[type(op)](_eval(left, params), _eval(right, params))
        case ast.UnaryOp(op=op, operand=operand):
            return _UNARY_OPS[type(op)](_eval(operand, params))
        case ast.Call(func=ast.Name(id=name), args=[arg]):
            return float(FUNCTIONS[name](_eval(arg, params)))
    raise FormulaError("expresión no permitida")  # pragma: no cover - _collect_variables lo evita
