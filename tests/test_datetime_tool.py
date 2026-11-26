
import pytest

from tools.datetime_tool import DateTimeTool
from tools.extended_task_router import ExtendedTaskRouter


tool = DateTimeTool()
router = ExtendedTaskRouter()


def test_current_date():

    assert tool.current_date()


def test_current_time():

    assert tool.current_time()


def test_current_day():

    assert tool.current_day() in (
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    )


def test_current_datetime():

    assert "UTC Offset:" in tool.current_datetime()


@pytest.mark.parametrize(
    "start,end,expected",
    [
        ("2026-01-01", "2026-12-31", 364),
        ("2024-02-28", "2024-03-01", 2),
        ("2026-01-01", "2026-01-01", 0),
        ("2026-01-10", "2026-01-01", 9),
    ],
)
def test_date_difference(start, end, expected):

    result = tool.date_difference(start, end)

    assert result["days"] == expected


@pytest.mark.parametrize(
    "start,days,expected",
    [
        ("2026-11-26", 30, "2026-12-26"),
        ("2026-11-26", -15, "2026-11-11"),
        ("2024-02-28", 1, "2024-02-29"),
        ("2026-12-31", 1, "2027-01-01"),
    ],
)
def test_add_days(start, days, expected):

    result = tool.add_days(start, days)

    assert result["result_date"] == expected


@pytest.mark.parametrize(
    "year,expected",
    [
        (2024, True),
        (2026, False),
        (2000, True),
        (1900, False),
    ],
)
def test_leap_year(year, expected):

    assert tool.is_leap_year(year) == expected


@pytest.mark.parametrize(
    "value",
    [
        "2026-02-30",
        "26-11-2026",
        "invalid",
    ],
)
def test_invalid_date(value):

    with pytest.raises(ValueError):

        tool.parse_date(value)


def test_date_router():

    assert "Today's date" in router.route(
        "What is today's date?"
    )


def test_date_difference_router():

    response = router.route(
        "Days between 2026-01-01 and 2026-12-31"
    )

    assert "364" in response


def test_date_adjustment_router():

    response = router.route(
        "Add 30 days to 2026-11-26"
    )

    assert "2026-12-26" in response
