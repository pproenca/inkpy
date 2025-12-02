"""
TextInput component module.

Provides a controlled text input field with cursor, validation, and submit handling.
Similar to Ink's TextInput component.
"""

from typing import Callable, Optional

from reactpy import component, html
from reactpy.core.hooks import use_effect, use_state

from inkpy.hooks.use_input import use_input
from inkpy.input.keypress import Key


@component
def TextInput(
    value: str = "",
    placeholder: str = "",
    focus: bool = True,
    mask: Optional[str] = None,
    on_change: Optional[Callable[[str], None]] = None,
    on_submit: Optional[Callable[[str], None]] = None,
    show_cursor: bool = True,
):
    """
    TextInput component for capturing user text input.

    Args:
        value: Current input value (controlled)
        placeholder: Placeholder text shown when value is empty
        focus: Whether input is focused and capturing input
        mask: Character to mask input with (for passwords)
        on_change: Called with new value when input changes
        on_submit: Called with value when Enter is pressed
        show_cursor: Whether to show cursor indicator

    Example:
        @component
        def App():
            text, set_text = use_state("")

            def handle_submit(value):
                print(f"Submitted: {value}")

            return TextInput(
                value=text,
                on_change=set_text,
                on_submit=handle_submit,
                placeholder="Enter text..."
            )
    """
    # Internal cursor position (for future cursor movement support)
    cursor_pos, set_cursor_pos = use_state(len(value))

    # Keep cursor at end when value changes
    use_effect(lambda: set_cursor_pos(len(value)), [value])

    def handle_input(input_str: str, key: Key):
        if not focus:
            return

        # Handle Enter key
        if key.return_key:
            if on_submit:
                on_submit(value)
            return

        # Handle Backspace
        if key.backspace or key.delete:
            if value and on_change:
                on_change(value[:-1])
            return

        # Handle Escape (could be used to blur)
        if key.escape:
            return

        # Handle regular character input
        if input_str and not key.ctrl and not key.meta:
            if on_change:
                on_change(value + input_str)

    # Set up input handling
    use_input(handle_input, is_active=focus)

    # Determine display text
    if value:
        if mask:
            display_text = mask * len(value)
        else:
            display_text = value
    else:
        display_text = placeholder

    # Add cursor if focused and showing cursor
    cursor = "█" if focus and show_cursor else ""

    # Style for placeholder vs value
    is_placeholder = not value and placeholder
    style = {
        "flexDirection": "row",
        "flexGrow": 0,
        "flexShrink": 1,
    }

    if is_placeholder:
        # Dim style for placeholder
        return html.span(
            {"style": style},
            html.span({"style": {"color": "gray"}}, display_text),
            cursor,
        )

    return html.span({"style": style}, display_text, cursor)
