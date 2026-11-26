
import csv

from decimal import Decimal, InvalidOperation, localcontext
from pathlib import Path

from openpyxl import load_workbook

from tools.file_reader import FileReader


class DataAnalyzer:

    MAX_ROWS = 10000
    MAX_COLUMNS = 100

    def __init__(self, input_directory=None):

        self.reader = FileReader(input_directory)

    def load_table(self, filename):

        path = self.reader.validator.validate(filename)

        extension = path.suffix.lower()

        if extension == ".csv":

            with path.open(
                "r",
                encoding="utf-8-sig",
                newline="",
            ) as file:

                rows = self.prepare_rows(
                    csv.reader(file)
                )

        elif extension == ".xlsx":

            self.reader.check_office_archive(path)

            workbook = load_workbook(
                str(path),
                read_only=True,
                data_only=True,
                keep_links=False,
            )

            try:

                sheet = workbook.worksheets[0]

                rows = self.prepare_rows(
                    sheet.iter_rows(values_only=True)
                )

            finally:

                workbook.close()

        else:

            raise ValueError(
                "Data analysis supports CSV and XLSX files."
            )

        if not rows:

            raise ValueError("The file contains no data.")

        headers = [
            str(value).strip() if value is not None else ""
            for value in rows[0]
        ]

        if not headers or any(not value for value in headers):

            raise ValueError(
                "Every data column must have a header."
            )

        normalized = [
            header.casefold()
            for header in headers
        ]

        if len(normalized) != len(set(normalized)):

            raise ValueError(
                "Duplicate column names are not supported."
            )

        records = []

        for row in rows[1:]:

            if len(row) > len(headers):

                raise ValueError(
                    "A record contains more values than headers."
                )

            row = row + [None] * (
                len(headers) - len(row)
            )

            records.append(
                dict(zip(headers, row))
            )

        return headers, records

    def prepare_rows(self, source):

        rows = []

        for index, raw_row in enumerate(source):

            if index >= self.MAX_ROWS + 1:

                raise ValueError(
                    "Dataset exceeds the 10,000 record limit."
                )

            row = list(raw_row)

            while row and (
                row[-1] is None
                or str(row[-1]).strip() == ""
            ):

                row.pop()

            if len(row) > self.MAX_COLUMNS:

                raise ValueError(
                    "Dataset exceeds the column limit."
                )

            if not row:

                continue

            rows.append(row)

        return rows

    @staticmethod
    def resolve_column(headers, column):

        requested = column.strip().casefold()

        for header in headers:

            if header.casefold() == requested:

                return header

        raise ValueError(
            f"Column not found: {column}. "
            f"Available columns: {', '.join(headers)}"
        )

    @staticmethod
    def parse_number(value):

        if value is None or isinstance(value, bool):

            return None

        text = str(value).strip()

        if not text:

            return None

        try:

            number = Decimal(text)

            if not number.is_finite():

                return None

            if abs(number) > Decimal("1e30"):

                return None

            if number != 0 and abs(number) < Decimal("1e-20"):

                return None

            return number

        except (InvalidOperation, ValueError):

            return None

    @staticmethod
    def format_number(value):

        if value == 0:

            return "0"

        result = format(value, "f")

        if "." in result:

            result = result.rstrip("0").rstrip(".")

        return result

    def numeric_values(self, records, column):

        values = []
        skipped = 0

        for record in records:

            number = self.parse_number(
                record.get(column)
            )

            if number is None:

                skipped += 1

            else:

                values.append(number)

        return values, skipped

    def calculate(self, filename, column, operation):

        headers, records = self.load_table(filename)

        column = self.resolve_column(headers, column)

        values, skipped = self.numeric_values(
            records,
            column,
        )

        if not values:

            raise ValueError(
                f"No numeric values found in {column}."
            )

        with localcontext() as context:

            context.prec = 50

            if operation == "sum":

                result = sum(values, Decimal("0"))

            elif operation == "average":

                result = sum(values, Decimal("0")) / len(values)

            elif operation == "max":

                result = max(values)

            elif operation == "min":

                result = min(values)

            else:

                raise ValueError(
                    "Unsupported calculation."
                )

        return {
            "filename": filename,
            "column": column,
            "operation": operation,
            "result": result,
            "numeric_records": len(values),
            "skipped_records": skipped,
        }

    def count(self, filename):

        headers, records = self.load_table(filename)

        return len(records)

    def columns(self, filename):

        headers, records = self.load_table(filename)

        return headers

    def analyze(self, filename):

        headers, records = self.load_table(filename)

        statistics = {}

        with localcontext() as context:

            context.prec = 50

            for column in headers:

                values, skipped = self.numeric_values(
                    records,
                    column,
                )

                if not values:

                    continue

                total = sum(values, Decimal("0"))

                statistics[column] = {
                    "count": len(values),
                    "skipped": skipped,
                    "total": total,
                    "average": total / len(values),
                    "minimum": min(values),
                    "maximum": max(values),
                }

        return {
            "filename": filename,
            "records": len(records),
            "columns": headers,
            "statistics": statistics,
        }

    def group_sum(
        self,
        filename,
        group_column,
        value_column,
    ):

        headers, records = self.load_table(filename)

        group_column = self.resolve_column(
            headers,
            group_column,
        )

        value_column = self.resolve_column(
            headers,
            value_column,
        )

        groups = {}
        skipped = 0

        with localcontext() as context:

            context.prec = 50

            for record in records:

                number = self.parse_number(
                    record.get(value_column)
                )

                if number is None:

                    skipped += 1
                    continue

                group = record.get(group_column)

                if group is None or not str(group).strip():

                    group = "(Empty)"

                else:

                    group = str(group).strip()

                groups[group] = (
                    groups.get(group, Decimal("0"))
                    + number
                )

        return {
            "filename": filename,
            "group_column": group_column,
            "value_column": value_column,
            "groups": groups,
            "skipped_records": skipped,
        }
