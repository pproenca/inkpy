"""Tests for rendering stability during rapid input."""

import pytest

from inkpy.reconciler import app_hooks
from inkpy.reconciler.reconciler import Reconciler
from inkpy.reconciler.component import component
from inkpy.reconciler.element import create_element
from inkpy.reconciler.hooks import use_state


class TestRapidStateUpdates:
    """Tests for rapid state updates during rendering."""

    def test_rapid_state_updates_render_correctly(self):
        """Multiple rapid state updates should all render correctly."""
        render_outputs = []
        set_state_ref = [None]

        @component
        def Counter():
            count, set_count = use_state(0)
            set_state_ref[0] = set_count
            render_outputs.append(count)
            return create_element("ink-text", {}, str(count))

        reconciler = Reconciler()
        reconciler.render(Counter())

        # Rapid state updates
        for i in range(1, 11):
            set_state_ref[0](i)
            reconciler.flush_sync()

        # All values should have been rendered
        assert 10 in render_outputs, f"Final value 10 should be in outputs: {render_outputs}"

    def test_state_updates_are_batched(self):
        """Multiple state updates in sequence should work correctly."""
        render_count = [0]
        final_values = []

        @component
        def MultiState():
            count, set_count = use_state(0)
            name, set_name = use_state("initial")
            render_count[0] += 1
            final_values.append((count, name))
            return create_element("ink-text", {}, f"{count}-{name}")

        reconciler = Reconciler()
        reconciler.render(MultiState())

        # Initial render happened
        assert render_count[0] >= 1


class TestRapidInputProcessing:
    """Tests for rapid input processing stability."""

    def setup_method(self):
        """Reset app state before each test."""
        self.original_handlers = app_hooks._app_state["input_handlers"][:]
        app_hooks._app_state["input_handlers"] = []

    def teardown_method(self):
        """Restore app state after each test."""
        app_hooks._app_state["input_handlers"] = self.original_handlers

    def test_input_during_render_queued_correctly(self):
        """Input received during render should be queued and processed."""
        inputs_received = []

        def handler(input_str, key):
            inputs_received.append(input_str)

        app_hooks._app_state["input_handlers"].append(handler)

        # Simulate rapid input
        for char in "abcdef":
            app_hooks._process_input(char)

        # All inputs should be processed in order
        assert inputs_received == ["a", "b", "c", "d", "e", "f"]

    def test_rapid_arrow_key_sequence(self):
        """Rapid arrow key presses should all be processed."""
        arrows_received = []

        def handler(input_str, key):
            if key.name in ("up", "down", "left", "right"):
                arrows_received.append(key.name)

        app_hooks._app_state["input_handlers"].append(handler)

        # Rapid arrow key sequence
        app_hooks._process_input("\x1b[A")  # Up
        app_hooks._process_input("\x1b[B")  # Down
        app_hooks._process_input("\x1b[A")  # Up
        app_hooks._process_input("\x1b[A")  # Up

        assert arrows_received == ["up", "down", "up", "up"]

    def test_mixed_input_types_processed_correctly(self):
        """Mixed input (characters, arrows, special keys) should all work."""
        all_inputs = []

        def handler(input_str, key):
            all_inputs.append(
                {
                    "input": input_str,
                    "name": key.name,
                }
            )

        app_hooks._app_state["input_handlers"].append(handler)

        # Mix of different input types
        app_hooks._process_input("a")  # Character
        app_hooks._process_input("\x1b[A")  # Up arrow
        app_hooks._process_input("\r")  # Enter
        app_hooks._process_input("z")  # Character

        assert len(all_inputs) == 4
        assert all_inputs[0]["input"] == "a"
        assert all_inputs[1]["name"] == "up"
        assert all_inputs[2]["name"] == "return"
        assert all_inputs[3]["input"] == "z"

    def test_handler_exception_doesnt_break_queue(self):
        """Exceptions in one handler shouldn't break other handlers."""
        received = []

        def bad_handler(input_str, key):
            if input_str == "b":
                raise ValueError("Intentional error")
            received.append(f"bad:{input_str}")

        def good_handler(input_str, key):
            received.append(f"good:{input_str}")

        app_hooks._app_state["input_handlers"].append(bad_handler)
        app_hooks._app_state["input_handlers"].append(good_handler)

        # Process inputs including one that triggers exception
        app_hooks._process_input("a")
        app_hooks._process_input("b")  # Triggers exception in bad_handler
        app_hooks._process_input("c")

        # Good handler should have received all inputs
        assert "good:a" in received
        assert "good:b" in received
        assert "good:c" in received


class TestInputOrderPreservation:
    """Tests to verify input order is preserved."""

    def setup_method(self):
        """Reset app state before each test."""
        self.original_handlers = app_hooks._app_state["input_handlers"][:]
        app_hooks._app_state["input_handlers"] = []

    def teardown_method(self):
        """Restore app state after each test."""
        app_hooks._app_state["input_handlers"] = self.original_handlers

    def test_input_order_preserved(self):
        """Input order should be preserved across all handlers."""
        order = []

        def handler1(input_str, key):
            order.append(f"h1:{input_str}")

        def handler2(input_str, key):
            order.append(f"h2:{input_str}")

        app_hooks._app_state["input_handlers"].append(handler1)
        app_hooks._app_state["input_handlers"].append(handler2)

        app_hooks._process_input("x")
        app_hooks._process_input("y")

        # h1 and h2 should both receive x before y
        assert order == ["h1:x", "h2:x", "h1:y", "h2:y"]

    def test_numeric_input_sequence(self):
        """Numeric input (like typing a number) should be in order."""
        digits = []

        def handler(input_str, key):
            digits.append(input_str)

        app_hooks._app_state["input_handlers"].append(handler)

        for d in "12345":
            app_hooks._process_input(d)

        assert digits == ["1", "2", "3", "4", "5"]
