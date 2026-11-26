
import pytest

from decimal import Decimal

from tools.calculator import Calculator
from tools.task_router import TaskRouter


calculator = Calculator()
router = TaskRouter()


@pytest.mark.parametrize(
    "expression,expected",
    [
        ("25 + 16", "41"),
        ("100 - 25", "75"),
        ("25 * 16", "400"),
        ("100 / 5", "20"),
        ("254 * 876", "222504"),
        ("(25 + 15) * 2", "80"),
        ("2 ** 10", "1024"),
        ("100 % 7", "2"),
        ("0.1 + 0.2", "0.3"),
        ("25 × 16", "400"),
        ("100 ÷ 5", "20"),
        ("-10 + 5", "-5"),
    ],
)
def test_calculation(expression, expected):

    assert calculator.calculate(
        expression
    ) == Decimal(expected)


def test_gst():

    result = calculator.gst(
        25000,
        18,
    )

    assert result["gst"] == Decimal("4500.00")
    assert result["total"] == Decimal("29500.00")


def test_discount():

    result = calculator.discount(
        5000,
        15,
    )

    assert result["discount"] == Decimal("750.00")
    assert result["total"] == Decimal("4250.00")


def test_percentage():

    assert calculator.percentage(
        25,
        15000,
    ) == Decimal("3750")


@pytest.mark.parametrize(
    "expression",
    [
        "100 / 0",
        "2 ** 1000000",
        "__import__('os')",
        "print('Hello')",
        "open('test.txt')",
        "[1, 2, 3]",
        "True",
    ],
)
def test_unsafe_expression(expression):

    with pytest.raises(ValueError):

        calculator.calculate(expression)


def test_invalid_gst():

    with pytest.raises(ValueError):

        calculator.gst(-5000, 18)


def test_invalid_discount():

    with pytest.raises(ValueError):

        calculator.discount(5000, 150)


def test_task_router_calculation():

    response = router.route(
        "Calculate 25 x 16"
    )

    assert "400" in response


def test_task_router_gst():

    response = router.route(
        "Calculate 18% GST on ₹25,000"
    )

    assert "29,500.00" in response


def test_task_router_discount():

    response = router.route(
        "Apply 15% discount on 5000"
    )

    assert "4,250.00" in response


def test_task_router_percentage():

    response = router.route(
        "Calculate 25% of 15000"
    )

    assert "3750" in response


def test_normal_ai_question():

    assert router.route(
        "What is Laravel?"
    ) is None


def test_file_request():

    assert router.route(
        "Create a PDF report about Python."
    ) is None
