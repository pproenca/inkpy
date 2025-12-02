"""
ConfirmInput component module.

Provides a Yes/No confirmation dialog with keyboard shortcuts.
Similar to Ink's ConfirmInput component.
"""

from typing import Callable, Optional

from reactpy import component, html

from inkpy.hooks.use_input import use_input
from inkpy.input.keypress import Key


@component
def ConfirmInput(
    message: str = "",
    on_confirm: Optional[Callable[[bool], None]] = None,
    default_value: bool = True,
    yes_label: str = "Y",
    no_label: str = "n",
    focus: bool = True,
):
    """
    ConfirmInput component for Yes/No confirmation dialogs.

    Args:
        message: Confirmation message to display
        on_confirm: Called with True/False when user confirms
        default_value: Default value (True=Yes, False=No)
        yes_label: Label for Yes option
        no_label: Label for No option
        focus: Whether input is focused and capturing input

    Example:
        @component
        def App():
            def handle_confirm(confirmed):
                if confirmed:
                    print("User confirmed!")
                else:
                    print("User cancelled.")

            return ConfirmInput(
                message="Are you sure you want to delete this file?",
                on_confirm=handle_confirm,
                default_value=False,
            )
    """

    def handle_input(input_str: str, key: Key):
        if not focus:
            return

        # Handle Y/y for Yes
        if input_str.lower() == "y":
            if on_confirm:
                on_confirm(True)
            return

        # Handle N/n for No
        if input_str.lower() == "n":
            if on_confirm:
                on_confirm(False)
            return

        # Handle Enter for default value
        if key.return_key:
            if on_confirm:
                on_confirm(default_value)
            return

    # Set up input handling
    use_input(handle_input, is_active=focus)

    # Format labels based on default value
    if default_value:
        # Yes is default - capitalize Y
        formatted_yes = yes_label.upper()
        formatted_no = no_label.lower()
    else:
        # No is default - capitalize N
        formatted_yes = yes_label.lower()
        formatted_no = no_label.upper()

    # Build prompt display
    prompt_text = f"{message} ({formatted_yes}/{formatted_no})"

    return html.span(
        {"style": {"flexDirection": "row"}},
        html.span({}, prompt_text),
        html.span({"style": {"color": "gray"}}, " "),
    )
