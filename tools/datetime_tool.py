
from datetime import datetime, date, timedelta


class DateTimeTool:

    DATE_FORMAT = "%Y-%m-%d"

    @staticmethod
    def now():

        return datetime.now().astimezone()

    def current_date(self):

        now = self.now()

        return now.strftime(
            "%d %B %Y"
        )

    def current_time(self):

        now = self.now()

        return now.strftime(
            "%I:%M:%S %p %Z"
        )

    def current_day(self):

        return self.now().strftime("%A")

    def current_datetime(self):

        now = self.now()

        return (
            "Current Date and Time\n\n"
            f"Date: {now.strftime('%d %B %Y')}\n"
            f"Day: {now.strftime('%A')}\n"
            f"Time: {now.strftime('%I:%M:%S %p')}\n"
            f"Timezone: {now.strftime('%Z')}\n"
            f"UTC Offset: {now.strftime('%z')}\n\n"
            "Retrieved from the local system clock."
        )

    def parse_date(self, value):

        value = value.strip()

        try:

            parsed = date.fromisoformat(value)

            if parsed.isoformat() != value:

                raise ValueError()

            return parsed

        except ValueError as error:

            raise ValueError(
                "Invalid date. Use YYYY-MM-DD format."
            ) from error

    def date_difference(self, start_date, end_date):

        start = self.parse_date(start_date)
        end = self.parse_date(end_date)

        difference = (end - start).days

        return {
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "days": abs(difference),
            "signed_days": difference,
            "weeks": abs(difference) // 7,
            "remaining_days": abs(difference) % 7,
        }

    def add_days(self, start_date, days):

        start = self.parse_date(start_date)

        days = int(days)

        if abs(days) > 365000:

            raise ValueError(
                "Maximum date adjustment is 365000 days."
            )

        try:

            result = start + timedelta(days=days)

        except OverflowError as error:

            raise ValueError(
                "Resulting date is outside supported range."
            ) from error

        return {
            "original_date": start.isoformat(),
            "days": days,
            "result_date": result.isoformat(),
            "formatted_date": result.strftime(
                "%d %B %Y"
            ),
            "day": result.strftime("%A"),
        }

    def subtract_days(self, start_date, days):

        return self.add_days(
            start_date,
            -int(days),
        )

    def is_leap_year(self, year):

        year = int(year)

        if year < 1 or year > 9999:

            raise ValueError("Invalid year.")

        return (
            year % 400 == 0
            or (
                year % 4 == 0
                and year % 100 != 0
            )
        )
