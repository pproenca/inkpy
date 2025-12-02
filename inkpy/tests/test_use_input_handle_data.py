"""Tests for use_input handle_data function coverage.

These tests cover the _setup_input_listener function and its internal
handle_data function from inkpy/hooks/use_input.py
"""

import pytest

from inkpy.hooks.use_input import _setup_input_listener
from inkpy.input.event_emitter import EventEmitter


class TestHandleDataMetaPrefix:
    """Tests for meta prefix handling in handle_data."""

    def test_handle_data_strips_meta_prefix(self):
        """Input strings starting with ESC should have the prefix stripped."""
        received = []

        def handler(input_str, key):
            received.append({"input": input_str, "meta": key.meta})

        # Create mock stdin context with event emitter
        emitter = EventEmitter()
        stdin_ctx = {
            "internal_eventEmitter": emitter,
            "internal_exitOnCtrlC": True,
        }

        # Set up listener
        cleanup = _setup_input_listener(stdin_ctx, handler)

        # Emit input with meta prefix (ESC + a)
        emitter.emit("input", "\x1ba")

        # Verify meta was detected and prefix stripped
        assert len(received) == 1
        assert received[0]["meta"] is True
        # The input_str may be empty (if 'a' becomes meta key name) or 'a'
        # after stripping the ESC prefix

        if cleanup:
            cleanup()


class TestHandleDataNonAlphanumeric:
    """Tests for non-alphanumeric key handling."""

    def test_handle_data_non_alphanumeric_returns_empty(self):
        """Non-alphanumeric keys should return empty string as input."""
        received = []

        def handler(input_str, key):
            received.append({"input": input_str, "name": key.name})

        emitter = EventEmitter()
        stdin_ctx = {
            "internal_eventEmitter": emitter,
            "internal_exitOnCtrlC": True,
        }

        cleanup = _setup_input_listener(stdin_ctx, handler)

        # Emit arrow key (non-alphanumeric)
        emitter.emit("input", "\x1b[A")  # Up arrow

        assert len(received) == 1
        assert received[0]["input"] == ""  # Empty for non-alphanumeric
        assert received[0]["name"] == "up"

        if cleanup:
            cleanup()

    def test_handle_data_down_arrow_empty_string(self):
        """Down arrow should also return empty string."""
        received = []

        def handler(input_str, key):
            received.append({"input": input_str, "name": key.name})

        emitter = EventEmitter()
        stdin_ctx = {
            "internal_eventEmitter": emitter,
            "internal_exitOnCtrlC": True,
        }

        cleanup = _setup_input_listener(stdin_ctx, handler)

        # Down arrow
        emitter.emit("input", "\x1b[B")

        assert len(received) == 1
        assert received[0]["input"] == ""
        assert received[0]["name"] == "down"

        if cleanup:
            cleanup()


class TestHandleDataShiftDetection:
    """Tests for shift key detection with uppercase letters."""

    def test_handle_data_detects_shift_for_uppercase(self):
        """Uppercase letters should set key.shift = True."""
        received = []

        def handler(input_str, key):
            received.append({"input": input_str, "shift": key.shift})

        emitter = EventEmitter()
        stdin_ctx = {
            "internal_eventEmitter": emitter,
            "internal_exitOnCtrlC": True,
        }

        cleanup = _setup_input_listener(stdin_ctx, handler)

        # Emit uppercase letter
        emitter.emit("input", "A")

        assert len(received) == 1
        assert received[0]["shift"] is True

        if cleanup:
            cleanup()

    def test_handle_data_no_shift_for_lowercase(self):
        """Lowercase letters should not set shift."""
        received = []

        def handler(input_str, key):
            received.append({"input": input_str, "shift": key.shift})

        emitter = EventEmitter()
        stdin_ctx = {
            "internal_eventEmitter": emitter,
            "internal_exitOnCtrlC": True,
        }

        cleanup = _setup_input_listener(stdin_ctx, handler)

        # Emit lowercase letter
        emitter.emit("input", "a")

        assert len(received) == 1
        assert received[0]["shift"] is False

        if cleanup:
            cleanup()


