"""Integration tests for modifier key combinations."""

import pytest

from inkpy.input.keypress import parse_keypress
from inkpy.reconciler import app_hooks


class TestCtrlArrowKeys:
    """Tests for Ctrl+Arrow key combinations."""

    def test_ctrl_arrow_keys(self):
        """Ctrl+Arrow should set both ctrl and arrow flags."""
        # Ctrl+Up: ESC [ 1 ; 5 A
        key = parse_keypress("\x1b[1;5A")
        assert key.ctrl is True
        assert key.up_arrow is True

        # Ctrl+Down: ESC [ 1 ; 5 B
        key = parse_keypress("\x1b[1;5B")
        assert key.ctrl is True
        assert key.down_arrow is True

        # Ctrl+Right: ESC [ 1 ; 5 C
        key = parse_keypress("\x1b[1;5C")
        assert key.ctrl is True
        assert key.right_arrow is True

        # Ctrl+Left: ESC [ 1 ; 5 D
        key = parse_keypress("\x1b[1;5D")
        assert key.ctrl is True
        assert key.left_arrow is True


class TestAltArrowKeys:
    """Tests for Alt+Arrow (meta) key combinations."""

    def test_alt_arrow_keys(self):
        """Alt+Arrow (meta) should set meta and arrow flags."""
        # Alt+Up (some terminals): ESC [ 1 ; 3 A
        key = parse_keypress("\x1b[1;3A")
        assert key.meta is True
        assert key.up_arrow is True

        # Alt+Down
        key = parse_keypress("\x1b[1;3B")
        assert key.meta is True
        assert key.down_arrow is True


class TestShiftArrowKeys:
    """Tests for Shift+Arrow key combinations."""

    def test_shift_arrow_keys(self):
        """Shift+Arrow should set shift and arrow flags."""
        # Shift+Up: ESC [ 1 ; 2 A
        key = parse_keypress("\x1b[1;2A")
        assert key.shift is True
        assert key.up_arrow is True

        # Shift+Down
        key = parse_keypress("\x1b[1;2B")
        assert key.shift is True
        assert key.down_arrow is True

        # Shift+Right
        key = parse_keypress("\x1b[1;2C")
        assert key.shift is True
        assert key.right_arrow is True


class TestRxvtModifiers:
    """Tests for rxvt-style modifier sequences."""

    def test_rxvt_shift_arrows(self):
        """rxvt-style shift+arrow sequences should be parsed correctly."""
        # [a, [b, [c, [d are shift+arrows in rxvt
        key = parse_keypress("\x1b[a")
        assert key.shift is True
        assert key.name == "up"

        key = parse_keypress("\x1b[b")
        assert key.shift is True
        assert key.name == "down"

    def test_rxvt_ctrl_arrows(self):
        """rxvt-style ctrl+arrow sequences should be parsed correctly."""
        # Oa, Ob, Oc, Od are ctrl+arrows in rxvt
        key = parse_keypress("\x1bOa")
        assert key.ctrl is True
        assert key.name == "up"

        key = parse_keypress("\x1bOb")
        assert key.ctrl is True
        assert key.name == "down"


class TestModifierHandlerIntegration:
    """Tests for modifier keys received by input handlers."""

    def setup_method(self):
        """Reset app state before each test."""
        self.original_handlers = app_hooks._app_state["input_handlers"][:]
        app_hooks._app_state["input_handlers"] = []

    def teardown_method(self):
        """Restore app state after each test."""
        app_hooks._app_state["input_handlers"] = self.original_handlers

    def test_ctrl_arrow_received_by_handler(self):
        """Ctrl+Arrow should be received with both flags set."""
        received = []

        def handler(input_str, key):
            received.append(
                {
                    "ctrl": key.ctrl,
                    "up_arrow": key.up_arrow,
                    "name": key.name,
                }
            )

        app_hooks._app_state["input_handlers"].append(handler)

        # Process Ctrl+Up
        app_hooks._process_input("\x1b[1;5A")

        assert len(received) == 1
        assert received[0]["ctrl"] is True
        assert received[0]["up_arrow"] is True
        assert received[0]["name"] == "up"

    def test_combined_modifiers(self):
        """Combined modifiers (Ctrl+Shift) should be detected."""
        # Ctrl+Shift+Up: ESC [ 1 ; 6 A (6 = ctrl(4) + shift(2) - 1 + 1)
        key = parse_keypress("\x1b[1;6A")
        assert key.ctrl is True
        assert key.shift is True
        assert key.up_arrow is True
