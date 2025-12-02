"""Integration tests for focus and input combined workflows."""

import pytest

from inkpy.reconciler import app_hooks
from inkpy.reconciler.focus_hooks import (
    _add_focusable,
    _focus,
    _focus_next,
    get_focus_state,
    reset_focus_state,
)


class TestFocusedComponentInput:
    """Tests for focus and input working together."""

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

    def test_focused_component_handles_input(self):
        """Only the focused component should handle specific input."""
        # Simulate two focusable components
        _add_focusable("comp1", {"auto_focus": True})
        _add_focusable("comp2", {"auto_focus": False})

        component_inputs = {"comp1": [], "comp2": []}

        # Register handlers that check focus state
        def comp1_handler(input_str, key):
            if get_focus_state()["active_id"] == "comp1":
                component_inputs["comp1"].append(input_str)

        def comp2_handler(input_str, key):
            if get_focus_state()["active_id"] == "comp2":
                component_inputs["comp2"].append(input_str)

        app_hooks._app_state["input_handlers"].append(comp1_handler)
        app_hooks._app_state["input_handlers"].append(comp2_handler)

        # Process input while comp1 is focused
        app_hooks._process_input("a")
        app_hooks._process_input("b")

        # Only comp1 should receive input
        assert component_inputs["comp1"] == ["a", "b"]
        assert component_inputs["comp2"] == []

        # Switch focus to comp2
        _focus("comp2")
        assert get_focus_state()["active_id"] == "comp2"

        # Now comp2 should receive input
        app_hooks._process_input("c")
        assert component_inputs["comp2"] == ["c"]
        # comp1 should not receive new input
        assert component_inputs["comp1"] == ["a", "b"]

    def test_enter_key_triggers_focused_action(self):
        """Enter key should trigger action on focused component."""
        actions_triggered = []

        _add_focusable("opt1", {"auto_focus": True})
        _add_focusable("opt2", {"auto_focus": False})

        def handler(input_str, key):
            if key.return_:
                focused = get_focus_state()["active_id"]
                actions_triggered.append(focused)

        app_hooks._app_state["input_handlers"].append(handler)

        # Simulate Enter key on first item (auto-focused)
        app_hooks._process_input("\r")

        assert "opt1" in actions_triggered

        # Move focus and trigger Enter again
        _focus("opt2")
        app_hooks._process_input("\r")

        assert actions_triggered == ["opt1", "opt2"]

    def test_arrow_keys_navigate_and_select(self):
        """Arrow keys should navigate, Enter should select."""
        _add_focusable("menu1", {"auto_focus": True})
        _add_focusable("menu2", {"auto_focus": False})
        _add_focusable("menu3", {"auto_focus": False})

        selections = []

        def handler(input_str, key):
            if key.down_arrow:
                _focus_next()
            elif key.return_:
                selections.append(get_focus_state()["active_id"])

        app_hooks._app_state["input_handlers"].append(handler)

        # Start at menu1
        assert get_focus_state()["active_id"] == "menu1"

        # Navigate down twice
        app_hooks._process_input("\x1b[B")  # Down arrow
        assert get_focus_state()["active_id"] == "menu2"

        app_hooks._process_input("\x1b[B")  # Down arrow
        assert get_focus_state()["active_id"] == "menu3"

        # Select
        app_hooks._process_input("\r")  # Enter
        assert selections == ["menu3"]

    def test_escape_cancels_focus(self):
        """Escape key should be detectable to cancel operations."""
        _add_focusable("item1", {"auto_focus": True})

        escaped = []

        def handler(input_str, key):
            if key.escape:
                escaped.append(True)

        app_hooks._app_state["input_handlers"].append(handler)

        # Press Escape
        app_hooks._process_input("\x1b")

        assert len(escaped) == 1

    def test_space_key_toggles_focused_item(self):
        """Space key should toggle the focused item."""
        _add_focusable("checkbox1", {"auto_focus": True})
        _add_focusable("checkbox2", {"auto_focus": False})

        toggled = []

        def handler(input_str, key):
            if key.name == "space":
                toggled.append(get_focus_state()["active_id"])

        app_hooks._app_state["input_handlers"].append(handler)

        # Toggle checkbox1
        app_hooks._process_input(" ")
        assert toggled == ["checkbox1"]

        # Move focus and toggle checkbox2
        _focus("checkbox2")
        app_hooks._process_input(" ")
        assert toggled == ["checkbox1", "checkbox2"]


class TestMultiStepFocusFlow:
    """Tests for multi-step focus workflows."""

    def setup_method(self):
        """Reset state before each test."""
        reset_focus_state()
        self.original_handlers = app_hooks._app_state["input_handlers"][:]
        app_hooks._app_state["input_handlers"] = []

    def teardown_method(self):
        """Restore state after each test."""
        app_hooks._app_state["input_handlers"] = self.original_handlers
        reset_focus_state()

    def test_form_navigation_workflow(self):
        """Simulate form navigation: Tab between fields, Enter to submit."""
        _add_focusable("username", {"auto_focus": True})
        _add_focusable("password", {"auto_focus": False})
        _add_focusable("submit", {"auto_focus": False})

        form_state = {"current_field": "username", "submitted": False}

        def handler(input_str, key):
            if key.name == "tab":
                _focus_next()
                form_state["current_field"] = get_focus_state()["active_id"]
            elif key.return_ and get_focus_state()["active_id"] == "submit":
                form_state["submitted"] = True

        app_hooks._app_state["input_handlers"].append(handler)

        # Navigate through form
        assert form_state["current_field"] == "username"

        app_hooks._process_input("\t")  # Tab
        assert form_state["current_field"] == "password"

        app_hooks._process_input("\t")  # Tab
        assert form_state["current_field"] == "submit"

        # Submit
        app_hooks._process_input("\r")
        assert form_state["submitted"] is True
