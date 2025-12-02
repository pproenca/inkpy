"""
use_terminal_dimensions hook module.

Provides access to terminal dimensions with automatic updates on resize.
"""

import contextlib
import shutil
import signal
from typing import Optional

from reactpy import use_effect, use_state


def get_terminal_dimensions() -> dict[str, int]:
    """
    Get current terminal dimensions.

    Returns:
        Dict with 'columns' and 'rows' keys containing terminal size.
        Falls back to 80x24 if terminal size cannot be determined.
    """
    try:
        size = shutil.get_terminal_size(fallback=(80, 24))
        return {"columns": size.columns, "rows": size.lines}
    except (AttributeError, ValueError, OSError):
        # Fallback for environments where terminal size is unavailable
        return {"columns": 80, "rows": 24}


def use_terminal_dimensions() -> dict[str, int]:
    """
    Hook that returns current terminal dimensions and updates on resize.

    Returns:
        Dict with 'columns' (int) and 'rows' (int) keys.

    Example:
        @component
        def App():
            dimensions = use_terminal_dimensions()
            return Text(f"Terminal: {dimensions['columns']}x{dimensions['rows']}")
    """
    dimensions, set_dimensions = use_state(get_terminal_dimensions)

    def setup_resize_handler():
        def handle_resize(signum: Optional[int] = None, frame=None):
            new_dimensions = get_terminal_dimensions()
            set_dimensions(new_dimensions)

        # Try to set up SIGWINCH handler (Unix only)
        old_handler = None
        try:
            if hasattr(signal, "SIGWINCH"):
                old_handler = signal.signal(signal.SIGWINCH, handle_resize)
        except (ValueError, OSError):
            # signal.signal may fail in non-main thread
            pass

        def cleanup():
            if old_handler is not None:
                with contextlib.suppress(ValueError, OSError):
                    signal.signal(signal.SIGWINCH, old_handler)

        return cleanup

    use_effect(setup_resize_handler, [])

    return dimensions
