"""
InkPy - React for CLIs in Python
"""

__version__ = "0.1.0"

# Main render function
from inkpy.render import render

# Components
from inkpy.components.box import Box
from inkpy.components.text import Text
from inkpy.components.static import Static
from inkpy.components.newline import Newline
from inkpy.components.spacer import Spacer
from inkpy.components.transform import Transform

# Hooks
from inkpy.hooks.use_app import use_app
from inkpy.hooks.use_input import use_input
from inkpy.hooks.use_stdin import use_stdin
from inkpy.hooks.use_stdout import use_stdout
from inkpy.hooks.use_stderr import use_stderr
from inkpy.hooks.use_focus import use_focus
from inkpy.hooks.use_focus_manager import use_focus_manager
from inkpy.hooks.use_is_screen_reader_enabled import use_is_screen_reader_enabled

# Utilities
from inkpy.measure_element import measure_element

__all__ = [
    # Core
    'render',
    
    # Components
    'Box',
    'Text',
    'Static',
    'Newline',
    'Spacer',
    'Transform',
    
    # Hooks
    'use_app',
    'use_input',
    'use_stdin',
    'use_stdout',
    'use_stderr',
    'use_focus',
    'use_focus_manager',
    'use_is_screen_reader_enabled',
    
    # Utilities
    'measure_element',
]
