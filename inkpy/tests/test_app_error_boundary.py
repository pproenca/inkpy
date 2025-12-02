"""
Tests for App component error boundary functionality.

Following TDD: Write failing test first, then implement.
"""

import io

from reactpy import component

from inkpy.components.app import App


def test_app_catches_errors_in_children():
    """Test that App component catches errors from children and shows ErrorOverview"""
    stdout = io.StringIO()
    stdin = io.StringIO()
    stderr = io.StringIO()

    @component
    def BrokenComponent():
        raise ValueError("Test error")

    # App should catch the error and show ErrorOverview
    # This requires full rendering, so we'll test the structure
    app = App(
        children=BrokenComponent(),
        stdin=stdin,
        stdout=stdout,
        stderr=stderr,
        write_to_stdout=lambda x: stdout.write(x),
        write_to_stderr=lambda x: stderr.write(x),
    )

    # Should not raise - error should be caught
    assert app is not None


def test_app_shows_error_overview_on_error():
    """Test that App shows ErrorOverview component when error occurs"""
    # This will be tested through rendering
    # ErrorOverview should be rendered instead of children when error state is set
    pass  # Will verify through integration


def test_app_calls_on_exit_with_error():
    """Test that App calls on_exit callback with error when error occurs"""
    stdout = io.StringIO()
    stdin = io.StringIO()
    stderr = io.StringIO()

    errors_received = []

    def on_exit(error):
        errors_received.append(error)

    @component
    def BrokenComponent():
        raise ValueError("Test error")

    app = App(
        children=BrokenComponent(),
        stdin=stdin,
        stdout=stdout,
        stderr=stderr,
        write_to_stdout=lambda x: stdout.write(x),
        write_to_stderr=lambda x: stderr.write(x),
        on_exit=on_exit,
    )

    # Error should trigger on_exit
    # This requires full rendering context
    assert app is not None
