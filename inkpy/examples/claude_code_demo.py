#!/usr/bin/env python3
"""
Mini Claude-Code CLI Demo using InkPy

Demonstrates the key UI patterns needed for building Claude-Code-like CLIs:
- Welcome screen with styled text
- Spinner with status transitions (loading → success/failure)
- Streaming text output (typewriter effect)
- Input prompts (text, select, confirm)
- Progress bar for operations
- Table display for structured data
"""

import random
import threading
import time

from reactpy import component, use_effect, use_state

from inkpy import render
from inkpy.components import (
    Box,
    ConfirmInput,
    ProgressBar,
    SelectInput,
    Spinner,
    SpinnerStatus,
    StreamingText,
    Table,
    Text,
    TextInput,
)
from inkpy.hooks import use_app, use_input


@component
def WelcomeScreen(on_continue):
    """Welcome screen with styled branding."""

    def handle_input(input_str, key):
        if key.return_key:
            on_continue()

    use_input(handle_input)

    return Box(
        [
            Text(""),
            Text("  Claude Code CLI Demo", color="blue", bold=True),
            Text("  Version 0.1.0 (InkPy Demo)", color="gray"),
            Text(""),
            Text("  Welcome! This demo showcases InkPy capabilities.", color="white"),
            Text("  Type /help for available commands.", color="cyan"),
            Text(""),
            Text("  Press Enter to continue...", color="gray"),
            Text(""),
        ],
        flex_direction="column",
        border_style="round",
        padding=1,
    )


@component
def MainMenu(on_select):
    """Main menu with option selection."""
    options = [
        {"label": "Spinner Demo", "value": "spinner"},
        {"label": "Streaming Text Demo", "value": "streaming"},
        {"label": "Progress Bar Demo", "value": "progress"},
        {"label": "Table Demo", "value": "table"},
        {"label": "Input Demo", "value": "input"},
        {"label": "Exit", "value": "exit"},
    ]

    return Box(
        [
            Text("Select a demo:", color="cyan", bold=True),
            Text(""),
            SelectInput(
                items=options,
                on_select=lambda item: on_select(item["value"]),
            ),
        ],
        flex_direction="column",
        padding=1,
    )


@component
def SpinnerDemo(on_back):
    """Demonstrates spinner with status transitions."""
    status, set_status = use_state(SpinnerStatus.SPINNING)
    message, set_message = use_state("Loading data...")

    def simulate_operation():
        """Simulate an async operation."""
        time.sleep(2)
        if random.random() > 0.3:
            set_status(SpinnerStatus.SUCCESS)
            set_message("Data loaded successfully!")
        else:
            set_status(SpinnerStatus.FAILURE)
            set_message("Failed to load data")

    # Start operation on mount
    def start_operation():
        thread = threading.Thread(target=simulate_operation, daemon=True)
        thread.start()

    use_effect(start_operation, [])

    def handle_input(input_str, key):
        if key.return_key and status != SpinnerStatus.SPINNING:
            on_back()

    use_input(handle_input)

    return Box(
        [
            Text("Spinner Status Demo", color="cyan", bold=True),
            Text(""),
            Spinner(text=message, status=status, type="dots"),
            Text(""),
            Text(
                "Press Enter to go back..." if status != SpinnerStatus.SPINNING else "",
                color="gray",
            ),
        ],
        flex_direction="column",
        padding=1,
    )


@component
def StreamingDemo(on_back):
    """Demonstrates streaming text with typewriter effect."""
    complete, set_complete = use_state(False)

    sample_response = (
        "Hello! I'm Claude, an AI assistant created by Anthropic. "
        "I can help you with coding, writing, analysis, and much more. "
        "This text is being rendered character by character to simulate "
        "a streaming AI response. Pretty cool, right?"
    )

    def handle_input(input_str, key):
        if key.return_key and complete:
            on_back()

    use_input(handle_input)

    return Box(
        [
            Text("Streaming Text Demo", color="cyan", bold=True),
            Text(""),
            StreamingText(
                text=sample_response,
                speed_ms=30,
                on_complete=lambda: set_complete(True),
                color="white",
            ),
            Text(""),
            Text("Press Enter to go back..." if complete else "", color="gray"),
        ],
        flex_direction="column",
        padding=1,
    )


