from decimal import DecimalException

from core.file_assistant import FileEnabledKlubAI
from tools.file_read_router import FileReadRouter


class TaskEnabledKlubAI(FileEnabledKlubAI):

    def __init__(self):

        super().__init__()

        self.task_router = FileReadRouter()

    def chat_stream(self, user_message):

        user_message = user_message.strip()

        try:

            response = self.task_router.route(
                user_message
            )

        except (
            ValueError,
            ArithmeticError,
            DecimalException,
            OSError,
        ) as error:

            yield f"Task error: {error}"

            return

        except Exception as error:

            yield (
                "Task execution failed: "
                f"{type(error).__name__}: {error}"
            )

            return

        if response is None:

            yield from super().chat_stream(
                user_message
            )

            return

        command = " ".join(user_message.lower().split())

        # Do not automatically store extracted documents
        # in conversation history or AI memory.
        if (
            command.startswith((
                "/read ",
                "/file-info ",
                "read ",
            ))
            or command in {
                "/task-help",
                "show task commands",
                "/units",
                "show supported units",
                "show unit conversions",
                "/read-help",
                "/input-files",
                "show input files",
                "list input files",
                "show file reading commands",
            }
        ):

            yield response

            return

        self.conversation.add_user_message(
            user_message
        )

        completed = False

        try:

            self.conversation.add_assistant_message(
                response
            )

            completed = True

            yield response

        finally:

            if not completed:

                self.conversation.remove_last_message()
