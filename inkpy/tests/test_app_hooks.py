"""
Tests for app_hooks module - custom reconciler hooks for app-level functionality.
"""

import pytest
from unittest.mock import Mock

from inkpy.reconciler.app_hooks import (
    UseAppResult,
    _app_state,
    _process_input,
    set_app_exit_callback,
    set_app_exit_on_ctrl_c,
    set_app_stdin,
    use_app,
)
from inkpy.input.keypress import Key


class TestSetAppFunctions:
    """Tests for the set_app_* configuration functions"""

    def setup_method(self):
        """Reset app state before each test"""
        # Save original state
        self.original_exit_callback = _app_state["exit_callback"]
        self.original_stdin = _app_state["stdin"]
        self.original_exit_on_ctrl_c = _app_state["exit_on_ctrl_c"]

    def teardown_method(self):
        """Restore original state after each test"""
        _app_state["exit_callback"] = self.original_exit_callback
        _app_state["stdin"] = self.original_stdin
        _app_state["exit_on_ctrl_c"] = self.original_exit_on_ctrl_c

    def test_set_app_exit_callback(self):
        """Test setting exit callback"""
        mock_callback = Mock()
        set_app_exit_callback(mock_callback)

        assert _app_state["exit_callback"] == mock_callback

    def test_set_app_stdin(self):
        """Test setting stdin stream"""
        import io

        mock_stdin = io.StringIO()
        set_app_stdin(mock_stdin)

        assert _app_state["stdin"] == mock_stdin

    def test_set_app_exit_on_ctrl_c(self):
        """Test setting exit on Ctrl+C behavior"""
        set_app_exit_on_ctrl_c(True)
        assert _app_state["exit_on_ctrl_c"] is True

        set_app_exit_on_ctrl_c(False)
        assert _app_state["exit_on_ctrl_c"] is False


class TestUseApp:
    """Tests for use_app hook"""

    def setup_method(self):
        """Reset app state before each test"""
        self.original_exit_callback = _app_state["exit_callback"]

    def teardown_method(self):
        """Restore original state after each test"""
        _app_state["exit_callback"] = self.original_exit_callback

    def test_use_app_returns_result(self):
        """Test use_app returns UseAppResult"""
        result = use_app()
        assert isinstance(result, UseAppResult)

    def test_use_app_result_has_exit(self):
        """Test UseAppResult has exit method"""
        result = use_app()
        assert hasattr(result, "exit")
        assert callable(result.exit)

    def test_use_app_exit_calls_callback(self):
        """Test UseAppResult.exit calls the exit callback"""
        mock_callback = Mock()
        _app_state["exit_callback"] = mock_callback

        result = use_app()
        result.exit()

        mock_callback.assert_called_once_with(None)

    def test_use_app_exit_with_error(self):
        """Test UseAppResult.exit passes error to callback"""
        mock_callback = Mock()
        _app_state["exit_callback"] = mock_callback

        error = ValueError("test error")
        result = use_app()
        result.exit(error)

        mock_callback.assert_called_once_with(error)

    def test_use_app_exit_no_callback(self):
        """Test UseAppResult.exit does nothing when no callback set"""
        _app_state["exit_callback"] = None

        result = use_app()
        # Should not raise
        result.exit()


class TestProcessInput:
    """Tests for _process_input function"""

    def setup_method(self):
        """Reset app state before each test"""
        self.original_handlers = _app_state["input_handlers"][:]
        self.original_exit_callback = _app_state["exit_callback"]
        self.original_exit_on_ctrl_c = _app_state["exit_on_ctrl_c"]
        _app_state["input_handlers"] = []

    def teardown_method(self):
        """Restore original state after each test"""
        _app_state["input_handlers"] = self.original_handlers
        _app_state["exit_callback"] = self.original_exit_callback
        _app_state["exit_on_ctrl_c"] = self.original_exit_on_ctrl_c

    def test_process_input_calls_handlers(self):
        """Test _process_input calls registered handlers"""
        received = []

        def handler(input_str, key):
            received.append((input_str, key.name))

        _app_state["input_handlers"].append(handler)

        _process_input("a")

        assert len(received) == 1
        assert received[0][0] == "a"

    def test_process_input_ctrl_c_exits(self):
        """Test Ctrl+C triggers exit when exit_on_ctrl_c is True"""
        mock_callback = Mock()
        _app_state["exit_callback"] = mock_callback
        _app_state["exit_on_ctrl_c"] = True

        _process_input("\x03")  # Ctrl+C

        mock_callback.assert_called_once_with(None)

    def test_process_input_ctrl_c_no_exit_when_disabled(self):
        """Test Ctrl+C doesn't exit when exit_on_ctrl_c is False"""
        mock_callback = Mock()
        _app_state["exit_callback"] = mock_callback
        _app_state["exit_on_ctrl_c"] = False

        _process_input("\x03")  # Ctrl+C

        # Callback should NOT be called
        mock_callback.assert_not_called()

    def test_process_input_uppercase_sets_shift(self):
        """Test uppercase letters set shift flag on Key"""
        received_keys = []

        def handler(input_str, key):
            received_keys.append(key)

        _app_state["input_handlers"].append(handler)

        _process_input("A")  # Uppercase A

        assert len(received_keys) == 1
        assert received_keys[0].shift is True

    def test_process_input_escape_sequence(self):
        """Test escape sequences are processed"""
        received = []

        def handler(input_str, key):
            received.append((input_str, key))

        _app_state["input_handlers"].append(handler)

        # Up arrow is \x1b[A
        _process_input("\x1b[A")

        assert len(received) == 1
        # Input should have escape stripped
        assert received[0][1].name == "up"

    def test_process_input_handler_exception_ignored(self):
        """Test exceptions in handlers are caught and ignored"""

        def bad_handler(input_str, key):
            raise ValueError("Handler error")

        received = []

        def good_handler(input_str, key):
            received.append(input_str)

        _app_state["input_handlers"].append(bad_handler)
        _app_state["input_handlers"].append(good_handler)

        # Should not raise
        _process_input("x")

        # Good handler should still be called
        assert "x" in received

    def test_process_input_with_meta_prefix(self):
        """Test input with meta/escape prefix is handled"""
        received = []

        def handler(input_str, key):
            received.append((input_str, key.meta))

        _app_state["input_handlers"].append(handler)

        _process_input("\x1ba")  # Meta-a

        assert len(received) == 1
        # Meta should be True for escape sequences
        assert received[0][1] is True


class TestKeyObject:
    """Tests for Key object created by _process_input"""

    def setup_method(self):
        """Reset app state before each test"""
        self.original_handlers = _app_state["input_handlers"][:]
        _app_state["input_handlers"] = []

    def teardown_method(self):
        """Restore original state after each test"""
        _app_state["input_handlers"] = self.original_handlers

    def test_key_has_required_attributes(self):
        """Test Key object has all required attributes"""
        received_key = None

        def handler(input_str, key):
            nonlocal received_key
            received_key = key

        _app_state["input_handlers"].append(handler)

        _process_input("a")

        assert received_key is not None
        assert hasattr(received_key, "name")
        assert hasattr(received_key, "ctrl")
        assert hasattr(received_key, "shift")
        assert hasattr(received_key, "meta")
        assert hasattr(received_key, "sequence")

    def test_key_ctrl_detection(self):
        """Test Ctrl key is detected"""
        received_key = None

        def handler(input_str, key):
            nonlocal received_key
            received_key = key

        _app_state["input_handlers"].append(handler)

        _process_input("\x01")  # Ctrl+A

        assert received_key is not None
        assert received_key.ctrl is True
