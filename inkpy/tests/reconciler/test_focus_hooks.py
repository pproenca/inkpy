# tests/reconciler/test_focus_hooks.py
"""Tests for use_focus hook in custom reconciler"""

from io import StringIO

import pytest


@pytest.fixture(autouse=True)
def reset_focus_state_before_each():
    """Reset focus state before each test to ensure isolation"""
    from inkpy.reconciler.focus_hooks import reset_focus_state

    reset_focus_state()
    yield
    reset_focus_state()


class TestUseFocusHook:
    """Tests for use_focus hook"""

    def test_use_focus_returns_focus_state(self):
        """use_focus should return is_focused boolean and focus function"""
        from inkpy import render
        from inkpy.reconciler import component
        from inkpy.reconciler.element import create_element
        from inkpy.reconciler.focus_hooks import use_focus

        focus_result = [None]

        @component
        def App():
            focus = use_focus()
            focus_result[0] = focus
            return create_element("ink-text", {}, "Focusable")

        stdout = StringIO()
        instance = render(App(), stdout=stdout, debug=True)

        # Should have is_focused and focus attributes
        assert focus_result[0] is not None
        assert hasattr(focus_result[0], "is_focused")
        assert hasattr(focus_result[0], "focus")
        assert isinstance(focus_result[0].is_focused, bool)
        assert callable(focus_result[0].focus)

        instance.unmount()

    def test_use_focus_with_auto_focus(self):
        """use_focus with auto_focus=True should auto-focus the component"""
        from inkpy import render
        from inkpy.reconciler import component
        from inkpy.reconciler.element import create_element
        from inkpy.reconciler.focus_hooks import use_focus

        focus_result = [None]

        @component
        def App():
            focus = use_focus(auto_focus=True)
            focus_result[0] = focus
            return create_element("ink-text", {}, "Auto focused")

        stdout = StringIO()
        instance = render(App(), stdout=stdout, debug=True)

        # Should be auto-focused
        assert focus_result[0].is_focused is True

        instance.unmount()

    def test_use_focus_with_custom_id(self):
        """use_focus should accept a custom ID"""
        from inkpy import render
        from inkpy.reconciler import component
        from inkpy.reconciler.element import create_element
        from inkpy.reconciler.focus_hooks import get_focus_state, use_focus

        @component
        def App():
            use_focus(id="my-custom-id")
            return create_element("ink-text", {}, "Custom ID")

        stdout = StringIO()
        instance = render(App(), stdout=stdout, debug=True)

        # Should be registered with custom ID
        state = get_focus_state()
        assert "my-custom-id" in [f["id"] for f in state["focusables"]]

        instance.unmount()

    def test_use_focus_is_active_controls_focusability(self):
        """use_focus with is_active=False should not be focusable"""
        from inkpy import render
        from inkpy.reconciler import component, use_state
        from inkpy.reconciler.element import create_element
        from inkpy.reconciler.focus_hooks import get_focus_state, use_focus

        set_active_ref = [None]

        @component
        def App():
            is_active, set_active = use_state(True)
            set_active_ref[0] = set_active
            focus = use_focus(is_active=is_active, id="test-item")
            return create_element("ink-text", {}, "Active" if focus.is_focused else "Inactive")

        stdout = StringIO()
        instance = render(App(), stdout=stdout, debug=True)

        # Should initially be active
        state = get_focus_state()
        item = next(f for f in state["focusables"] if f["id"] == "test-item")
        assert item["is_active"] is True

        # Deactivate
        set_active_ref[0](False)

        state = get_focus_state()
        item = next(f for f in state["focusables"] if f["id"] == "test-item")
        assert item["is_active"] is False

        instance.unmount()


class TestUseFocusManagerHook:
    """Tests for use_focus_manager hook"""

    def test_use_focus_manager_provides_navigation(self):
        """use_focus_manager should provide focus navigation functions"""
        from inkpy import render
        from inkpy.reconciler import component
        from inkpy.reconciler.element import create_element
        from inkpy.reconciler.focus_hooks import use_focus_manager

        manager_result = [None]

        @component
        def App():
            manager = use_focus_manager()
            manager_result[0] = manager
            return create_element("ink-text", {}, "Manager test")

        stdout = StringIO()
        instance = render(App(), stdout=stdout, debug=True)

        manager = manager_result[0]
        assert hasattr(manager, "focus_next")
        assert hasattr(manager, "focus_previous")
        assert hasattr(manager, "focus")
        assert callable(manager.focus_next)
        assert callable(manager.focus_previous)
        assert callable(manager.focus)

        instance.unmount()

    def test_focus_navigation_cycles_through_items(self):
        """focus_next should cycle through focusable items"""
        from inkpy import render
        from inkpy.reconciler import component
        from inkpy.reconciler.element import create_element
        from inkpy.reconciler.focus_hooks import get_focus_state, use_focus, use_focus_manager

        focus_results = {}
        manager_ref = [None]

        @component
        def FocusableItem(id: str = ""):
            focus = use_focus(id=id)
            focus_results[id] = focus
            return create_element("ink-text", {}, f"Item {id}")

        @component
        def App():
            manager = use_focus_manager()
            manager_ref[0] = manager
            return create_element(
                "ink-box",
                {},
                FocusableItem(id="item1"),
                FocusableItem(id="item2"),
                FocusableItem(id="item3"),
            )

        stdout = StringIO()
        instance = render(App(), stdout=stdout, debug=True)

        # Focus first item
        manager_ref[0].focus("item1")

        state = get_focus_state()
        assert state["active_id"] == "item1"

        # Navigate to next
        manager_ref[0].focus_next()

        state = get_focus_state()
        assert state["active_id"] == "item2"

        # Navigate to next again
        manager_ref[0].focus_next()

        state = get_focus_state()
        assert state["active_id"] == "item3"

        # Should wrap around
        manager_ref[0].focus_next()

        state = get_focus_state()
        assert state["active_id"] == "item1"

        instance.unmount()


