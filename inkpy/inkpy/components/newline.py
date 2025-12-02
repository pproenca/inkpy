"""
Newline component module.

Adds one or more newline characters.
"""

from reactpy import component

from .text import Text


@component
def Newline(count: int = 1):
    """
    Add one or more newline characters.

    Args:
        count: Number of newlines to insert (default: 1)

    Example:
        Text([
            "Line 1",
            Newline(),
            "Line 2"
        ])
    """
    return Text("\n" * count)
