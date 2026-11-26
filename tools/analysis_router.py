
import re

from tools.data_analyzer import DataAnalyzer


class AnalysisRouter:

    COMMANDS = {
        "/sum",
        "/average",
        "/max",
        "/min",
        "/count",
        "/columns",
        "/analyze",
        "/group",
        "/analysis-help",
    }

    def __init__(self, input_directory=None):

        self.analyzer = DataAnalyzer(
            input_directory
        )

    def get_help(self):

        return (
            "KlubAI Data Analysis Commands\n\n"
            "/sum sample.xlsx Amount\n"
            "/average sample.xlsx Amount\n"
            "/max sample.xlsx Amount\n"
            "/min sample.xlsx Amount\n"
            "/count sample.xlsx\n"
            "/columns sample.xlsx\n"
            "/analyze sample.xlsx\n"
            "/group sample.xlsx Category Amount\n\n"
            "For column names containing spaces:\n"
            '/sum sample.xlsx "Total Amount"\n'
            '/group sample.xlsx "Product Name" "Total Amount"\n\n'
            "Document Intelligence:\n"
            "/summarize sample.pdf\n"
            "/ask-file sample.pdf | What is the main topic?\n\n"
            "Place documents inside the inputs directory."
        )

    @staticmethod
    def parse_arguments(text):

        import shlex

        return shlex.split(text)

    def route(self, message):

        message = message.strip()

        if not message:

            return None

        command = message.split(maxsplit=1)[0].lower()

        if command not in self.COMMANDS:

            return None

        if command == "/analysis-help":

            return self.get_help()

        arguments = self.parse_arguments(message)[1:]

        analyzer = self.analyzer

        if command in {
            "/sum",
            "/average",
            "/max",
            "/min",
        }:

            if len(arguments) != 2:

                raise ValueError(
                    f"Usage: {command} filename column"
                )

            filename, column = arguments

            result = analyzer.calculate(
                filename,
                column,
                command[1:],
            )

            value = analyzer.format_number(
                result["result"]
            )

            return (
                "Data Calculation\n\n"
                f"File: {filename}\n"
                f"Column: {result['column']}\n"
                f"Operation: {result['operation']}\n"
                f"Result: {value}\n"
                f"Numeric Records: {result['numeric_records']}\n"
                f"Skipped Records: {result['skipped_records']}\n\n"
                "Calculated locally by KlubAI."
            )

        if command in {
            "/count",
            "/columns",
            "/analyze",
        }:

            if len(arguments) != 1:

                raise ValueError(
                    f"Usage: {command} filename"
                )

            filename = arguments[0]

            if command == "/count":

                return (
                    f"File: {filename}\n"
                    f"Total Records: {analyzer.count(filename)}"
                )

            if command == "/columns":

                columns = analyzer.columns(filename)

                return (
                    "Available Columns\n\n"
                    + "\n".join(
                        f"{index}. {column}"
                        for index, column in enumerate(
                            columns,
                            start=1,
                        )
                    )
                )

            result = analyzer.analyze(filename)

            lines = [
                "Dataset Analysis",
                "",
                f"File: {filename}",
                f"Total Records: {result['records']}",
                f"Columns: {', '.join(result['columns'])}",
            ]

            for column, stats in result["statistics"].items():

                lines.extend([
                    "",
                    f"Column: {column}",
                    f"Numeric Records: {stats['count']}",
                    f"Skipped Records: {stats['skipped']}",
                ])

                for key in (
                    "total",
                    "average",
                    "minimum",
                    "maximum",
                ):

                    value = analyzer.format_number(
                        stats[key]
                    )

                    lines.append(
                        f"{key.title()}: {value}"
                    )

            if not result["statistics"]:

                lines.append(
                    "\nNo numeric columns found."
                )

            return "\n".join(lines)

        if command == "/group":

            if len(arguments) != 3:

                raise ValueError(
                    "Usage: /group filename "
                    "group_column value_column"
                )

            result = analyzer.group_sum(*arguments)

            lines = [
                "Grouped Data Analysis",
                "",
                f"File: {result['filename']}",
                f"Group Column: {result['group_column']}",
                f"Value Column: {result['value_column']}",
                "",
            ]

            for group, value in sorted(
                result["groups"].items()
            ):

                formatted = analyzer.format_number(value)

                lines.append(
                    f"{group}: {formatted}"
                )

            lines.append(
                f"\nSkipped Records: "
                f"{result['skipped_records']}"
            )

            return "\n".join(lines)

        return None