class TestFocusCleanup:
    """Tests for focus cleanup on unmount"""

    def test_focus_unregisters_on_unmount(self):
        """use_focus should unregister when component unmounts"""
        from inkpy import render
        from inkpy.reconciler import component
        from inkpy.reconciler.element import create_element
        from inkpy.reconciler.focus_hooks import get_focus_state, reset_focus_state, use_focus

        # Reset state for clean test
        reset_focus_state()

        @component
        def App():
            use_focus(id="test-focus")
            return create_element("ink-text", {}, "Test")

        stdout = StringIO()
        instance = render(App(), stdout=stdout, debug=True)

        # Should be registered
        state = get_focus_state()
        assert len(state["focusables"]) == 1

        # Unmount
        instance.unmount()

        # Should be unregistered
        state = get_focus_state()
        assert len(state["focusables"]) == 0


class TestFocusInternalFunctions:
    """Tests for internal focus management functions"""

    def test_add_focusable_updates_existing(self):
        """_add_focusable should update existing entry"""
        from inkpy.reconciler.focus_hooks import (
            _add_focusable,
            get_focus_state,
            reset_focus_state,
        )

        reset_focus_state()

        # Add first time
        _add_focusable("test-id", {"auto_focus": False})
        state = get_focus_state()
        assert len(state["focusables"]) == 1
        assert state["focusables"][0]["auto_focus"] is False

        # Add again with different options - should update
        _add_focusable("test-id", {"auto_focus": True})
        state = get_focus_state()
        assert len(state["focusables"]) == 1  # Still only one
        assert state["focusables"][0]["auto_focus"] is True

    def test_remove_focusable_auto_focuses_next(self):
        """_remove_focusable should auto-focus next when active is removed"""
        from inkpy.reconciler.focus_hooks import (
            _add_focusable,
            _focus,
            _remove_focusable,
            get_focus_state,
            reset_focus_state,
        )

        reset_focus_state()

        # Add two focusables
        _add_focusable("item1", {"auto_focus": False})
        _add_focusable("item2", {"auto_focus": False})

        # Focus the first
        _focus("item1")
        state = get_focus_state()
        assert state["active_id"] == "item1"

        # Remove the focused one - should auto-focus next
        _remove_focusable("item1")
        state = get_focus_state()
        assert state["active_id"] == "item2"

    def test_deactivate_clears_active_focus(self):
        """_deactivate_focusable clears active if deactivating focused item"""
        from inkpy.reconciler.focus_hooks import (
            _add_focusable,
            _deactivate_focusable,
            _focus,
            get_focus_state,
            reset_focus_state,
        )

        reset_focus_state()

        _add_focusable("test-id", {"auto_focus": False})
        _focus("test-id")

        state = get_focus_state()
        assert state["active_id"] == "test-id"

        # Deactivate should clear active
        _deactivate_focusable("test-id")
        state = get_focus_state()
        assert state["active_id"] is None

    def test_focus_only_active_items(self):
        """_focus should only focus active items"""
        from inkpy.reconciler.focus_hooks import (
            _add_focusable,
            _deactivate_focusable,
            _focus,
            get_focus_state,
            reset_focus_state,
        )

        reset_focus_state()

        _add_focusable("test-id", {"auto_focus": False})
        _deactivate_focusable("test-id")

        # Try to focus inactive item
        _focus("test-id")
        state = get_focus_state()
        assert state["active_id"] is None  # Should not focus

    def test_focus_next_with_no_focusables(self):
        """_focus_next should handle empty focusables list"""
        from inkpy.reconciler.focus_hooks import (
            _focus_next,
            get_focus_state,
            reset_focus_state,
        )

        reset_focus_state()

        # Should not raise
        _focus_next()
        state = get_focus_state()
        assert state["active_id"] is None

    def test_focus_next_with_no_active(self):
        """_focus_next should focus first when nothing is active"""
        from inkpy.reconciler.focus_hooks import (
            _add_focusable,
            _focus_next,
            get_focus_state,
            reset_focus_state,
        )

        reset_focus_state()

        _add_focusable("item1", {"auto_focus": False})
        _add_focusable("item2", {"auto_focus": False})

        # No active focus
        state = get_focus_state()
        assert state["active_id"] is None

        # Focus next should focus first
        _focus_next()
        state = get_focus_state()
        assert state["active_id"] == "item1"

    def test_focus_next_with_invalid_active(self):
        """_focus_next handles when active_id doesn't match any focusable"""
        from inkpy.reconciler.focus_hooks import (
            _add_focusable,
            _focus_next,
            get_focus_state,
            reset_focus_state,
        )

        reset_focus_state()

        _add_focusable("item1", {"auto_focus": False})

        # Set invalid active_id directly
        state = get_focus_state()
        state["active_id"] = "nonexistent"

        # Focus next should focus first valid
        _focus_next()
        state = get_focus_state()
        assert state["active_id"] == "item1"

    def test_focus_previous_with_no_focusables(self):
        """_focus_previous should handle empty focusables list"""
        from inkpy.reconciler.focus_hooks import (
            _focus_previous,
            get_focus_state,
            reset_focus_state,
        )

        reset_focus_state()

        # Should not raise
        _focus_previous()
        state = get_focus_state()
        assert state["active_id"] is None

    def test_focus_previous_with_no_active(self):
        """_focus_previous should focus last when nothing is active"""
        from inkpy.reconciler.focus_hooks import (
            _add_focusable,
            _focus_previous,
            get_focus_state,
            reset_focus_state,
        )

        reset_focus_state()

        _add_focusable("item1", {"auto_focus": False})
        _add_focusable("item2", {"auto_focus": False})

        # No active focus
        state = get_focus_state()
        assert state["active_id"] is None

        # Focus previous should focus last
        _focus_previous()
        state = get_focus_state()
        assert state["active_id"] == "item2"

    def test_focus_previous_with_invalid_active(self):
        """_focus_previous handles when active_id doesn't match any focusable"""
        from inkpy.reconciler.focus_hooks import (
            _add_focusable,
            _focus_previous,
            get_focus_state,
            reset_focus_state,
        )

        reset_focus_state()

        _add_focusable("item1", {"auto_focus": False})
        _add_focusable("item2", {"auto_focus": False})

        # Set invalid active_id directly
        state = get_focus_state()
        state["active_id"] = "nonexistent"

        # Focus previous should focus last valid
        _focus_previous()
        state = get_focus_state()
        assert state["active_id"] == "item2"

    def test_focus_previous_wraps_around(self):
        """_focus_previous should wrap from first to last"""
        from inkpy.reconciler.focus_hooks import (
            _add_focusable,
            _focus,
            _focus_previous,
            get_focus_state,
            reset_focus_state,
        )

        reset_focus_state()

        _add_focusable("item1", {"auto_focus": False})
        _add_focusable("item2", {"auto_focus": False})
        _add_focusable("item3", {"auto_focus": False})

        _focus("item1")  # Focus first

        # Previous should wrap to last
        _focus_previous()
        state = get_focus_state()
        assert state["active_id"] == "item3"


