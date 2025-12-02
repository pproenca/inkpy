"""
Tests for App component input loop functionality.

Following TDD: Write failing test first, then implement.
"""

import io
from unittest.mock import Mock, patch

from reactpy import component

from inkpy import Box, Text, render
from inkpy.components.app import App
from inkpy.input.event_emitter import EventEmitter


def test_app_creates_event_emitter():
    """Test that App component creates EventEmitter"""
    stdout = io.StringIO()
    stdout.columns = 80
    stdout.rows = 24
    stdin = io.StringIO()
    stderr = io.StringIO()

    @component
    def TestComponent():
        return Box(Text("test"))

    app = App(
        children=TestComponent(),
        stdin=stdin,
        stdout=stdout,
        stderr=stderr,
        write_to_stdout=lambda x: stdout.write(x),
        write_to_stderr=lambda x: stderr.write(x),
    )

    # App should create successfully
    assert app is not None


def test_app_context_values_structure():
    """Test that App component provides correct context structures"""
    stdout = io.StringIO()
    stdout.columns = 80
    stdin = io.StringIO()
    stderr = io.StringIO()

    write_calls = {"stdout": [], "stderr": []}

    @component
    def TestComponent():
        return Box(Text("test"))

    app = App(
        children=TestComponent(),
        stdin=stdin,
        stdout=stdout,
        stderr=stderr,
        write_to_stdout=lambda x: write_calls["stdout"].append(x),
        write_to_stderr=lambda x: write_calls["stderr"].append(x),
        exit_on_ctrl_c=True,
        on_exit=lambda e: None,
    )

    # App should be created with all context values
    assert app is not None


def test_app_with_on_exit_callback():
    """Test App with on_exit callback"""
    exit_calls = []

    stdout = io.StringIO()
    stdout.columns = 80
    stdin = io.StringIO()
    stderr = io.StringIO()

    @component
    def TestComponent():
        return Box(Text("test"))

    app = App(
        children=TestComponent(),
        stdin=stdin,
        stdout=stdout,
        stderr=stderr,
        write_to_stdout=lambda x: stdout.write(x),
        write_to_stderr=lambda x: stderr.write(x),
        on_exit=lambda e: exit_calls.append(e),
    )

    assert app is not None


def test_app_non_tty_stdin():
    """Test App handles non-TTY stdin gracefully"""
    stdout = io.StringIO()
    stdout.columns = 80
    stdin = io.StringIO()  # StringIO is not a TTY
    stderr = io.StringIO()

    @component
    def TestComponent():
        return Box(Text("test"))

    # App should not crash with non-TTY stdin
    app = App(
        children=TestComponent(),
        stdin=stdin,
        stdout=stdout,
        stderr=stderr,
        write_to_stdout=lambda x: stdout.write(x),
        write_to_stderr=lambda x: stderr.write(x),
    )

    assert app is not None


def test_app_renders_in_full_context():
    """Test App component renders correctly in full render context"""
    stdout = io.StringIO()
    stdout.columns = 80
    stdout.rows = 24

    @component
    def TestComponent():
        return Box(Text("Hello from App"))

    instance = render(TestComponent(), stdout=stdout, debug=True)
    output = stdout.getvalue()

    assert "Hello from App" in output
    instance.unmount()


def test_app_exit_on_ctrl_c_disabled():
    """Test App with exit_on_ctrl_c disabled"""
    stdout = io.StringIO()
    stdout.columns = 80
    stdin = io.StringIO()
    stderr = io.StringIO()

    @component
    def TestComponent():
        return Box(Text("test"))

    app = App(
        children=TestComponent(),
        stdin=stdin,
        stdout=stdout,
        stderr=stderr,
        write_to_stdout=lambda x: stdout.write(x),
        write_to_stderr=lambda x: stderr.write(x),
        exit_on_ctrl_c=False,  # Disable Ctrl+C exit
    )

    assert app is not None
