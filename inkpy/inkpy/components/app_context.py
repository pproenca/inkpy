"""
AppContext module - ReactPy context for app-level functionality
"""

from typing import Callable, Optional

from reactpy.core.hooks import create_context

# Default context value - dict with exit function
_default_value: dict[str, Callable[[Optional[Exception]], None]] = {"exit": lambda error=None: None}

# Create context with default no-op exit function
AppContext = create_context(_default_value)

AppContext.__name__ = "InternalAppContext"