class TestUseFocusManagerEnableDisable:
    """Tests for focus manager enable/disable functions"""

    def test_enable_focus(self):
        """enable_focus should set enabled to True"""
        from inkpy.reconciler.focus_hooks import (
            get_focus_state,
            reset_focus_state,
            use_focus_manager,
        )

        reset_focus_state()

        # Disable first
        state = get_focus_state()
        state["enabled"] = False

        manager = use_focus_manager()
        manager.enable_focus()

        state = get_focus_state()
        assert state["enabled"] is True

    def test_disable_focus(self):
        """disable_focus should set enabled to False"""
        from inkpy.reconciler.focus_hooks import (
            get_focus_state,
            reset_focus_state,
            use_focus_manager,
        )

        reset_focus_state()

        manager = use_focus_manager()
        manager.disable_focus()

        state = get_focus_state()
        assert state["enabled"] is False


class TestUseFocusFocusCallback:
    """Tests for use_focus focus callback"""

    def test_focus_self_callback(self):
        """use_focus.focus() should focus the component"""
        from inkpy.reconciler.focus_hooks import (
            _add_focusable,
            get_focus_state,
            reset_focus_state,
        )
        from inkpy import render
        from inkpy.reconciler import component
        from inkpy.reconciler.element import create_element
        from inkpy.reconciler.focus_hooks import use_focus

        reset_focus_state()

        focus_results = {}

        @component
        def App():
            focus1 = use_focus(id="item1")
            focus2 = use_focus(id="item2")
            focus_results["item1"] = focus1
            focus_results["item2"] = focus2
            return create_element("ink-box", {})

        stdout = StringIO()
        instance = render(App(), stdout=stdout, debug=True)

        # Initially nothing focused
        state = get_focus_state()
        assert state["active_id"] is None

        # Call focus on item2
        focus_results["item2"].focus()

        state = get_focus_state()
        assert state["active_id"] == "item2"

        instance.unmount()
