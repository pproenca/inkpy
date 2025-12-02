"""
App-level hooks for custom reconciler.

Provides use_app and use_input hooks that work with the custom reconciler.
These are simplified versions focused on the core functionality needed
for interactive terminal applications.
"""

import contextlib
import os
import select
import sys
import termios
import threading
import tty
from typing import Any, Callable, Optional

from inkpy.input.keypress import NON_ALPHANUMERIC_KEYS, Key, parse_keypress
from inkpy.reconciler.hooks import Context, create_context, use_effect, use_ref

# App context for exit functionality
AppContext: Context[dict[str, Any]] = create_context(
    {
        "exit": lambda error=None: None,
    }
)

# Stdin context for input handling
StdinContext: Context[dict[str, Any]] = create_context(
    {
        "stdin": sys.stdin,
        "set_raw_mode": lambda mode: None,
        "internal_exitOnCtrlC": True,
    }
)

# Global storage for app state (workaround until full context is implemented)
_app_state = {
    "exit_callback": None,
    "stdin": sys.stdin,
    "raw_mode": False,
    "exit_on_ctrl_c": True,
    "input_handlers": [],
    "input_thread": None,
    "running": False,
    "_old_terminal_settings": None,
    "_terminal_fd": None,
}


def set_app_exit_callback(callback: Callable[[Optional[Exception]], None]):
    """Set the app exit callback (called by Ink when using custom reconciler)"""
    _app_state["exit_callback"] = callback


def set_app_stdin(stdin):
    """Set the stdin stream (called by Ink when using custom reconciler)"""
    _app_state["stdin"] = stdin


def set_app_exit_on_ctrl_c(value: bool):
    """Set exit on Ctrl+C behavior"""
    _app_state["exit_on_ctrl_c"] = value


def _start_input_thread():
    """Start background thread for reading input"""
    if _app_state["running"]:
        return

    _app_state["running"] = True

    def read_input():
        stdin = _app_state["stdin"]

        # Get file descriptor - handle pytest's captured stdin which has fileno()
        # but raises UnsupportedOperation when called
        try:
            fd = stdin.fileno() if hasattr(stdin, "fileno") else None
        except OSError:
            # stdin is a pseudo-file (pytest capture, StringIO, etc.)
            fd = None

        if fd is None:
            return

        # Check if stdin is a TTY - if not, input won't work
        if not os.isatty(fd):
            return

        old_settings = None
        try:
            # Save terminal settings for raw mode
            old_settings = termios.tcgetattr(fd)
            _app_state["_old_terminal_settings"] = old_settings
            _app_state["_terminal_fd"] = fd
            tty.setraw(fd)
            _app_state["raw_mode"] = True

            while _app_state["running"]:
                # Check if input is available (with timeout)
                # Use fd directly for select for consistency
                if select.select([fd], [], [], 0.1)[0]:
                    # Use os.read for unbuffered read (important in raw mode!)
                    data = os.read(fd, 1)
                    if data:
                        # Read any additional available bytes (for escape sequences)
                        while select.select([fd], [], [], 0)[0]:
                            extra = os.read(fd, 1)
                            if extra:
                                data += extra
                            else:
                                break

                        # Temporarily restore terminal for processing
                        # (handlers may trigger renders which need normal terminal mode)
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                        _app_state["raw_mode"] = False

                        try:
                            # Process input (decode bytes to string)
                            _process_input(data.decode("utf-8", errors="replace"))
                        finally:
                            # Re-enable raw mode for next input
                            if _app_state["running"]:
                                tty.setraw(fd)
                                _app_state["raw_mode"] = True
        except Exception:
            pass
        finally:
            # Restore terminal settings
            if old_settings is not None:
                with contextlib.suppress(Exception):
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            _app_state["raw_mode"] = False
            _app_state["_old_terminal_settings"] = None
            _app_state["_terminal_fd"] = None

    thread = threading.Thread(target=read_input, daemon=True)
    thread.start()
    _app_state["input_thread"] = thread


def _stop_input_thread():
    """Stop the input reading thread"""
    _app_state["running"] = False


def _process_input(data: str):
    """Process input and call handlers"""
    keypress = parse_keypress(data)

    # Build Key object
    key = Key(
        name=keypress.name,
        ctrl=keypress.ctrl,
        shift=keypress.shift,
        meta=keypress.meta or keypress.name == "escape" or keypress.option,
        option=keypress.option,
        sequence=keypress.sequence,
        raw=keypress.raw,
        code=keypress.code,
    )

    # Determine input string
    input_str = (keypress.ctrl and keypress.name) or keypress.sequence

    # Strip meta prefix if present
    if input_str.startswith("\u001b"):
        input_str = input_str[1:]

    # Empty string for non-alphanumeric keys
    if keypress.name in NON_ALPHANUMERIC_KEYS:
        input_str = ""

    # Detect shift for uppercase letters
    if len(input_str) == 1 and isinstance(input_str, str) and input_str.isupper():
        key.shift = True

    # Handle Ctrl+C
    if input_str == "c" and key.ctrl:
        if _app_state["exit_on_ctrl_c"] and _app_state["exit_callback"]:
            _app_state["exit_callback"](None)
            return

    # Call all registered handlers
    for handler in _app_state["input_handlers"][:]:
        with contextlib.suppress(Exception):
            handler(input_str, key)


class UseAppResult:
    """Result object from use_app hook"""

    def exit(self, error: Optional[Exception] = None):
        """Exit the application"""
        if _app_state["exit_callback"]:
            _app_state["exit_callback"](error)


def use_app() -> UseAppResult:
    """
    Hook that provides access to app-level functionality.

    Returns:
        Object with 'exit' method to exit the app

    Example:
        @component
        def App():
            app = use_app()

            def handle_quit():
                app.exit()

            return Text("Press 'q' to quit")
    """
    return UseAppResult()


def use_input(handler: Callable[[str, Key], None], is_active: bool = True) -> None:
    """
    Hook for handling keyboard input.

    Args:
        handler: Callback function (input_str: str, key: Key) -> None
        is_active: Enable/disable input handling

    Example:
        @component
        def App():
            selected, set_selected = use_state(0)

            def handle_input(input_str, key):
                if key.up_arrow:
                    set_selected(lambda s: max(0, s - 1))
                elif key.down_arrow:
                    set_selected(lambda s: s + 1)

            use_input(handle_input)
            return Text(f"Selected: {selected}")
    """
    # Use a ref to always call the latest handler
    # This avoids stale closure issues where old handler is called
    # even after component re-renders with new state
    handler_ref = use_ref(handler)

    # Update the ref to latest handler on every render
    handler_ref.current = handler

    def setup_input():
        if not is_active:
            return None

        # Create a stable wrapper that always calls the latest handler
        def stable_wrapper(input_str, key):
            handler_ref.current(input_str, key)

        # Register the stable wrapper (not the handler itself)
        _app_state["input_handlers"].append(stable_wrapper)

        # Start input thread if not running
        _start_input_thread()

        # Cleanup function
        def cleanup():
            if stable_wrapper in _app_state["input_handlers"]:
                _app_state["input_handlers"].remove(stable_wrapper)

        return cleanup

    use_effect(setup_input, [is_active])
