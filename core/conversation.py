
from config import (
    SYSTEM_PROMPT,
    MAX_HISTORY_MESSAGES,
)

from memory.database import Database
from memory.memory_manager import MemoryManager


class ConversationManager:

    def __init__(self):

        self.database = Database()

        self.memory = MemoryManager(
            self.database
        )

        self.session_id = (
            self.database.get_latest_session()
        )

        if self.session_id is None:

            self.session_id = (
                self.database.create_session()
            )

        self.history = self.database.get_messages(
            self.session_id,
            MAX_HISTORY_MESSAGES,
        )

    def add_user_message(self, message):

        self.history.append({
            "role": "user",
            "content": message,
        })

    def add_assistant_message(self, message):

        if (
            not self.history
            or self.history[-1]["role"] != "user"
        ):
            raise RuntimeError(
                "No pending user message."
            )

        user_message = self.history[-1]["content"]

        self.database.save_turn(
            self.session_id,
            user_message,
            message,
        )

        self.history.append({
            "role": "assistant",
            "content": message,
        })

        self.history = self.history[
            -MAX_HISTORY_MESSAGES:
        ]

    def get_messages(self):

        system_prompt = SYSTEM_PROMPT

        memory_context = (
            self.memory.build_memory_context()
        )

        if memory_context:

            system_prompt += (
                "\n\n" + memory_context
            )

        return [
            {
                "role": "system",
                "content": system_prompt,
            },
            *self.history,
        ]

    def remove_last_message(self):

        if (
            self.history
            and self.history[-1]["role"] == "user"
        ):
            self.history.pop()

    def get_history(self):

        return self.database.get_messages(
            self.session_id,
            limit=100,
        )

    def clear(self):

        self.session_id = (
            self.database.create_session()
        )

        self.history = []

    def message_count(self):

        return len(self.history)

    def clear_all_data(self):

        self.database.clear_all_data()

        self.clear()
