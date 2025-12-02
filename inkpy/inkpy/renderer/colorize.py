"""
Colorize text with ANSI escape codes.

Ports the colorize functionality from Ink's colorize.ts to Python.
Supports named colors, hex colors, 256-color palette, and RGB colors.
"""

import re
from typing import Literal, Union

ColorType = Literal["foreground", "background"]

# Named color mappings to ANSI codes
NAMED_COLORS = {
    "black": 0,
    "red": 1,
    "green": 2,
    "yellow": 3,
    "blue": 4,
    "magenta": 5,
    "cyan": 6,
    "white": 7,
    "gray": 8,
    "grey": 8,
    # Bright variants
    "brightBlack": 8,
    "brightRed": 9,
    "brightGreen": 10,
    "brightYellow": 11,
    "brightBlue": 12,
    "brightMagenta": 13,
    "brightCyan": 14,
    "brightWhite": 15,
}

# ANSI escape codes
RESET = "\x1b[0m"
FOREGROUND_BASE = 30
BACKGROUND_BASE = 40
BRIGHT_FOREGROUND_BASE = 90
BRIGHT_BACKGROUND_BASE = 100


def colorize(text: str, color: Union[str, int, None], color_type: ColorType = "foreground") -> str:
    """
    Apply color to text using ANSI escape codes.

    Args:
        text: Text to colorize
        color: Color specification (named color, hex, 256-color index, or RGB)
        color_type: 'foreground' or 'background'

    Returns:
        Colored text with ANSI escape codes
    """
    if not color:
        return text

    if not text:
        return text

    # Handle integer (256-color palette)
    if isinstance(color, int):
        if 0 <= color <= 255:
            if color_type == "foreground":
                return f"\x1b[38;5;{color}m{text}{RESET}"
            else:
                return f"\x1b[48;5;{color}m{text}{RESET}"
        return text

    color_str = str(color)

    # Named colors
    if color_str.lower() in NAMED_COLORS:
        code = NAMED_COLORS[color_str.lower()]
        base = FOREGROUND_BASE if color_type == "foreground" else BACKGROUND_BASE

        # Bright colors (8-15) use different base
        if code >= 8:
            base = BRIGHT_FOREGROUND_BASE if color_type == "foreground" else BRIGHT_BACKGROUND_BASE
            code = code - 8

        ansi_code = base + code
        return f"\x1b[{ansi_code}m{text}{RESET}"

    # Hex colors (#RRGGBB)
    if color_str.startswith("#"):
        hex_match = re.match(r"^#([0-9a-fA-F]{6})$", color_str)
        if hex_match:
            hex_value = hex_match.group(1)
            r = int(hex_value[0:2], 16)
            g = int(hex_value[2:4], 16)
            b = int(hex_value[4:6], 16)

            if color_type == "foreground":
                return f"\x1b[38;2;{r};{g};{b}m{text}{RESET}"
            else:
                return f"\x1b[48;2;{r};{g};{b}m{text}{RESET}"

        # Short hex (#RGB)
        short_hex_match = re.match(r"^#([0-9a-fA-F]{3})$", color_str)
        if short_hex_match:
            hex_value = short_hex_match.group(1)
            r = int(hex_value[0] * 2, 16)
            g = int(hex_value[1] * 2, 16)
            b = int(hex_value[2] * 2, 16)

            if color_type == "foreground":
                return f"\x1b[38;2;{r};{g};{b}m{text}{RESET}"
            else:
                return f"\x1b[48;2;{r};{g};{b}m{text}{RESET}"

        return text

    # RGB format: rgb(r, g, b)
    rgb_match = re.match(r"^rgb\(\s?(\d+),\s?(\d+),\s?(\d+)\s?\)$", color_str)
    if rgb_match:
        r = int(rgb_match.group(1))
        g = int(rgb_match.group(2))
        b = int(rgb_match.group(3))

        # Clamp values to 0-255
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))

        if color_type == "foreground":
            return f"\x1b[38;2;{r};{g};{b}m{text}{RESET}"
        else:
            return f"\x1b[48;2;{r};{g};{b}m{text}{RESET}"

    # ANSI256 format: ansi256(n)
    ansi256_match = re.match(r"^ansi256\(\s?(\d+)\s?\)$", color_str)
    if ansi256_match:
        value = int(ansi256_match.group(1))
        if 0 <= value <= 255:
            if color_type == "foreground":
                return f"\x1b[38;5;{value}m{text}{RESET}"
            else:
                return f"\x1b[48;5;{value}m{text}{RESET}"

    # Unknown color format, return text as-is
    return text
