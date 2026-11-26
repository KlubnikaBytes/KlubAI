
from core.model_engine import ModelEngine
from core.conversation import ConversationManager


class KlubAI:

    def __init__(self):

        self.engine = ModelEngine()

        self.conversation = (
            ConversationManager()
        )

        self.memory = self.conversation.memory

    def initialize(self):

        self.engine.load_model()

    def handle_memory_command(self, message):

        command = message.lower().strip()

        if command == "/memory-help":

            return (
                "Memory commands:\n"
                "/memory - Show stored facts\n"
                "/remember key=value - Save a fact\n"
                "/recall key - Retrieve a fact\n"
                "/forget key - Remove a fact\n"
                "/forget-all confirm - Clear saved facts\n"
                "/delete-data confirm - Clear all data"
            )

        if command == "/memory":

            memories = self.memory.get_all()

            if not memories:
                return "No saved memories."

            lines = ["Saved user information:"]

            for key, value in memories.items():

                label = key.replace("_", " ").title()

                lines.append(
                    f"{label}: {value}"
                )

            return "\n".join(lines)

        if command.startswith("/remember "):

            content = message[
                len("/remember "):
            ].strip()

            if "=" not in content:

                return "Usage: /remember key=value"

            key, value = content.split("=", 1)

            self.memory.remember(key, value)

            return "Information saved successfully."

        if command.startswith("/recall "):

            key = message[
                len("/recall "):
            ].strip()

            value = self.memory.recall(key)

            if value is None:

                return "No saved information found."

            return value

        if command.startswith("/forget "):

            key = message[
                len("/forget "):
            ].strip()

            if self.memory.forget(key):

                return (
                    "Saved memory removed. "
                    "It may still appear in old "
                    "conversation history."
                )

            return "Memory not found."

        if command == "/forget-all":

            return (
                "Use /forget-all confirm "
                "to remove all saved facts."
            )

        if command == "/forget-all confirm":

            self.memory.database.clear_memory()

            return (
                "All saved facts removed. "
                "Conversation history is retained."
            )

        if command == "/delete-data":

            return (
                "Use /delete-data confirm "
                "to delete all conversations and facts."
            )

        if command == "/delete-data confirm":

            self.conversation.clear_all_data()

            return (
                "Saved conversations and facts "
                "have been cleared from the database."
            )

        return None

    def handle_user_fact(self, message):

        fact = self.memory.extract_fact(message)

        if fact is None:

            return None

        key, value = fact

        self.memory.remember(key, value)

        label = key.replace("_", " ")

        return (
            f"I will remember that your "
            f"{label} is {value}."
        )

    def handle_memory_question(self, message):

        key = self.memory.detect_memory_question(
            message
        )

        if key is None:

            return None

        value = self.memory.recall(key)

        label = key.replace("_", " ")

        if value is None:

            return (
                f"You have not saved your "
                f"{label} yet."
            )

        return f"Your {label} is {value}."

    def handle_direct_question(self, message):

        normalized = (
            message.lower()
            .strip()
            .rstrip(".!?")
        )

        responses = {
            "hello": (
                "Hello! How can I help you today?"
            ),
            "hi": (
                "Hi! How can I help you?"
            ),
            "how are you": (
                "I'm doing well and ready to help!"
            ),
            "who are you": (
                "I am KlubAI, an AI assistant "
                "application developed by Klubnika Bytes "
                "using a Qwen3 foundation model."
            ),
            "who developed you": (
                "KlubAI was developed by Klubnika Bytes."
            ),
            "show memory commands": (
                self.handle_memory_command(
                    "/memory-help"
                )
            ),
        }

        return responses.get(normalized)

    def chat_stream(self, user_message):

        user_message = user_message.strip()

        if not user_message:

            yield "Please enter a question."
            return

        response = self.handle_memory_command(
            user_message
        )

        if response is not None:

            yield response
            return

        self.conversation.add_user_message(
            user_message
        )

        completed = False

        try:

            response = self.handle_user_fact(
                user_message
            )

            if response is None:

                response = self.handle_memory_question(
                    user_message
                )

            if response is None:

                response = self.handle_direct_question(
                    user_message
                )

            # Deterministic response
            if response is not None:

                self.conversation.add_assistant_message(
                    response
                )

                completed = True

                yield response

                return

            # AI-generated streaming response
            messages = self.conversation.get_messages()

            response_parts = []

            stream = self.engine.stream_response(
                messages
            )

            try:

                for text in stream:

                    response_parts.append(text)

                    yield text

            finally:

                stream.close()

            full_response = "".join(
                response_parts
            ).strip()

            if not full_response:

                raise RuntimeError(
                    "The model returned an empty response."
                )

            self.conversation.add_assistant_message(
                full_response
            )

            completed = True

        finally:

            if not completed:

                self.conversation.remove_last_message()

    def chat(self, user_message):

        return "".join(
            self.chat_stream(user_message)
        ).strip()

    def clear_conversation(self):

        self.conversation.clear()

    def get_history(self):

        return self.conversation.get_history()

    def shutdown(self):

        self.engine.close()
