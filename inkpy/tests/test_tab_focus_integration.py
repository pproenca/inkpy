"""Integration tests for Tab key focus navigation."""

import pytest

from inkpy.reconciler import app_hooks
from inkpy.reconciler.focus_hooks import (
    _focus_next,
    _focus_previous,
    get_focus_state,
    reset_focus_state,
)


class TestTabFocusNavigation:
    """Tests for Tab and Shift+Tab focus navigation."""

    def setup_method(self):
        """Reset state before each test."""
        reset_focus_state()
        self.original_handlers = app_hooks._app_state["input_handlers"][:]
        self.original_running = app_hooks._app_state["running"]
        app_hooks._app_state["input_handlers"] = []
        app_hooks._app_state["running"] = False

    def teardown_method(self):
        """Restore state after each test."""
        app_hooks._app_state["input_handlers"] = self.original_handlers
        app_hooks._app_state["running"] = self.original_running
        reset_focus_state()

    def test_tab_key_triggers_focus_next(self):
        """Tab key should trigger focus_next when input handler wires it."""
        # Register focusables manually (simulating what use_focus does during render)
        from inkpy.reconciler.focus_hooks import _add_focusable, _focus

        _add_focusable("item1", {"auto_focus": True})
        _add_focusable("item2", {"auto_focus": False})
        _add_focusable("item3", {"auto_focus": False})

        # Verify initial state (item1 should be auto-focused)
        state = get_focus_state()
        assert state["active_id"] == "item1", f"Expected item1, got {state['active_id']}"

        # Register input handler that wires Tab to focus_next
        def tab_handler(input_str, key):
            if key.name == "tab":
                _focus_next()

        app_hooks._app_state["input_handlers"].append(tab_handler)

        # Simulate Tab key (Tab is \t or \x09)
        app_hooks._process_input("\t")

        # Verify focus moved to next item
        state = get_focus_state()
        assert state["active_id"] == "item2", f"Expected item2, got {state['active_id']}"

    def test_tab_key_cycles_through_all_items(self):
        """Tab key should cycle through all focusable items."""
        from inkpy.reconciler.focus_hooks import _add_focusable

        _add_focusable("item1", {"auto_focus": True})
        _add_focusable("item2", {"auto_focus": False})
        _add_focusable("item3", {"auto_focus": False})

        # Register input handler that wires Tab to focus_next
        def tab_handler(input_str, key):
            if key.name == "tab":
                _focus_next()

        app_hooks._app_state["input_handlers"].append(tab_handler)

        # Tab 3 times to cycle through all items and back to first
        app_hooks._process_input("\t")  # item1 -> item2
        assert get_focus_state()["active_id"] == "item2"

        app_hooks._process_input("\t")  # item2 -> item3
        assert get_focus_state()["active_id"] == "item3"

        app_hooks._process_input("\t")  # item3 -> item1 (wrap around)
        assert get_focus_state()["active_id"] == "item1"

    def test_shift_tab_triggers_focus_previous(self):
        """Shift+Tab should trigger focus_previous on the focus manager."""
        from inkpy.reconciler.focus_hooks import _add_focusable, _focus

        _add_focusable("item1", {"auto_focus": False})
        _add_focusable("item2", {"auto_focus": False})
        _add_focusable("item3", {"auto_focus": False})

        # Set focus to item2
        _focus("item2")
        state = get_focus_state()
        assert state["active_id"] == "item2"

        # Register input handler that wires Shift+Tab to focus_previous
        # Shift+Tab sequence is ESC [ Z or simply check for shift+tab
        def shift_tab_handler(input_str, key):
            # Shift+Tab escape sequence \x1b[Z
            if key.sequence == "\x1b[Z" or (key.name == "tab" and key.shift):
                _focus_previous()

        app_hooks._app_state["input_handlers"].append(shift_tab_handler)

        # Simulate Shift+Tab (ESC [ Z is the standard sequence)
        app_hooks._process_input("\x1b[Z")

        # Verify focus moved to previous item
        state = get_focus_state()
        assert state["active_id"] == "item1", f"Expected item1, got {state['active_id']}"

    def test_shift_tab_cycles_backwards(self):
        """Shift+Tab should cycle backwards through focusable items."""
        from inkpy.reconciler.focus_hooks import _add_focusable, _focus

        _add_focusable("item1", {"auto_focus": False})
        _add_focusable("item2", {"auto_focus": False})
        _add_focusable("item3", {"auto_focus": False})

        # Start at item1
        _focus("item1")
        assert get_focus_state()["active_id"] == "item1"

        # Register handler
        def shift_tab_handler(input_str, key):
            if key.sequence == "\x1b[Z":
                _focus_previous()

        app_hooks._app_state["input_handlers"].append(shift_tab_handler)

        # Shift+Tab from item1 should wrap to item3
        app_hooks._process_input("\x1b[Z")
        assert (
            get_focus_state()["active_id"] == "item3"
        ), f"Expected item3 (wrap), got {get_focus_state()['active_id']}"

        # Shift+Tab again -> item2
        app_hooks._process_input("\x1b[Z")
        assert get_focus_state()["active_id"] == "item2"
