"""
StderrContext module - ReactPy context for stderr stream access
"""
from typing import Dict, Any
import sys
from reactpy.core.hooks import create_context

# Default context value - dict with stderr stream and write function
_default_value: Dict[str, Any] = {
    'stderr': sys.stderr,
    'write': lambda data: sys.stderr.write(data)
}

# Create context with default stderr
StderrContext = create_context(_default_value)

StderrContext.__name__ = 'InternalStderrContext'

