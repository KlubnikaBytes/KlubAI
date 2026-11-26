
from core.assistant import KlubAI

from tools.file_generator import FileGenerator
from tools.file_request_handler import (
    FileRequestHandler,
)


class FileEnabledKlubAI(KlubAI):

    def __init__(self):

        super().__init__()

        self.file_generator = FileGenerator()

        self.file_handler = FileRequestHandler()

    def get_file_help(self):

        return (
            "KlubAI File Generation Commands\n\n"
            "/create pdf Your topic\n"
            "/create docx Your topic\n"
            "/create xlsx Your topic\n"
            "/create csv Your topic\n"
            "/create txt Your topic\n"
            "/create pptx Your topic\n"
            "/files - Show generated files\n"
            "/file-help - Show file commands\n\n"
            "Natural language examples:\n"
            "Create a PDF report about Python.\n"
            "Create a Word document about Laravel.\n"
            "Create an Excel sheet for monthly expenses.\n"
            "Create a PowerPoint about AI."
        )

    def list_generated_files(self):

        directory = self.file_generator.output_dir

        files = [
            path for path in directory.iterdir()
            if path.is_file()
            and path.suffix.lower().lstrip(".")
            in self.file_generator.SUPPORTED_FORMATS
        ]

        files.sort(
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )

        if not files:

            return "No generated files found."

        lines = [
            "Generated files:",
            f"Directory: {directory}",
            "",
        ]

        for index, path in enumerate(
            files[:30],
            start=1,
        ):

            size_kb = path.stat().st_size / 1024

            lines.append(
                f"{index}. {path.name} "
                f"({size_kb:.2f} KB)"
            )

        return "\n".join(lines)

    def chat_stream(self, user_message):

        user_message = user_message.strip()

        command = user_message.lower()

        if command in (
            "/file-help",
            "show file commands",
        ):

            yield self.get_file_help()
            return

        if command == "/files":

            yield self.list_generated_files()
            return

        if command == "/create":

            yield self.get_file_help()
            return

        try:

            request = self.file_handler.detect(
                user_message
            )

        except ValueError as error:

            yield str(error)
            return

        if request is None:

            yield from super().chat_stream(
                user_message
            )

            return

        self.conversation.add_user_message(
            user_message
        )

        completed = False

        try:

            yield (
                f"Preparing "
                f"{request.file_format.upper()} "
                f"document...\n"
            )

            messages = (
                self.file_handler.build_prompt(
                    request
                )
            )

            yield (
                "Generating content using "
                "the local AI model...\n"
            )

            content = self.engine.generate_response(
                messages
            )

            if not content:

                raise RuntimeError(
                    "AI returned empty document content."
                )

            yield "Creating file locally...\n"

            path = self.file_generator.generate(
                file_format=request.file_format,
                title=request.topic,
                content=content,
            )

            size_kb = path.stat().st_size / 1024

            response = (
                "File generated successfully!\n\n"
                f"Format: {request.file_format.upper()}\n"
                f"Topic: {request.topic}\n"
                f"Filename: {path.name}\n"
                f"File size: {size_kb:.2f} KB\n"
                f"Location: {path}\n\n"
                "Please review AI-generated content "
                "before using it professionally."
            )

            self.conversation.add_assistant_message(
                response
            )

            completed = True

            yield "\n" + response

        finally:

            if not completed:

                self.conversation.remove_last_message()
