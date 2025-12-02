"""
Spinner component module.

Provides an animated loading indicator with multiple styles and status states.
Similar to Ink's Spinner component with ora-like status functionality.
"""

from enum import Enum
from typing import Optional, Union

from reactpy import component, html
from reactpy.core.hooks import use_effect, use_state


class SpinnerStatus(Enum):
    """Status states for the Spinner component."""

    SPINNING = "spinning"
    SUCCESS = "success"
    FAILURE = "failure"
    WARNING = "warning"
    INFO = "info"


# Default status colors
DEFAULT_STATUS_COLORS = {
    SpinnerStatus.SUCCESS: "green",
    SpinnerStatus.FAILURE: "red",
    SpinnerStatus.WARNING: "yellow",
    SpinnerStatus.INFO: "blue",
}

# Spinner type definitions (inspired by cli-spinners)
SPINNER_TYPES: dict[str, dict[str, Union[list[str], int]]] = {
    "dots": {
        "interval": 80,
        "frames": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
    },
    "dots2": {
        "interval": 80,
        "frames": ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"],
    },
    "dots3": {
        "interval": 80,
        "frames": ["⠋", "⠙", "⠚", "⠞", "⠖", "⠦", "⠴", "⠲", "⠳", "⠓"],
    },
    "line": {
        "interval": 130,
        "frames": ["-", "\\", "|", "/"],
    },
    "line2": {
        "interval": 100,
        "frames": [".", "-", "=", "#", "=", "-"],
    },
    "arc": {
        "interval": 100,
        "frames": ["◜", "◠", "◝", "◞", "◡", "◟"],
    },
    "circle": {
        "interval": 120,
        "frames": ["◐", "◓", "◑", "◒"],
    },
    "square": {
        "interval": 100,
        "frames": ["◰", "◳", "◲", "◱"],
    },
    "toggle": {
        "interval": 250,
        "frames": ["⊶", "⊷"],
    },
    "bounce": {
        "interval": 120,
        "frames": ["⠁", "⠂", "⠄", "⠂"],
    },
    "bouncingBar": {
        "interval": 80,
        "frames": [
            "[    ]",
            "[=   ]",
            "[==  ]",
            "[=== ]",
            "[ ===]",
            "[  ==]",
            "[   =]",
            "[    ]",
            "[   =]",
            "[  ==]",
            "[ ===]",
            "[====]",
            "[=== ]",
            "[==  ]",
            "[=   ]",
        ],
    },
    "bouncingBall": {
        "interval": 80,
        "frames": [
            "( ●    )",
            "(  ●   )",
            "(   ●  )",
            "(    ● )",
            "(     ●)",
            "(    ● )",
            "(   ●  )",
            "(  ●   )",
            "( ●    )",
            "(●     )",
        ],
    },
    "clock": {
        "interval": 100,
        "frames": ["🕛", "🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "🕗", "🕘", "🕙", "🕚"],
    },
    "earth": {
        "interval": 180,
        "frames": ["🌍", "🌎", "🌏"],
    },
    "moon": {
        "interval": 80,
        "frames": ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"],
    },
    "point": {
        "interval": 125,
        "frames": ["∙∙∙", "●∙∙", "∙●∙", "∙∙●", "∙∙∙"],
    },
    "arrow": {
        "interval": 100,
        "frames": ["←", "↖", "↑", "↗", "→", "↘", "↓", "↙"],
    },
    "simpleDots": {
        "interval": 400,
        "frames": [".  ", ".. ", "...", "   "],
    },
}


@component
def Spinner(
    type: str = "dots",
    text: str = "",
    color: Optional[str] = None,
    status: SpinnerStatus = SpinnerStatus.SPINNING,
    success_icon: str = "✓",
    failure_icon: str = "✗",
    warning_icon: str = "⚠",
    info_icon: str = "i",
):
    """
    Spinner component for animated loading indicators with status states.

    Args:
        type: Spinner style ('dots', 'line', 'arc', 'circle', etc.)
        text: Text to display next to spinner
        color: Color for the spinner (overrides status-based colors)
        status: Current status state (SPINNING, SUCCESS, FAILURE, WARNING, INFO)
        success_icon: Icon to show for SUCCESS status (default: "✓")
        failure_icon: Icon to show for FAILURE status (default: "✗")
        warning_icon: Icon to show for WARNING status (default: "⚠")
        info_icon: Icon to show for INFO status (default: "i")

    Example:
        @component
        def App():
            # Animated spinner
            return Spinner(type="dots", text="Loading...")

        @component
        def CompletedTask():
            # Static success state
            return Spinner(text="Completed", status=SpinnerStatus.SUCCESS)
    """
    # Custom icons mapping
    custom_icons = {
        SpinnerStatus.SUCCESS: success_icon,
        SpinnerStatus.FAILURE: failure_icon,
        SpinnerStatus.WARNING: warning_icon,
        SpinnerStatus.INFO: info_icon,
    }

    # Get spinner configuration
    spinner_config = SPINNER_TYPES.get(type, SPINNER_TYPES["dots"])
    frames = spinner_config["frames"]
    interval = spinner_config["interval"]

    # Track current frame
    frame_index, set_frame_index = use_state(0)

    # Set up animation timer (only when SPINNING)
    def setup_animation():
        if status != SpinnerStatus.SPINNING:
            # No animation needed for static states
            return lambda: None

        import threading

        timer = None
        running = True

        def advance_frame():
            nonlocal timer
            if running:
                set_frame_index(lambda idx: (idx + 1) % len(frames))
                timer = threading.Timer(interval / 1000, advance_frame)
                timer.daemon = True
                timer.start()

        # Start animation
        timer = threading.Timer(interval / 1000, advance_frame)
        timer.daemon = True
        timer.start()

        def cleanup():
            nonlocal running, timer
            running = False
            if timer:
                timer.cancel()

        return cleanup

    use_effect(setup_animation, [type, status])

    # Determine display icon based on status
    if status == SpinnerStatus.SPINNING:
        display_icon = frames[frame_index % len(frames)]
    else:
        display_icon = custom_icons.get(status, "")

    # Determine color based on status (unless explicitly overridden)
    display_color = color
    if display_color is None and status != SpinnerStatus.SPINNING:
        display_color = DEFAULT_STATUS_COLORS.get(status)

    # Build style
    icon_style = {}
    if display_color:
        icon_style["color"] = display_color

    # Render
    children = [html.span({"style": icon_style}, display_icon)]
    if text:
        children.append(html.span({}, f" {text}"))

    return html.span({"style": {"flexDirection": "row"}}, *children)
