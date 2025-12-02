"""
StdoutContext module - ReactPy context for stdout stream access
"""

import sys
from typing import Any

from reactpy.core.hooks import create_context

# Default context value - dict with stdout stream and write function
_default_value: dict[str, Any] = {
    "stdout": sys.stdout,
    "write": lambda data: sys.stdout.write(data),
}

# Create context with default stdout
StdoutContext = create_context(_default_value)

StdoutContext.__name__ = "InternalStdoutContext"
