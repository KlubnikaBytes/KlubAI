
import re

from tools.extended_task_router import ExtendedTaskRouter
from tools.file_reader import FileReader


class FileReadRouter(ExtendedTaskRouter):

    def __init__(self):

        super().__init__()

        self.file_reader = FileReader()

    def get_file_read_help(self):

        return (
            "KlubAI Local File Reading Commands\n\n"
            "/read filename.pdf\n"
            "/file-info filename.pdf\n"
            "/input-files\n"
            "/read-help\n\n"
            "Natural language examples:\n"
            "Read report.pdf\n"
            "Read employees.xlsx\n"
            "Read project.docx\n"
            "Read file expenses.csv\n\n"
            "Supported formats:\n"
            "PDF, DOCX, XLSX, CSV, TXT, MD, JSON, PPTX\n\n"
            "Place documents inside the inputs directory."
        )

    def get_help(self):

        return (
            super().get_help()
            + "\n\n"
            + self.get_file_read_help()
        )

    def format_file_content(self, filename):

        result = self.file_reader.read(filename)

        lines = [
            "Local File Reading Result",
            "",
            f"Filename: {result['filename']}",
            f"Format: {result['format']}",
            f"File Size: {result['size'] / 1024:.2f} KB",
        ]

        for key, value in result["metadata"].items():

            if key == "limited":
                continue

            label = key.replace("_", " ").title()

            lines.append(f"{label}: {value}")

        lines.extend([
            "",
            "Extracted Content",
            "=" * 45,
            result["content"] or "No readable text found.",
            "=" * 45,
        ])

        if result["truncated"]:

            lines.append(
                "Note: Content was limited by "
                "document processing limits."
            )

        lines.append(
            "\nRead locally by KlubAI."
        )

        return "\n".join(lines)

    def format_file_info(self, filename):

        result = self.file_reader.file_info(filename)

        return (
            "File Information\n\n"
            f"Filename: {result['filename']}\n"
            f"Format: {result['format']}\n"
            f"Size: {result['size'] / 1024:.2f} KB\n"
            f"Location: {result['location']}"
        )

    def format_file_list(self):

        files = self.file_reader.list_files()

        if not files:
            return (
                "No supported documents found.\n"
                "Place files inside the inputs directory."
            )

        lines = [
            "Available Input Files",
            "",
        ]

        for index, item in enumerate(files, start=1):

            lines.append(
                f"{index}. {item['name']} "
                f"({item['size'] / 1024:.2f} KB)"
            )

        return "\n".join(lines)

    def route(self, message):

        message = message.strip()

        command = message.lower()

        if command in {
            "/read-help",
            "show file reading commands",
        }:
            return self.get_file_read_help()

        if command in {
            "/input-files",
            "show input files",
            "list input files",
        }:
            return self.format_file_list()

        if command == "/read":
            return "Usage: /read filename.pdf"

        if command == "/file-info":
            return "Usage: /file-info filename.pdf"

        if command.startswith("/read "):

            filename = message.split(maxsplit=1)[1]

            return self.format_file_content(filename)

        if command.startswith("/file-info "):

            filename = message.split(maxsplit=1)[1]

            return self.format_file_info(filename)

        match = re.fullmatch(
            r"read\s+(?:file\s+)?"
            r"(.+\.(?:pdf|docx|xlsx|csv|txt|md|json|pptx))"
            r"[\"']?[?!.]?",
            message,
            flags=re.IGNORECASE,
        )

        if match:

            filename = match.group(1)

            return self.format_file_content(filename)

        return super().route(message)
