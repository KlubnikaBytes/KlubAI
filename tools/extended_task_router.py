
import re

from tools.task_router import TaskRouter
from tools.datetime_tool import DateTimeTool
from tools.unit_converter import UnitConverter


class ExtendedTaskRouter(TaskRouter):

    DATE_PATTERN = r"\d{4}-\d{2}-\d{2}"

    def __init__(self):

        super().__init__()

        self.datetime_tool = DateTimeTool()
        self.unit_converter = UnitConverter()

    def get_help(self):

        return (
            super().get_help()
            + "\n\n"
            "Date and Time Commands\n\n"
            "/date - Current date\n"
            "/time - Current time\n"
            "/datetime - Current date and time\n"
            "/day - Current day\n"
            "/days-between YYYY-MM-DD YYYY-MM-DD\n"
            "/add-days YYYY-MM-DD number\n"
            "/subtract-days YYYY-MM-DD number\n"
            "/leap-year year\n\n"
            "Unit Conversion Commands\n\n"
            "/convert 25 km to m\n"
            "/convert 100 Celsius to Fahrenheit\n"
            "/units - Supported units\n\n"
            "Natural language examples:\n"
            "What is today's date?\n"
            "What time is it?\n"
            "Convert 5 kg to grams\n"
            "Convert 25 km into metres\n"
            "Add 30 days to 2026-11-26\n"
            "Days between 2026-01-01 and 2026-12-31"
        )

    def format_date_difference(self, start, end):

        result = self.datetime_tool.date_difference(
            start,
            end,
        )

        return (
            "Date Difference\n\n"
            f"Start Date: {result['start_date']}\n"
            f"End Date: {result['end_date']}\n"
            f"Total Days: {result['days']}\n"
            f"Duration: {result['weeks']} weeks "
            f"and {result['remaining_days']} days\n\n"
            "Calculated as elapsed days."
        )

    def format_date_adjustment(self, start, days):

        result = self.datetime_tool.add_days(
            start,
            days,
        )

        return (
            "Date Calculation\n\n"
            f"Original Date: {result['original_date']}\n"
            f"Days Adjustment: {result['days']}\n"
            f"Result Date: {result['result_date']}\n"
            f"Day: {result['day']}\n"
            f"Formatted Date: {result['formatted_date']}"
        )

    def format_conversion(self, value, source, target):

        result = self.unit_converter.convert(
            value,
            source,
            target,
        )

        formatted = self.unit_converter.format_number(
            result
        )

        return (
            "Unit Conversion\n\n"
            f"Input: {value} {source}\n"
            f"Result: {formatted} {target}\n\n"
            "Calculated locally by KlubAI."
        )

    def route(self, message):

        message = message.strip()

        text = message.lower().rstrip("?!.").strip()

        text = text.replace("’", "'")

        text = re.sub(r"\s+", " ", text)

        # Current date
        if text in (
            "/date",
            "today's date",
            "what is today's date",
            "what is the date today",
            "what is the current date",
            "current date",
            "tell me today's date",
        ):

            return (
                "Today's date is "
                + self.datetime_tool.current_date()
                + "."
            )

        # Current time
        if text in (
            "/time",
            "what time is it",
            "current time",
            "what is the current time",
            "what is the time",
            "tell me the time",
        ):

            return (
                "Current time: "
                + self.datetime_tool.current_time()
            )

        # Current day
        if text in (
            "/day",
            "what day is today",
            "what day is it",
            "current day",
        ):

            return (
                "Today is "
                + self.datetime_tool.current_day()
                + "."
            )

        # Date and time
        if text in (
            "/datetime",
            "current date and time",
            "what is the current date and time",
            "show date and time",
        ):

            return self.datetime_tool.current_datetime()

        # Supported units
        if text in (
            "/units",
            "show supported units",
            "show unit conversions",
        ):

            return self.unit_converter.get_supported_units()

        # Explicit date commands
        if text.startswith("/days-between "):

            parts = text.split()

            if len(parts) != 3:

                raise ValueError(
                    "Usage: /days-between "
                    "YYYY-MM-DD YYYY-MM-DD"
                )

            return self.format_date_difference(
                parts[1],
                parts[2],
            )

        if text.startswith(
            ("/add-days ", "/subtract-days ")
        ):

            parts = text.split()

            if len(parts) != 3:

                raise ValueError(
                    "Usage: /add-days YYYY-MM-DD number"
                )

            days = int(parts[2])

            if parts[0] == "/subtract-days":

                days = -days

            return self.format_date_adjustment(
                parts[1],
                days,
            )

        # Leap year
        leap_match = re.fullmatch(
            r"(?:/leap-year\s+|is\s+)"
            r"(\d{1,4})(?:\s+a leap year)?",
            text,
        )

        if leap_match:

            year = int(leap_match.group(1))

            result = self.datetime_tool.is_leap_year(
                year
            )

            if result:

                return f"{year} is a leap year."

            return f"{year} is not a leap year."

        # Natural language date difference
        date_pattern = self.DATE_PATTERN

        difference_match = re.fullmatch(
            rf"(?:(?:calculate|how many)\s+)?"
            rf"days between\s+"
            rf"({date_pattern})\s+"
            rf"(?:and|to)\s+"
            rf"({date_pattern})",
            text,
        )

        if difference_match:

            return self.format_date_difference(
                difference_match.group(1),
                difference_match.group(2),
            )

        # Natural language date adjustment
        adjustment_match = re.fullmatch(
            rf"(add|subtract)\s+"
            rf"(\d+)\s+days?\s+"
            rf"(?:to|from)\s+"
            rf"({date_pattern})",
            text,
        )

        if adjustment_match:

            operation = adjustment_match.group(1)

            days = int(adjustment_match.group(2))

            start = adjustment_match.group(3)

            if operation == "subtract":

                days = -days

            return self.format_date_adjustment(
                start,
                days,
            )

        # Natural language and explicit unit conversion
        conversion_match = re.fullmatch(
            r"(?:/convert|convert)\s+"
            r"(-?\d[\d,]*(?:\.\d+)?)\s+"
            r"(.+?)\s+"
            r"(?:to|into|in)\s+"
            r"(.+)",
            text,
        )

        if conversion_match:

            value = conversion_match.group(1)

            value = value.replace(",", "")

            source = conversion_match.group(2)
            target = conversion_match.group(3)

            return self.format_conversion(
                value,
                source,
                target,
            )

        if text.split(" ", 1)[0] in {
            "/convert",
            "/days-between",
            "/add-days",
            "/subtract-days",
            "/leap-year",
        }:

            raise ValueError(
                "Invalid task command. "
                "Type /task-help for examples."
            )

        # Existing calculator, GST and discount functionality
        return super().route(message)
