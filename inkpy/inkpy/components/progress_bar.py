"""
ProgressBar component module.

Provides a determinate progress indicator for displaying
task completion status.
"""

from typing import Optional, Union

from reactpy import component, html

from ..renderer.colorize import colorize


@component
def ProgressBar(
    value: float,
    width: int = 40,
    filled_char: str = "█",
    empty_char: str = "░",
    show_percentage: bool = True,
    color: Optional[Union[str, int]] = None,
    left_bracket: str = "[",
    right_bracket: str = "]",
):
    """
    ProgressBar component for displaying determinate progress.

    Args:
        value: Progress value between 0.0 and 1.0
        width: Width of the progress bar in characters (default: 40)
        filled_char: Character for filled portion (default: "█")
        empty_char: Character for empty portion (default: "░")
        show_percentage: Whether to display percentage (default: True)
        color: Color for the filled portion
        left_bracket: Left bracket character (default: "[")
        right_bracket: Right bracket character (default: "]")

    Example:
        @component
        def App():
            progress, set_progress = use_state(0.0)
            return ProgressBar(value=progress, color="green")
    """
    # Clamp value between 0 and 1
    clamped_value = max(0.0, min(1.0, value))

    # Calculate filled and empty portions
    filled_width = int(width * clamped_value)
    empty_width = width - filled_width

    # Build the bar
    filled_portion = filled_char * filled_width
    empty_portion = empty_char * empty_width

    # Apply color to filled portion if specified
    if color:
        filled_portion = colorize(filled_portion, color, "foreground")

    # Build percentage string
    percentage_str = ""
    if show_percentage:
        percentage_str = f" {int(clamped_value * 100)}%"

    # Combine elements
    bar = f"{left_bracket}{filled_portion}{empty_portion}{right_bracket}{percentage_str}"

    return html.span(
        {"style": {"flexDirection": "row", "flexGrow": 0, "flexShrink": 1}},
        bar,
    )
