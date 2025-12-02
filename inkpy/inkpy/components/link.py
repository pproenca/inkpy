"""
Link component module.

Provides terminal hyperlinks using OSC 8 escape sequences.
Supported by iTerm2, Hyper, Windows Terminal, and other modern terminals.
"""

from typing import Optional

from reactpy import component, html


def create_hyperlink(url: str, text: str) -> str:
    """
    Create a terminal hyperlink using OSC 8 escape sequence.

    The OSC 8 format is:
        ESC ] 8 ; params ; URL ST text ESC ] 8 ; ; ST

    Where:
        - ESC ] is OSC (Operating System Command)
        - ST is String Terminator (ESC \\)
        - params are optional (like id=value)

    Args:
        url: The URL to link to
        text: The visible text for the link

    Returns:
        String with OSC 8 escape sequences for terminal hyperlink
    """
    # OSC 8 escape sequences
    osc = "\x1b]8;;"  # Start: ESC ] 8 ; ;
    st = "\x1b\\"  # String Terminator: ESC \

    # Format: OSC URL ST text OSC ST
    return f"{osc}{url}{st}{text}{osc}{st}"


@component
def Link(
    url: str,
    children: Optional[str] = None,
    fallback: bool = False,
    color: str = "cyan",
    underline: bool = True,
):
    """
    Link component for terminal hyperlinks.

    Uses OSC 8 escape sequences for clickable links in supported terminals.
    Falls back to showing URL in parentheses for unsupported terminals.

    Args:
        url: The URL to link to
        children: Link text (defaults to URL if not provided)
        fallback: Whether to show URL in fallback mode
        color: Link text color
        underline: Whether to underline the link text

    Example:
        @component
        def App():
            return Box(children=[
                Link(url="https://github.com", children="GitHub"),
                Text(" - "),
                Link(url="https://python.org"),
            ])
    """
    # Use URL as text if no children provided
    text = children if children else url

    # Create the hyperlink with OSC 8
    linked_text = create_hyperlink(url, text)

    # Build style
    style = {"color": color}
    if underline:
        # ANSI underline escape codes will be applied by the renderer
        pass

    if fallback:
        # Show URL in parentheses for terminals that don't support OSC 8
        display = f"{text} ({url})"
    else:
        display = linked_text

    # Apply underline via ANSI codes if requested
    if underline:
        display = f"\x1b[4m{display}\x1b[24m"

    return html.span(
        {"style": style},
        display,
    )
