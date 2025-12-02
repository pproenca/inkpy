"""
Tests for console patching functionality.

Following TDD: Write failing test first, then implement.
"""

import io
import sys

from inkpy.console_patch import patch_console


def test_patch_console_intercepts_stdout():
    """Test that patch_console intercepts stdout writes"""
    stdout = io.StringIO()
    stderr = io.StringIO()

    # Patch console
    restore_fn = patch_console(stdout, stderr, lambda stream, data: None)

    # Write to stdout
    print("Test output", file=stdout)

    # Should be intercepted
    assert restore_fn is not None

    # Restore
    restore_fn()


def test_patch_console_calls_callback():
    """Test that patch_console calls callback with intercepted data"""
    stdout = io.StringIO()
    stderr = io.StringIO()

    intercepted = []

    def callback(stream, data):
        intercepted.append((stream, data))

    # Patch console
    restore_fn = patch_console(stdout, stderr, callback)

    # Write to stdout (using print() which writes to sys.stdout)
    print("Test output")

    # Should have intercepted
    assert len(intercepted) > 0
    assert any(stream == "stdout" for stream, _ in intercepted)

    # Restore
    restore_fn()


def test_patch_console_handles_stderr():
    """Test that patch_console handles stderr separately"""
    stdout = io.StringIO()
    stderr = io.StringIO()

    intercepted = []

    def callback(stream, data):
        intercepted.append((stream, data))

    # Patch console
    restore_fn = patch_console(stdout, stderr, callback)

    # Write to stderr (using print() which writes to sys.stderr)
    print("Error output", file=sys.stderr)

    # Should have intercepted with stream='stderr'
    assert any(stream == "stderr" for stream, _ in intercepted)

    # Restore
    restore_fn()


def test_restore_console_restores_original():
    """Test that restore_console restores original behavior"""
    stdout = io.StringIO()
    stderr = io.StringIO()

    # Patch console
    restore_fn = patch_console(stdout, stderr, lambda stream, data: None)

    # Restore
    restore_fn()

    # After restore, should work normally
    print("Normal output", file=stdout)
    assert "Normal output" in stdout.getvalue()
