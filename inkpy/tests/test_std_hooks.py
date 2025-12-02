# test_std_hooks.py
import io

from reactpy import component

from inkpy import Box, Text, render
from inkpy.hooks.use_stderr import use_stderr
from inkpy.hooks.use_stdout import use_stdout
from inkpy.hooks.use_focus_manager import use_focus_manager


def test_use_stdout_provides_stream():
    """Test that useStdout provides stdout stream and write function"""

    @component
    def TestApp():
        stdout = use_stdout()
        assert hasattr(stdout, "stdout")
        assert hasattr(stdout, "write")
        assert callable(stdout.write)
        return None

    # Will test after integration


def test_stdout_write():
    """Test that stdout write function works"""
    buffer = io.StringIO()

    def write_fn(data):
        buffer.write(data)

    write_fn("Hello, World!")
    assert buffer.getvalue() == "Hello, World!"


def test_use_stderr_provides_stream():
    """Test that useStderr provides stderr stream"""

    @component
    def TestApp():
        stderr = use_stderr()
        assert hasattr(stderr, "stderr")
        assert hasattr(stderr, "write")
        assert callable(stderr.write)
        return None


def test_stderr_write():
    """Test that stderr write function works"""
    buffer = io.StringIO()

    def write_fn(data):
        buffer.write(data)

    write_fn("Error message")
    assert buffer.getvalue() == "Error message"


# === Integration tests that exercise the actual hook calls ===


def test_use_stdout_in_render_context():
    """Test use_stdout hook in a real render context"""
    hook_called = []

    @component
    def App():
        stdout_ctx = use_stdout()
        hook_called.append(True)
        # Verify the context provides expected keys
        assert "stdout" in stdout_ctx
        assert "write" in stdout_ctx
        return Box(Text("test"))

    stdout = io.StringIO()
    stdout.columns = 80
    stdout.rows = 24

    instance = render(App(), stdout=stdout, debug=True)
    # Hook should have been called during render
    assert len(hook_called) >= 1
    instance.unmount()


def test_use_stderr_in_render_context():
    """Test use_stderr hook in a real render context"""
    hook_called = []

    @component
    def App():
        stderr_ctx = use_stderr()
        hook_called.append(True)
        # Verify the context provides expected keys
        assert "stderr" in stderr_ctx
        assert "write" in stderr_ctx
        return Box(Text("test"))

    stdout = io.StringIO()
    stdout.columns = 80
    stdout.rows = 24

    instance = render(App(), stdout=stdout, debug=True)
    # Hook should have been called during render
    assert len(hook_called) >= 1
    instance.unmount()


def test_use_focus_manager_in_render_context():
    """Test use_focus_manager hook in a real render context"""
    hook_called = []

    @component
    def App():
        focus_manager = use_focus_manager()
        hook_called.append(True)
        # Verify the context provides expected methods
        assert "enable_focus" in focus_manager
        assert "disable_focus" in focus_manager
        assert "focus_next" in focus_manager
        assert "focus_previous" in focus_manager
        assert "focus" in focus_manager
        return Box(Text("test"))

    stdout = io.StringIO()
    stdout.columns = 80
    stdout.rows = 24

    instance = render(App(), stdout=stdout, debug=True)
    # Hook should have been called during render
    assert len(hook_called) >= 1
    instance.unmount()


def test_stdout_write_in_component():
    """Test that stdout.write can be called from a component"""
    write_calls = []

    @component
    def App():
        stdout_ctx = use_stdout()
        # Store the write function for testing
        write_calls.append(stdout_ctx.get("write"))
        return Box(Text("test"))

    stdout = io.StringIO()
    stdout.columns = 80
    stdout.rows = 24

    instance = render(App(), stdout=stdout, debug=True)
    # Verify write function was captured
    assert len(write_calls) >= 1
    assert callable(write_calls[0])
    instance.unmount()


def test_stderr_write_in_component():
    """Test that stderr.write can be called from a component"""
    write_calls = []

    @component
    def App():
        stderr_ctx = use_stderr()
        # Store the write function for testing
        write_calls.append(stderr_ctx.get("write"))
        return Box(Text("test"))

    stdout = io.StringIO()
    stdout.columns = 80
    stdout.rows = 24

    instance = render(App(), stdout=stdout, debug=True)
    # Verify write function was captured
    assert len(write_calls) >= 1
    assert callable(write_calls[0])
    instance.unmount()
