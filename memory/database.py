
import sqlite3

from contextlib import contextmanager
from pathlib import Path

from config import DATABASE_PATH


class Database:

    def __init__(self, db_path=DATABASE_PATH):

        self.db_path = Path(db_path)

        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.initialize()

    @contextmanager
    def connect(self):

        connection = sqlite3.connect(
            str(self.db_path),
            timeout=10,
        )

        connection.row_factory = sqlite3.Row

        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        try:

            yield connection

            connection.commit()

        except BaseException:

            connection.rollback()
            raise

        finally:

            connection.close()

    def initialize(self):

        with self.connect() as connection:

            connection.executescript("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    role TEXT NOT NULL
                        CHECK(role IN ('user', 'assistant')),
                    content TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,

                    FOREIGN KEY(session_id)
                        REFERENCES sessions(id)
                        ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS user_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    memory_key TEXT NOT NULL UNIQUE,
                    memory_value TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS
                    idx_messages_session
                ON messages(session_id, id);
            """)

    def create_session(self, title="New Conversation"):

        with self.connect() as connection:

            cursor = connection.execute(
                """
                INSERT INTO sessions (title)
                VALUES (?)
                """,
                (title,),
            )

            return cursor.lastrowid

    def get_latest_session(self):

        with self.connect() as connection:

            row = connection.execute(
                """
                SELECT id
                FROM sessions
                ORDER BY id DESC
                LIMIT 1
                """
            ).fetchone()

            return row["id"] if row else None

    def save_turn(
        self,
        session_id,
        user_message,
        assistant_message,
    ):

        with self.connect() as connection:

            connection.executemany(
                """
                INSERT INTO messages (
                    session_id,
                    role,
                    content
                )
                VALUES (?, ?, ?)
                """,
                [
                    (
                        session_id,
                        "user",
                        user_message,
                    ),
                    (
                        session_id,
                        "assistant",
                        assistant_message,
                    ),
                ],
            )

    def get_messages(self, session_id, limit=12):

        with self.connect() as connection:

            rows = connection.execute(
                """
                SELECT role, content
                FROM messages
                WHERE session_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (session_id, limit),
            ).fetchall()

            return [
                dict(row)
                for row in reversed(rows)
            ]

    def save_memory(self, key, value):

        with self.connect() as connection:

            connection.execute(
                """
                INSERT INTO user_memory (
                    memory_key,
                    memory_value
                )
                VALUES (?, ?)

                ON CONFLICT(memory_key)
                DO UPDATE SET
                    memory_value = excluded.memory_value,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (key, value),
            )

    def get_memory(self, key):

        with self.connect() as connection:

            row = connection.execute(
                """
                SELECT memory_value
                FROM user_memory
                WHERE memory_key = ?
                """,
                (key,),
            ).fetchone()

            return row["memory_value"] if row else None

    def get_all_memory(self, limit=20):

        with self.connect() as connection:

            rows = connection.execute(
                """
                SELECT memory_key, memory_value
                FROM user_memory
                ORDER BY updated_at DESC, id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

            return {
                row["memory_key"]: row["memory_value"]
                for row in rows
            }

    def delete_memory(self, key):

        with self.connect() as connection:

            cursor = connection.execute(
                """
                DELETE FROM user_memory
                WHERE memory_key = ?
                """,
                (key,),
            )

            return cursor.rowcount > 0

    def clear_memory(self):

        with self.connect() as connection:

            connection.execute(
                "DELETE FROM user_memory"
            )

    def clear_all_data(self):

        with self.connect() as connection:

            connection.execute(
                "DELETE FROM sessions"
            )

            connection.execute(
                "DELETE FROM user_memory"
            )
