"""
StdinContext module - ReactPy context for stdin stream access and input handling
"""
from typing import Dict, Any
import sys
from reactpy.core.hooks import create_context
from inkpy.input.event_emitter import EventEmitter

# Default context value - dict with stdin stream, raw mode management, and event emitter
_default_value: Dict[str, Any] = {
    'stdin': sys.stdin,
    'set_raw_mode': lambda enabled: None,
    'is_raw_mode_supported': False,
    'internal_exitOnCtrlC': True,
    'internal_eventEmitter': EventEmitter(),
}

# Create context with default stdin
StdinContext = create_context(_default_value)

StdinContext.__name__ = 'InternalStdinContext'

