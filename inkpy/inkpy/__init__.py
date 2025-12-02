"""
InkPy - React for CLIs in Python
"""

__version__ = "0.1.0"

# Main render function
# Components
from inkpy.components.box import Box
from inkpy.components.newline import Newline
from inkpy.components.spacer import Spacer
from inkpy.components.static import Static
from inkpy.components.text import Text
from inkpy.components.transform import Transform

# Hooks
from inkpy.hooks.use_app import use_app
from inkpy.hooks.use_focus import use_focus
from inkpy.hooks.use_focus_manager import use_focus_manager
from inkpy.hooks.use_input import use_input
from inkpy.hooks.use_is_screen_reader_enabled import use_is_screen_reader_enabled
from inkpy.hooks.use_stderr import use_stderr
from inkpy.hooks.use_stdin import use_stdin
from inkpy.hooks.use_stdout import use_stdout

# Utilities
from inkpy.measure_element import measure_element
from inkpy.render import render

__all__ = [
    # Components
    "Box",
    "Newline",
    "Spacer",
    "Static",
    "Text",
    "Transform",
    # Utilities
    "measure_element",
    # Core
    "render",
    # Hooks
    "use_app",
    "use_focus",
    "use_focus_manager",
    "use_input",
    "use_is_screen_reader_enabled",
    "use_stderr",
    "use_stdin",
    "use_stdout",
]
