"""
Spinner component module.

Provides an animated loading indicator with multiple styles.
Similar to Ink's Spinner component.
"""

from typing import Optional, Union

from reactpy import component, html
from reactpy.core.hooks import use_effect, use_state

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
):
    """
    Spinner component for animated loading indicators.

    Args:
        type: Spinner style ('dots', 'line', 'arc', 'circle', etc.)
        text: Text to display next to spinner
        color: Color for the spinner

    Example:
        @component
        def App():
            return Spinner(type="dots", text="Loading...")
    """
    # Get spinner configuration
    spinner_config = SPINNER_TYPES.get(type, SPINNER_TYPES["dots"])
    frames = spinner_config["frames"]
    interval = spinner_config["interval"]

    # Track current frame
    frame_index, set_frame_index = use_state(0)

    # Set up animation timer
    def setup_animation():
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

    use_effect(setup_animation, [type])

    # Get current frame
    current_frame = frames[frame_index % len(frames)]

    # Build spinner style
    spinner_style = {}
    if color:
        spinner_style["color"] = color

    # Render
    children = [html.span({"style": spinner_style}, current_frame)]
    if text:
        children.append(html.span({}, f" {text}"))

    return html.span({"style": {"flexDirection": "row"}}, *children)
