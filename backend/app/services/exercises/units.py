"""Lectura y formato de magnitudes con prefijos SI ("22.7 mA", "4,7 kΩ", "1.2e-3 A").

Lo que escribe el alumno se interpreta aquí, en el backend; la app solo manda el texto.
"""

import math
import re
import unicodedata

MICRO = "µ"  # µ, signo micro (la notación del temario)
OHM = "Ω"  # Ω, omega griega (NFKC convierte el signo de ohm U+2126 en esta)

# Prefijos SI que se aceptan. Distinguen mayúsculas: "m" es mili y "M" es mega.
PREFIXES: dict[str, int] = {
    "p": -12,
    "n": -9,
    MICRO: -6,
    "m": -3,
    "": 0,
    "k": 3,
    "M": 6,
    "G": 9,
}
# Tras NFKC, el signo micro se vuelve mu griega (U+03BC); también se acepta "u" (teclados).
_MICRO_ALIASES = ("μ", "u")
_OHM_WORDS = ("ohms", "ohm")
_NUMBER = re.compile(r"^[+-]?(\d+(\.\d*)?|\.\d+)(e[+-]?\d+)?$", re.IGNORECASE)
_MAX_ABS = 1e15  # nadie escribe más de un petavolt; evita números absurdos


class InvalidQuantity(ValueError):
    """El texto no es un número válido o la unidad no corresponde a la esperada."""


def parse_number(text: str) -> float:
    cleaned = unicodedata.normalize("NFKC", text).strip().replace(" ", "")
    if cleaned.count(",") == 1 and "." not in cleaned:
        cleaned = cleaned.replace(",", ".")  # coma decimal: "2,5"
    if not _NUMBER.match(cleaned):
        raise InvalidQuantity(f"no es un número: {text!r}")
    value = float(cleaned)
    if not math.isfinite(value) or abs(value) > _MAX_ABS:
        raise InvalidQuantity(f"número fuera de rango: {text!r}")
    return value


def unit_factor(unit_text: str, base_unit: str) -> float:
    """Factor para pasar de `unit_text` (con prefijo opcional) a la unidad base.

    Sin unidad se asume la unidad base. Lanza `InvalidQuantity` si es otra magnitud.
    """
    unit = _normalize_unit(unit_text)
    base = _normalize_unit(base_unit)
    if unit == "":
        return 1.0
    if not unit.lower().endswith(base.lower()):
        raise InvalidQuantity(f"unidad {unit_text!r} no es de {base_unit}")
    prefix = unit[: len(unit) - len(base)]
    if prefix == "K":
        prefix = "k"  # error común: "KΩ"
    if prefix not in PREFIXES:
        raise InvalidQuantity(f"prefijo desconocido en {unit_text!r}")
    return 10.0 ** PREFIXES[prefix]


def parse_quantity(value_text: str, unit_text: str, base_unit: str) -> float:
    """Valor en la unidad base: parse_quantity("22.7", "mA", "A") == 0.0227."""
    return parse_number(value_text) * unit_factor(unit_text, base_unit)


def format_number(value: float, significant: int = 4) -> str:
    """Número legible para enunciados y respuestas: 5 → "5", 0.5 → "0.5", 22.727 → "22.73"."""
    if value == 0:
        return "0"
    if float(value).is_integer() and abs(value) < 1e9:
        return str(int(value))
    text = f"{value:.{significant}g}"
    if "e" in text:
        mantissa, exponent = text.split("e")
        return f"{mantissa} × 10^{int(exponent)}"
    return text


def format_quantity(value: float, base_unit: str, significant: int = 3) -> str:
    """Elige el prefijo SI que deja la cifra entre 1 y 1000: 0.0227 A → "22.7 mA"."""
    if value == 0 or not math.isfinite(value):
        return f"{format_number(value)} {base_unit}"
    exponent = math.floor(math.log10(abs(value)) / 3) * 3
    exponent = max(min(exponent, max(PREFIXES.values())), min(PREFIXES.values()))
    prefix = next(p for p, e in PREFIXES.items() if e == exponent)
    scaled = float(f"{value / 10.0**exponent:.{significant}g}")
    return f"{format_number(scaled, significant)} {prefix}{base_unit}"


def _normalize_unit(text: str) -> str:
    unit = unicodedata.normalize("NFKC", text).strip().replace(" ", "")
    for word in _OHM_WORDS:
        if unit.lower().endswith(word):
            unit = unit[: len(unit) - len(word)] + OHM
            break
    if len(unit) > 1 and unit[0] in _MICRO_ALIASES:
        unit = MICRO + unit[1:]
    return unit
