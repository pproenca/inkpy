"""
StreamingText component module.

Provides incremental text rendering with typewriter effect.
Useful for displaying AI responses, loading messages, or any text that
should appear character by character.
"""

from typing import Callable, Optional, Union

from reactpy import component, html
from reactpy.core.hooks import use_effect, use_state


@component
def StreamingText(
    text: str,
    speed_ms: int = 50,
    on_complete: Optional[Callable[[], None]] = None,
    color: Optional[Union[str, int]] = None,
    bold: bool = False,
    italic: bool = False,
):
    """
    StreamingText component for incremental text rendering.

    Renders text character by character with a configurable speed,
    creating a typewriter effect commonly used in AI chat interfaces.

    Args:
        text: The full text to display incrementally
        speed_ms: Milliseconds between each character (default: 50ms)
        on_complete: Callback function called when all text is displayed
        color: Foreground color for the text
        bold: Make text bold
        italic: Make text italic

    Example:
        @component
        def App():
            return StreamingText(
                text="Hello, World!",
                speed_ms=30,
                on_complete=lambda: print("Done!")
            )
    """
    # Track how many characters to display
    char_count, set_char_count = use_state(0)
    # Track whether streaming is complete
    is_complete, set_is_complete = use_state(False)

    # Set up streaming animation
    def setup_streaming():
        import threading

        timer = None
        running = True
        current_count = 0

        def advance_char():
            nonlocal timer, current_count
            if not running:
                return

            current_count += 1
            if current_count <= len(text):
                set_char_count(current_count)
                timer = threading.Timer(speed_ms / 1000, advance_char)
                timer.daemon = True
                timer.start()
            else:
                # Streaming complete
                set_is_complete(True)

        # Start streaming
        if len(text) > 0:
            timer = threading.Timer(speed_ms / 1000, advance_char)
            timer.daemon = True
            timer.start()
        else:
            # Empty text, immediately complete
            set_is_complete(True)

        def cleanup():
            nonlocal running, timer
            running = False
            if timer:
                timer.cancel()

        return cleanup

    use_effect(setup_streaming, [text, speed_ms])

    # Call on_complete when streaming finishes
    def handle_complete():
        if is_complete and on_complete:
            on_complete()

    use_effect(handle_complete, [is_complete, on_complete])

    # Get displayed text (up to current char count)
    displayed_text = text[:char_count]

    # Build style
    style = {"flexGrow": 0, "flexShrink": 1, "flexDirection": "row"}

    if color:
        style["color"] = color

    # Apply text styles via ANSI codes (combined for efficiency)
    result = displayed_text
    codes = []
    if bold:
        codes.append("1")
    if italic:
        codes.append("3")
    if codes:
        result = f"\x1b[{';'.join(codes)}m{result}\x1b[0m"

    return html.span({"style": style}, result)
