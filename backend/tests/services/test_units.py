import pytest

from app.services.exercises.units import (
    InvalidQuantity,
    format_number,
    format_quantity,
    parse_number,
    parse_quantity,
)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("22.7", 22.7),
        ("2,5", 2.5),
        (" 3 ", 3.0),
        ("-4", -4.0),
        (".5", 0.5),
        ("1.2e-3", 0.0012),
        ("1.2E3", 1200.0),
        ("１２", 12.0),  # dígitos de ancho completo (teclados asiáticos) por NFKC
    ],
)
def test_parse_number(text: str, expected: float) -> None:
    assert parse_number(text) == pytest.approx(expected)


@pytest.mark.parametrize(
    "text",
    ["", "abc", "1.2.3", "1,000.5", "1,2,3", "nan", "inf", "1e999", "1e16", "0x10", "1/2", "2^3"],
)
def test_parse_number_rejects(text: str) -> None:
    with pytest.raises(InvalidQuantity):
        parse_number(text)


@pytest.mark.parametrize(
    ("value", "unit", "base", "expected"),
    [
        ("22.7", "mA", "A", 0.0227),
        ("0.0227", "A", "A", 0.0227),
        ("0.0227", "", "A", 0.0227),
        ("22.7", "ma", "A", 0.0227),
        ("4.7", "kΩ", "Ω", 4700),
        ("4.7", "KΩ", "Ω", 4700),
        ("4.7", "kΩ", "Ω", 4700),  # signo de ohm U+2126 vs omega griega
        ("4.7", "kohm", "Ω", 4700),
        ("4.7", "kOhms", "Ω", 4700),
        ("470", "ohm", "Ω", 470),
        ("10", "µC", "C", 1e-5),  # signo micro U+00B5
        ("10", "μC", "C", 1e-5),  # mu griega U+03BC
        ("10", "uC", "C", 1e-5),
        ("15", "ms", "s", 0.015),
        ("2", "MW", "W", 2e6),
        ("2", "mW", "W", 2e-3),
        ("3", "nJ", "J", 3e-9),
    ],
)
def test_parse_quantity(value: str, unit: str, base: str, expected: float) -> None:
    assert parse_quantity(value, unit, base) == pytest.approx(expected)


@pytest.mark.parametrize(
    ("unit", "base"),
    [("V", "A"), ("mV", "A"), ("xA", "A"), ("m", "A"), ("kΩ", "A"), ("AA", "A")],
)
def test_parse_quantity_rejects_wrong_unit(unit: str, base: str) -> None:
    with pytest.raises(InvalidQuantity):
        parse_quantity("1", unit, base)


@pytest.mark.parametrize(
    ("value", "expected"),
    [(5, "5"), (5.0, "5"), (0.5, "0.5"), (22.72727, "22.73"), (1200, "1200"), (0, "0")],
)
def test_format_number(value: float, expected: str) -> None:
    assert format_number(value) == expected


@pytest.mark.parametrize(
    ("value", "base", "expected"),
    [
        (0.0227273, "A", "22.7 mA"),
        (3, "A", "3 A"),
        (650, "Ω", "650 Ω"),
        (5000, "Ω", "5 kΩ"),
        (100000, "Ω", "100 kΩ"),
        (1.72, "Ω", "1.72 Ω"),
        (0.001, "C", "1 mC"),
        (5e-5, "C", "50 µC"),
        (0.005, "J", "5 mJ"),
        (6.32121, "V", "6.32 V"),
        (0, "V", "0 V"),
    ],
)
def test_format_quantity(value: float, base: str, expected: str) -> None:
    assert format_quantity(value, base) == expected


def test_formatted_quantity_parses_back() -> None:
    for value in [0.0227273, 4700, 5e-5, 1.72, 123456, 0.000999]:
        number, unit = format_quantity(value, "A").split(" ")
        assert parse_quantity(number, unit, "A") == pytest.approx(value, rel=0.005)
