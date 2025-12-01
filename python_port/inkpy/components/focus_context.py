"""
FocusContext module - ReactPy context for focus management
"""
from typing import Optional, Callable, Dict, Any
from reactpy.core.hooks import create_context

# Default context value - dict with focus management functions
_default_value: Dict[str, Any] = {
    'active_id': None,
    'add': lambda id, opts: None,
    'remove': lambda id: None,
    'activate': lambda id: None,
    'deactivate': lambda id: None,
    'enable_focus': lambda: None,
    'disable_focus': lambda: None,
    'focus_next': lambda: None,
    'focus_previous': lambda: None,
    'focus': lambda id: None,
}

# Create context with default no-op functions
FocusContext = create_context(_default_value)

FocusContext.__name__ = 'InternalFocusContext'

