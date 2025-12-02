"""
Spacer component module.

A flexible space that expands along the major axis.
"""

from reactpy import component

from .box import Box


@component
def Spacer():
    """
    A flexible space that expands to fill available space.

    Example:
        Box([
            Text("Left"),
            Spacer(),
            Text("Right")
        ])
    """
    return Box(style={"flexGrow": 1})
