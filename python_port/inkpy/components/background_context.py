"""
BackgroundContext module - ReactPy context for inherited background colors
"""
from typing import Optional
from reactpy.core.hooks import create_context

# Default context value - None (no inherited background)
_default_value: Optional[str] = None

# Create context with default None value
background_context = create_context(_default_value)

background_context.__name__ = 'InternalBackgroundContext'

