
import pytest

from decimal import Decimal

from tools.unit_converter import UnitConverter
from tools.extended_task_router import ExtendedTaskRouter


converter = UnitConverter()
router = ExtendedTaskRouter()


@pytest.mark.parametrize(
    "value,source,target,expected",
    [
        (25, "km", "m", "25000"),
        (100, "cm", "m", "1"),
        (1, "inch", "cm", "2.54"),
        (1, "mile", "m", "1609.344"),

        (5, "kg", "g", "5000"),
        (1000, "mg", "g", "1"),
        (1, "lb", "kg", "0.45359237"),

        (100, "c", "f", "212"),
        (32, "f", "c", "0"),
        (0, "c", "k", "273.15"),
        ("273.15", "k", "c", "0"),
        (-40, "c", "f", "-40"),

        (2, "hours", "minutes", "120"),
        (1, "day", "seconds", "86400"),

        (5, "litres", "ml", "5000"),
        (1, "gallon", "l", "3.785411784"),

        (2, "hectares", "m2", "20000"),
        (1, "acre", "m2", "4046.8564224"),

        (5, "gb", "mb", "5000"),
        (1, "gib", "mib", "1024"),
    ],
)
def test_unit_conversion(
    value,
    source,
    target,
    expected,
):

    result = converter.convert(
        value,
        source,
        target,
    )

    assert result == Decimal(expected)


@pytest.mark.parametrize(
    "value,source,target",
    [
        (5, "kg", "km"),
        (10, "unknown", "m"),
        (10, "m", "unknown"),
        (-300, "c", "f"),
        (-1, "k", "c"),
    ],
)
def test_invalid_conversion(value, source, target):

    with pytest.raises(ValueError):

        converter.convert(
            value,
            source,
            target,
        )


def test_natural_language_conversion():

    response = router.route(
        "Convert 25 km to metres"
    )

    assert "25000" in response


def test_temperature_router():

    response = router.route(
        "Convert 100 Celsius to Fahrenheit"
    )

    assert "212" in response


def test_existing_calculator():

    assert "400" in router.route(
        "Calculate 25 x 16"
    )


def test_existing_gst():

    assert "29,500.00" in router.route(
        "Calculate 18% GST on 25000"
    )


def test_normal_ai_question():

    assert router.route(
        "What is Python?"
    ) is None


def test_existing_file_request():

    assert router.route(
        "Create a PDF report about Python."
    ) is None