@component
def ProgressDemo(on_back):
    """Demonstrates progress bar with animated progress."""
    progress, set_progress = use_state(0.0)
    complete, set_complete = use_state(False)

    def animate_progress():
        for i in range(101):
            set_progress(i / 100)
            time.sleep(0.03)
        set_complete(True)

    use_effect(lambda: threading.Thread(target=animate_progress, daemon=True).start(), [])

    def handle_input(input_str, key):
        if key.return_key and complete:
            on_back()

    use_input(handle_input)

    return Box(
        [
            Text("Progress Bar Demo", color="cyan", bold=True),
            Text(""),
            Text("Downloading files...", color="white"),
            ProgressBar(value=progress, width=40, color="green"),
            Text(""),
            Spinner(
                text="Complete!" if complete else "Processing...",
                status=SpinnerStatus.SUCCESS if complete else SpinnerStatus.SPINNING,
            ),
            Text(""),
            Text("Press Enter to go back..." if complete else "", color="gray"),
        ],
        flex_direction="column",
        padding=1,
    )


@component
def TableDemo(on_back):
    """Demonstrates table with styled headers."""

    data = [
        {"command": "/help", "description": "Show help", "status": "Available"},
        {"command": "/ask", "description": "Ask a question", "status": "Available"},
        {"command": "/edit", "description": "Edit files", "status": "Beta"},
        {"command": "/run", "description": "Run commands", "status": "Available"},
    ]

    columns = [
        {"key": "command", "header": "Command"},
        {"key": "description", "header": "Description"},
        {"key": "status", "header": "Status"},
    ]

    def handle_input(input_str, key):
        if key.return_key:
            on_back()

    use_input(handle_input)

    return Box(
        [
            Text("Table Demo - Available Commands", color="cyan", bold=True),
            Text(""),
            Table(
                data=data,
                columns=columns,
                header_style={"color": "blue"},
                border=True,
            ),
            Text(""),
            Text("Press Enter to go back...", color="gray"),
        ],
        flex_direction="column",
        padding=1,
    )


@component
def InputDemo(on_back):
    """Demonstrates various input types."""
    step, set_step = use_state(0)
    name, set_name = use_state("")
    confirmed, set_confirmed = use_state(None)

    def handle_name_submit(value):
        set_name(value)
        set_step(1)

    def handle_confirm(value):
        set_confirmed(value)
        set_step(2)

    def handle_input(input_str, key):
        if key.return_key and step == 2:
            on_back()

    use_input(handle_input)

    if step == 0:
        return Box(
            [
                Text("Input Demo", color="cyan", bold=True),
                Text(""),
                Text("What's your name?", color="white"),
                TextInput(
                    value=name,
                    on_change=set_name,
                    on_submit=handle_name_submit,
                    placeholder="Enter your name...",
                ),
            ],
            flex_direction="column",
            padding=1,
        )

    if step == 1:
        return Box(
            [
                Text("Input Demo", color="cyan", bold=True),
                Text(""),
                Text(f"Hello, {name}!", color="green"),
                Text("Would you like to continue?", color="white"),
                ConfirmInput(on_submit=handle_confirm),
            ],
            flex_direction="column",
            padding=1,
        )

    return Box(
        [
            Text("Input Demo", color="cyan", bold=True),
            Text(""),
            Text(f"Hello, {name}!", color="green"),
            Text(
                f"You chose: {'Yes' if confirmed else 'No'}",
                color="cyan" if confirmed else "yellow",
            ),
            Text(""),
            Text("Press Enter to go back...", color="gray"),
        ],
        flex_direction="column",
        padding=1,
    )


@component
def App():
    """Main application component."""
    screen, set_screen = use_state("welcome")
    app = use_app()

    def handle_welcome_continue():
        set_screen("menu")

    def handle_menu_select(value):
        if value == "exit":
            app.exit()
        else:
            set_screen(value)

    def handle_back():
        set_screen("menu")

    if screen == "welcome":
        return WelcomeScreen(on_continue=handle_welcome_continue)
    elif screen == "menu":
        return MainMenu(on_select=handle_menu_select)
    elif screen == "spinner":
        return SpinnerDemo(on_back=handle_back)
    elif screen == "streaming":
        return StreamingDemo(on_back=handle_back)
    elif screen == "progress":
        return ProgressDemo(on_back=handle_back)
    elif screen == "table":
        return TableDemo(on_back=handle_back)
    elif screen == "input":
        return InputDemo(on_back=handle_back)

    return Text("Unknown screen", color="red")


def main():
    """Entry point for the demo application."""
    print("\033[2J\033[H")  # Clear screen
    print("Starting Claude Code Demo...")
    print("Press Ctrl+C to exit at any time.\n")

    instance = render(App())
    try:
        import asyncio

        asyncio.run(instance.wait_until_exit())
    except KeyboardInterrupt:
        instance.unmount()
        print("\nGoodbye!")


if __name__ == "__main__":
    main()
