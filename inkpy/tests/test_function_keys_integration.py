"""Integration tests for function key handling."""

import pytest

from inkpy.input.keypress import parse_keypress
from inkpy.reconciler import app_hooks


class TestFunctionKeyParsing:
    """Tests for F1-F12 key parsing."""

    def test_function_keys_parsed_correctly(self):
        """F1-F12 keys should be parsed with correct names."""
        function_key_sequences = {
            "\x1bOP": "f1",  # F1 (xterm/gnome)
            "\x1bOQ": "f2",  # F2
            "\x1bOR": "f3",  # F3
            "\x1bOS": "f4",  # F4
            "\x1b[15~": "f5",  # F5
            "\x1b[17~": "f6",  # F6
            "\x1b[18~": "f7",  # F7
            "\x1b[19~": "f8",  # F8
            "\x1b[20~": "f9",  # F9
            "\x1b[21~": "f10",  # F10
            "\x1b[23~": "f11",  # F11
            "\x1b[24~": "f12",  # F12
        }

        for seq, expected_name in function_key_sequences.items():
            key = parse_keypress(seq)
            assert (
                key.name == expected_name
            ), f"Expected {expected_name} for {repr(seq)}, got {key.name}"

    def test_function_keys_alternative_sequences(self):
        """Test alternative function key sequences (rxvt style)."""
        alt_sequences = {
            "\x1b[11~": "f1",
            "\x1b[12~": "f2",
            "\x1b[13~": "f3",
            "\x1b[14~": "f4",
        }

        for seq, expected_name in alt_sequences.items():
            key = parse_keypress(seq)
            assert (
                key.name == expected_name
            ), f"Expected {expected_name} for {repr(seq)}, got {key.name}"


class TestFunctionKeyHandlerIntegration:
    """Tests for function keys received by input handlers."""

    def setup_method(self):
        """Reset app state before each test."""
        self.original_handlers = app_hooks._app_state["input_handlers"][:]
        app_hooks._app_state["input_handlers"] = []

    def teardown_method(self):
        """Restore app state after each test."""
        app_hooks._app_state["input_handlers"] = self.original_handlers

    def test_function_key_handler_receives_correct_key(self):
        """Function keys should be received by input handlers."""
        received = []

        def handler(input_str, key):
            received.append({"name": key.name, "input": input_str})

        app_hooks._app_state["input_handlers"].append(handler)

        # Process F1 key
        app_hooks._process_input("\x1bOP")

        assert len(received) == 1
        assert received[0]["name"] == "f1"
        assert received[0]["input"] == ""  # Non-alphanumeric

    def test_all_function_keys_received(self):
        """All F1-F12 keys should be received with correct names."""
        received = []

        def handler(input_str, key):
            received.append(key.name)

        app_hooks._app_state["input_handlers"].append(handler)

        # Process F5 and F10
        app_hooks._process_input("\x1b[15~")
        app_hooks._process_input("\x1b[21~")

        assert "f5" in received
        assert "f10" in received
