"""
StdoutContext module - ReactPy context for stdout stream access
"""
from typing import TextIO, Callable, Dict, Any
import sys
from reactpy.core.hooks import create_context

# Default context value - dict with stdout stream and write function
_default_value: Dict[str, Any] = {
    'stdout': sys.stdout,
    'write': lambda data: sys.stdout.write(data)
}

# Create context with default stdout
StdoutContext = create_context(_default_value)

StdoutContext.__name__ = 'InternalStdoutContext'

