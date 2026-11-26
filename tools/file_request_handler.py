
import re

from dataclasses import dataclass


@dataclass(frozen=True)
class FileRequest:

    file_format: str
    topic: str


class FileRequestHandler:

    FORMAT_ALIASES = {
        "pdf": "pdf",
        "word": "docx",
        "docx": "docx",
        "excel": "xlsx",
        "xlsx": "xlsx",
        "csv": "csv",
        "text": "txt",
        "txt": "txt",
        "powerpoint": "pptx",
        "presentation": "pptx",
        "ppt": "pptx",
        "pptx": "pptx",
    }

    @classmethod
    def detect(cls, message):

        message = message.strip()

        if message.lower().startswith("/create "):

            parts = message.split(
                maxsplit=2
            )

            if len(parts) < 3:

                raise ValueError(
                    "Usage: /create pdf Your topic"
                )

            file_format = cls.FORMAT_ALIASES.get(
                parts[1].lower().lstrip(".")
            )

            if file_format is None:

                raise ValueError(
                    "Supported formats: pdf, docx, "
                    "xlsx, csv, txt, pptx"
                )

            topic = parts[2].strip()

            return cls.validate(
                file_format,
                topic,
            )

        pattern = (
            r"^(?:please\s+)?"
            r"(?:create|generate|make|prepare|write)"
            r"\s+(?:me\s+)?"
            r"(?:a\s+|an\s+)?"
            r"(pdf|word|docx|excel|xlsx|csv|"
            r"text|txt|powerpoint|presentation|"
            r"pptx|ppt)\b"
            r"\s*(.*)$"
        )

        match = re.match(
            pattern,
            message,
            flags=re.IGNORECASE,
        )

        if not match:
            return None

        file_format = cls.FORMAT_ALIASES[
            match.group(1).lower()
        ]

        topic = match.group(2).strip()

        topic = re.sub(
            r"^(?:file|document|report|sheet|"
            r"spreadsheet|presentation)\b\s*",
            "",
            topic,
            flags=re.IGNORECASE,
        )

        topic = re.sub(
            r"^(?:about|on|for|containing|with)"
            r"\s+",
            "",
            topic,
            flags=re.IGNORECASE,
        )

        return cls.validate(
            file_format,
            topic,
        )

    @staticmethod
    def validate(file_format, topic):

        topic = topic.strip()

        if not topic:

            raise ValueError(
                "Please provide a document topic."
            )

        if len(topic) > 1000:

            raise ValueError(
                "Document topic is too long."
            )

        return FileRequest(
            file_format=file_format,
            topic=topic,
        )

    @staticmethod
    def build_prompt(request):

        if request.file_format in (
            "xlsx",
            "csv",
        ):

            return [
                {
                    "role": "system",
                    "content": (
                        "Generate valid CSV table data. "
                        "Return only CSV content. "
                        "The first row must contain "
                        "column headings. "
                        "Every row must contain the same "
                        "number of columns. "
                        "Use standard CSV quoting. "
                        "Do not use Markdown tables. "
                        "Do not add explanations. "
                        "Use no more than 10 data rows. "
                        "If actual data is unavailable, "
                        "clearly label generated data "
                        "as sample data."
                    ),
                },
                {
                    "role": "user",
                    "content": request.topic,
                },
            ]

        if request.file_format == "pptx":

            return [
                {
                    "role": "system",
                    "content": (
                        "Generate concise presentation "
                        "content in English. "
                        "Create 4 to 6 sections. "
                        "Start every section with "
                        "a Markdown heading using ##. "
                        "Include 3 to 4 short bullet "
                        "points per section. "
                        "Do not add introductory chat "
                        "or closing conversation. "
                        "Do not invent facts."
                    ),
                },
                {
                    "role": "user",
                    "content": request.topic,
                },
            ]

        return [
            {
                "role": "system",
                "content": (
                    "Generate a professional document "
                    "in English. "
                    "Use Markdown headings starting "
                    "with ## and short paragraphs. "
                    "Include an introduction, relevant "
                    "sections and a conclusion. "
                    "Do not repeat the document title. "
                    "Do not introduce yourself. "
                    "Do not add conversational messages. "
                    "Do not invent facts or statistics. "
                    "If uncertain, acknowledge uncertainty. "
                    "Keep the document under 400 words."
                ),
            },
            {
                "role": "user",
                "content": request.topic,
            },
        ]