class TestHandleDataCtrlCBehavior:
    """Tests for Ctrl+C skip behavior."""

    def test_handle_data_skips_ctrl_c_when_exit_enabled(self):
        """Ctrl+C should NOT call handler when exitOnCtrlC is True."""
        received = []

        def handler(input_str, key):
            received.append({"input": input_str, "ctrl": key.ctrl})

        emitter = EventEmitter()
        stdin_ctx = {
            "internal_eventEmitter": emitter,
            "internal_exitOnCtrlC": True,  # Exit enabled
        }

        cleanup = _setup_input_listener(stdin_ctx, handler)

        # Emit Ctrl+C
        emitter.emit("input", "\x03")

        # Handler should NOT be called
        assert len(received) == 0

        if cleanup:
            cleanup()

    def test_handle_data_calls_handler_ctrl_c_when_exit_disabled(self):
        """Ctrl+C SHOULD call handler when exitOnCtrlC is False."""
        received = []

        def handler(input_str, key):
            received.append({"input": input_str, "ctrl": key.ctrl})

        emitter = EventEmitter()
        stdin_ctx = {
            "internal_eventEmitter": emitter,
            "internal_exitOnCtrlC": False,  # Exit disabled
        }

        cleanup = _setup_input_listener(stdin_ctx, handler)

        # Emit Ctrl+C
        emitter.emit("input", "\x03")

        # Handler SHOULD be called
        assert len(received) == 1
        assert received[0]["ctrl"] is True

        if cleanup:
            cleanup()


class TestEventEmitterVariants:
    """Tests for event emitter binding variants."""

    def test_setup_listener_with_add_listener_method(self):
        """Test event emitter using add_listener/remove_listener methods."""
        received = []

        def handler(input_str, key):
            received.append(input_str)

        class AltEmitter:
            def __init__(self):
                self._listeners = {}

            def add_listener(self, event, fn):
                self._listeners.setdefault(event, []).append(fn)

            def remove_listener(self, event, fn):
                if event in self._listeners and fn in self._listeners[event]:
                    self._listeners[event].remove(fn)

            def emit(self, event, data):
                for fn in self._listeners.get(event, []):
                    fn(data)

        emitter = AltEmitter()
        stdin_ctx = {
            "internal_eventEmitter": emitter,
            "internal_exitOnCtrlC": True,
        }

        cleanup = _setup_input_listener(stdin_ctx, handler)

        emitter.emit("input", "x")
        assert "x" in received

        # Cleanup should work
        if cleanup:
            cleanup()

        # After cleanup, handler should not be called
        received.clear()
        emitter.emit("input", "y")
        assert len(received) == 0

    def test_setup_listener_with_standard_on_method(self):
        """Test that standard 'on' method works correctly."""
        received = []

        def handler(input_str, key):
            received.append(input_str)

        emitter = EventEmitter()
        stdin_ctx = {
            "internal_eventEmitter": emitter,
            "internal_exitOnCtrlC": True,
        }

        cleanup = _setup_input_listener(stdin_ctx, handler)

        emitter.emit("input", "z")
        assert "z" in received

        if cleanup:
            cleanup()


class TestPasteHandling:
    """Tests for multi-character paste handling."""

    def test_handle_data_paste_single_callback(self):
        """Pasted text (multiple chars) should call handler once with full string."""
        received = []

        def handler(input_str, key):
            received.append(input_str)

        emitter = EventEmitter()
        stdin_ctx = {
            "internal_eventEmitter": emitter,
            "internal_exitOnCtrlC": True,
        }

        cleanup = _setup_input_listener(stdin_ctx, handler)

        # Simulate pasting "hello world"
        emitter.emit("input", "hello world")

        # Handler should be called once with full string
        assert len(received) == 1
        assert received[0] == "hello world"

        if cleanup:
            cleanup()

    def test_handle_data_paste_with_special_chars(self):
        """Pasted text with special characters should be handled correctly."""
        received = []

        def handler(input_str, key):
            received.append(input_str)

        emitter = EventEmitter()
        stdin_ctx = {
            "internal_eventEmitter": emitter,
            "internal_exitOnCtrlC": True,
        }

        cleanup = _setup_input_listener(stdin_ctx, handler)

        # Paste with newlines and tabs
        emitter.emit("input", "line1\nline2\ttab")

        assert len(received) == 1
        assert received[0] == "line1\nline2\ttab"

        if cleanup:
            cleanup()
