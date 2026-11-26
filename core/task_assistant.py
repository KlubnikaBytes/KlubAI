
from decimal import DecimalException

from core.file_assistant import FileEnabledKlubAI
from tools.task_router import TaskRouter


class TaskEnabledKlubAI(FileEnabledKlubAI):

    def __init__(self):

        super().__init__()

        self.task_router = TaskRouter()

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
        ) as error:

            yield f"Calculation error: {error}"
            return

        if response is None:

            yield from super().chat_stream(
                user_message
            )

            return

        if user_message.lower() in (
            "/task-help",
            "show task commands",
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
