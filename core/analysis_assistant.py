
import re

from core.task_assistant import TaskEnabledKlubAI

from tools.analysis_router import AnalysisRouter
from tools.document_intelligence import DocumentIntelligence


class AnalysisEnabledKlubAI(TaskEnabledKlubAI):

    def __init__(self):

        super().__init__()

        self.analysis_router = AnalysisRouter()

        self.document_intelligence = DocumentIntelligence(
            self.engine
        )

    def chat_stream(self, user_message):

        user_message = user_message.strip()

        if not user_message:

            yield from super().chat_stream(user_message)
            return

        command = user_message.split(
            maxsplit=1
        )[0].lower()

        try:

            response = self.analysis_router.route(
                user_message
            )

            if response is not None:

                yield response
                return

            if command == "/summarize":

                parts = user_message.split(maxsplit=1)

                if len(parts) != 2:

                    yield "Usage: /summarize filename.pdf"
                    return

                filename = parts[1].strip().strip('"')

                yield from self.document_intelligence.summarize(
                    filename
                )

                return

            if command == "/ask-file":

                parts = user_message.split(maxsplit=1)

                if len(parts) != 2 or "|" not in parts[1]:

                    yield (
                        "Usage: /ask-file filename.pdf "
                        "| Your question"
                    )

                    return

                filename, question = parts[1].split(
                    "|",
                    1,
                )

                filename = filename.strip().strip('"')
                question = question.strip()

                yield from self.document_intelligence.ask(
                    filename,
                    question,
                )

                return

            summary_match = re.fullmatch(
                r"summarize\s+(.+\."
                r"(?:pdf|docx|txt|md|pptx|csv|xlsx|json))",
                user_message,
                flags=re.IGNORECASE,
            )

            if summary_match:

                yield from self.document_intelligence.summarize(
                    summary_match.group(1)
                )

                return

        except Exception as error:

            yield (
                f"Analysis error: "
                f"{type(error).__name__}: {error}"
            )

            return

        yield from super().chat_stream(
            user_message
        )
