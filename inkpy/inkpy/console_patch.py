"""
Console patching module - Intercept console output to prevent mixing with Ink output.

Ported from: patch-console (Node.js)
When console methods are called (like print()), Ink intercepts their output,
clears the main output, renders output from the console method, and then
rerenders the main output again.
"""

import sys
from io import StringIO
from typing import Callable, TextIO


class InterceptingStream:
    """
    A file-like object that intercepts writes and calls a callback.
    """

    def __init__(
        self, original_stream: TextIO, stream_name: str, callback: Callable[[str, str], None]
    ):
        self.original_stream = original_stream
        self.stream_name = stream_name
        self.callback = callback
        self.buffer = StringIO()

    def write(self, data: str) -> int:
        """Intercept write calls"""
        # Call callback with intercepted data
        self.callback(self.stream_name, data)
        # Also write to original stream (for compatibility)
        return self.original_stream.write(data)

    def flush(self):
        """Flush the stream"""
        self.original_stream.flush()

    def __getattr__(self, name):
        """Delegate other attributes to original stream"""
        return getattr(self.original_stream, name)


def patch_console(
    stdout: TextIO, stderr: TextIO, callback: Callable[[str, str], None]
) -> Callable[[], None]:
    """
    Patch console methods (print, sys.stdout, sys.stderr) to intercept output.

    Args:
        stdout: Standard output stream
        stderr: Standard error stream
        callback: Callback function called with (stream_name, data) when output occurs

    Returns:
        Restore function to undo the patching
    """
    # Store original streams
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    # Create intercepting streams
    intercepting_stdout = InterceptingStream(stdout, "stdout", callback)
    intercepting_stderr = InterceptingStream(stderr, "stderr", callback)

    # Replace sys.stdout and sys.stderr
    sys.stdout = intercepting_stdout
    sys.stderr = intercepting_stderr

    def restore():
        """Restore original streams"""
        sys.stdout = original_stdout
        sys.stderr = original_stderr

    return restore


def restore_console(restore_fn: Callable[[], None]):
    """
    Restore console to original state.

    Args:
        restore_fn: Function returned from patch_console
    """
    if restore_fn:
        restore_fn()
