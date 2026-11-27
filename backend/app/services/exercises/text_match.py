"""Búsqueda de la solución dentro de un texto libre (lo usa el tutor; backend/CLAUDE.md 3.9).

Todas las funciones devuelven *spans* `(inicio, fin)` sobre el texto ORIGINAL, para poder
detectar (¿el texto revela la solución?) y también tachar (quitarla del material del prompt).
"""

import re
import unicodedata
from collections.abc import Callable, Iterator

from app.services.exercises.units import (
    MICRO,
    PREFIXES,
    InvalidQuantity,
    parse_number,
    unit_factor,
)

Span = tuple[int, int]

# Superíndices → dígitos, carácter por carácter (no cambia posiciones): "10⁻³" → "10-3".
_SUPERSCRIPTS = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺", "0123456789-+")
_QUANTITY = re.compile(
    r"(?<![\w.,])"
    r"(?P<number>[+-]?(?:\d+(?:[.,]\d+)?|[.,]\d+)(?:[eE][+-]?\d+)?)"
    r"(?:\s*[×xX*·]\s*10\s*\^?\s*(?P<exp>[+-]?\d{1,2}))?"
    r"(?:\s*(?P<unit>[A-Za-zΩµμ]+))?"
)
# Unidades de OTRAS magnitudes: "12 V" no es una corriente aunque el número coincida.
_KNOWN_UNITS = frozenset(
    {"V", "A", "Ω", "W", "s", "C", "F", "H", "Hz", "S", "J", "m", "min", "h", "g", "%"}
)
_PREFIX_CHARS = frozenset(prefix for prefix in PREFIXES if prefix) | {"u", "μ", "K"}


def fold(text: str) -> str:
    """Minúsculas y sin acentos, conservando la longitud (un carácter por carácter)."""
    return "".join(_fold_char(char) for char in text)


def _fold_char(char: str) -> str:
    decomposed = unicodedata.normalize("NFD", char)
    base = decomposed[0] if decomposed else char
    lowered = base.lower()
    return lowered if len(lowered) == 1 else base


def phrase_spans(text: str, phrase: str, *, plural: bool = True) -> list[Span]:
    """Dónde aparece `phrase` como palabra completa, sin distinguir mayúsculas ni acentos."""
    words = fold(phrase).split()
    if not words:
        return []
    suffix = r"(?:s|es)?" if plural else ""
    pattern = r"(?<!\w)" + r"\s+".join(re.escape(word) for word in words) + suffix + r"(?!\w)"
    return [match.span() for match in re.finditer(pattern, fold(text))]


def glued_spans(text: str, pieces: list[str]) -> list[Span]:
    """Dónde aparecen las piezas seguidas, con o sin espacios entre sus caracteres.

    Sirve para el patrón ya completado: ["G = 1 /", "R"] encuentra "G=1/R" o "G = 1 / R".
    """
    chars = [char for piece in pieces for char in fold(piece) if not char.isspace()]
    if not chars:
        return []
    pattern = r"\s*".join(re.escape(char) for char in chars) + r"(?!\w)"
    return [match.span() for match in re.finditer(pattern, fold(text))]


def quantity_spans(text: str, base_unit: str, matches: Callable[[float], bool]) -> list[Span]:
    """Cantidades del texto que, en la unidad base, cumplen `matches` (p. ej. el resultado).

    - Con unidad de la misma magnitud ("24 mA" para A) se convierte con su prefijo.
    - Con unidad de otra magnitud ("12 V" para A) se ignora.
    - Sin unidad ("24", "0.024") se prueba con todos los prefijos SI: 24 podría ser 24 mA.
    """
    return list(_quantity_spans(text.translate(_SUPERSCRIPTS), base_unit, matches))


def _quantity_spans(text: str, base_unit: str, matches: Callable[[float], bool]) -> Iterator[Span]:
    for match in _QUANTITY.finditer(text):
        if _is_list_marker(text, match):
            continue
        try:
            value = parse_number(match["number"])
        except InvalidQuantity:
            continue
        if match["exp"]:
            value *= 10.0 ** int(match["exp"])
        unit = match["unit"] or ""
        end = match.end("exp") if match["exp"] else match.end("number")
        candidates: list[float]
        if unit:
            try:
                candidates = [value * unit_factor(unit, base_unit)]
                end = match.end()
            except InvalidQuantity:
                if _is_other_unit(unit):
                    continue
                candidates = _with_every_prefix(value)  # "24 de corriente": sin unidad
        else:
            candidates = _with_every_prefix(value)
        if any(matches(candidate) for candidate in candidates):
            yield (match.start(), end)


def _is_list_marker(text: str, match: re.Match[str]) -> bool:
    """Al inicio de una línea, "2. Usa la ley..." o "2) ..." es un paso numerado, no una
    cantidad."""
    if match["exp"] or match["unit"]:
        return False
    line_start = text.rfind("\n", 0, match.start()) + 1
    after = text[match.end("number") : match.end("number") + 2]
    return (
        text[line_start : match.start()].strip() == ""
        and after[:1] in ".)"
        and (after[1:] == "" or after[1:].isspace())
    )


def _with_every_prefix(value: float) -> list[float]:
    return [value * 10.0**exponent for exponent in PREFIXES.values()]


def _is_other_unit(unit: str) -> bool:
    unit = unit.replace("μ", MICRO)
    if unit.lower().startswith("ohm"):
        return True
    return unit in _KNOWN_UNITS or (unit[0] in _PREFIX_CHARS and unit[1:] in _KNOWN_UNITS)


def redact(text: str, spans: list[Span], placeholder: str = "[…]") -> str:
    """Reemplaza los spans (que pueden traslaparse) por `placeholder`."""
    if not spans:
        return text
    merged: list[list[int]] = []
    for start, end in sorted(spans):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    pieces: list[str] = []
    cursor = 0
    for start, end in merged:
        pieces.append(text[cursor:start])
        pieces.append(placeholder)
        cursor = end
    pieces.append(text[cursor:])
    return "".join(pieces)
