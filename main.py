
import time

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from config import (
    APP_NAME,
    APP_VERSION,
    COMPANY_NAME,
    MODEL_NAME,
    CPU_THREADS,
    CONTEXT_SIZE,
    MAX_TOKENS,
    STREAMING_ENABLED,
    initialize_directories,
)

from core.file_assistant import FileEnabledKlubAI


console = Console()


def show_banner():

    console.clear()

    banner = Text()

    banner.append(
        "K L U B A I\n\n",
        style="bold green",
    )

    banner.append(
        "Independent AI Assistant\n"
    )

    banner.append(
        f"Developed by {COMPANY_NAME}\n"
    )

    banner.append(
        f"Version: {APP_VERSION}\n"
    )

    banner.append(
        "Execution Mode: Local CPU\n"
    )

    banner.append(
        "External AI API: Not Required\n"
    )

    banner.append(
        "Persistent Memory: Enabled\n"
    )

    banner.append(
        "Response Streaming: "
        f"{'Enabled' if STREAMING_ENABLED else 'Disabled'}"
    )

    console.print(
        Panel(
            banner,
            title=APP_NAME,
            border_style="green",
            expand=False,
        )
    )


def show_help():

    table = Table(
        title="KlubAI Commands"
    )

    table.add_column(
        "Command",
        style="cyan",
    )

    table.add_column(
        "Description"
    )

    commands = [
        ("/file-help", "Show file generation commands"),
        ("/create format topic", "Generate a file"),
        ("/files", "Show generated files"),
        ("/help", "Show available commands"),
        ("/clear", "Clear terminal screen"),
        ("/new", "Start a new conversation"),
        ("/history", "Show conversation history"),
        ("/model", "Show AI model information"),
        ("/memory-help", "Show memory commands"),
        ("/memory", "Display saved facts"),
        ("/remember key=value", "Save information"),
        ("/recall key", "Retrieve information"),
        ("/forget key", "Remove saved information"),
        ("/forget-all confirm", "Remove all saved facts"),
        ("/delete-data confirm", "Clear all saved data"),
        ("/exit", "Exit KlubAI"),
    ]

    for command, description in commands:

        table.add_row(
            command,
            description,
        )

    console.print(table)


def show_model_information():

    table = Table(
        title="KlubAI Model Information"
    )

    table.add_column(
        "Property",
        style="cyan",
    )

    table.add_column("Value")

    information = [
        ("Application", APP_NAME),
        ("Version", APP_VERSION),
        ("Developer", COMPANY_NAME),
        ("Foundation model", MODEL_NAME),
        ("Execution", "Local CPU"),
        ("CPU threads", str(CPU_THREADS)),
        ("Context size", str(CONTEXT_SIZE)),
        ("Maximum output tokens", str(MAX_TOKENS)),
        ("Memory database", "SQLite"),
        (
            "Streaming",
            "Enabled" if STREAMING_ENABLED else "Disabled"
        ),
        ("External AI API", "Not required"),
        ("Internet access", "Not implemented"),
    ]

    for key, value in information:

        table.add_row(key, value)

    console.print(table)


def show_history(assistant):

    history = assistant.get_history()

    if not history:

        console.print(
            "[yellow]No conversation history.[/yellow]"
        )

        return

    console.print(
        "\n[bold green]Conversation History[/bold green]\n"
    )

    for message in history:

        role = message["role"]

        label = (
            "You"
            if role == "user"
            else "KlubAI"
        )

        color = (
            "cyan"
            if role == "user"
            else "green"
        )

        console.print(
            f"[bold {color}]{label}:[/bold {color}]"
        )

        console.print(
            message["content"],
            markup=False,
            highlight=False,
        )

        console.print()


def display_response(assistant, user_input):

    start_time = time.perf_counter()

    first_response_time = None

    console.print(
        "\n[bold green]KlubAI:[/bold green]"
    )

    if STREAMING_ENABLED:

        stream = assistant.chat_stream(
            user_input
        )

        try:

            for chunk in stream:

                if first_response_time is None:

                    first_response_time = (
                        time.perf_counter()
                        - start_time
                    )

                console.file.write(chunk)
                console.file.flush()

        finally:

            stream.close()

            console.file.write("\n")
            console.file.flush()

    else:

        response = assistant.chat(
            user_input
        )

        console.print(
            response,
            markup=False,
            highlight=False,
        )

    elapsed_time = (
        time.perf_counter()
        - start_time
    )

    console.print()

    if first_response_time is not None:

        console.print(
            f"[dim]First response: "
            f"{first_response_time:.2f}s[/dim]"
        )

    console.print(
        f"[dim]Response time: "
        f"{elapsed_time:.2f}s[/dim]\n"
    )


def main():

    initialize_directories()

    show_banner()

    assistant = None

    try:

        assistant = FileEnabledKlubAI()

        with console.status(
            "[bold green]Loading local AI model..."
        ):

            assistant.initialize()

        console.print(
            "[bold green]AI Engine Ready![/bold green]"
        )

        console.print(
            "KlubAI is running locally."
        )

        console.print(
            "Conversations and recognized user facts "
            "are saved locally in SQLite."
        )

        console.print(
            "Type [cyan]/help[/cyan] "
            "for available commands.\n"
        )

        while True:

            try:

                user_input = console.input(
                    "[bold cyan]You: [/bold cyan]"
                ).strip()

                if not user_input:

                    continue

                command = user_input.lower()

                if command in (
                    "/exit",
                    "exit",
                    "quit",
                ):

                    console.print(
                        "\n[bold green]"
                        "KlubAI: Goodbye!"
                        "[/bold green]"
                    )

                    break

                if command == "/help":

                    show_help()
                    continue

                if command == "/clear":

                    show_banner()
                    continue

                if command == "/new":

                    assistant.clear_conversation()

                    console.print(
                        "[green]New conversation "
                        "started.[/green]"
                    )

                    continue

                if command == "/history":

                    show_history(assistant)
                    continue

                if command == "/model":

                    show_model_information()
                    continue

                display_response(
                    assistant,
                    user_input,
                )

            except KeyboardInterrupt:

                console.print(
                    "\n[yellow]Response interrupted. "
                    "Incomplete AI response was not saved."
                    "[/yellow]\n"
                )

            except EOFError:

                break

            except Exception as error:

                console.print(
                    Text(
                        f"Error: {error}",
                        style="red",
                    )
                )

    except Exception as error:

        console.print(
            Text(
                f"Model initialization failed: {error}",
                style="red",
            )
        )

    finally:

        if assistant is not None:

            assistant.shutdown()


if __name__ == "__main__":

    main()
