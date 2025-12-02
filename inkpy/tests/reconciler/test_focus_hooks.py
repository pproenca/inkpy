# tests/reconciler/test_focus_hooks.py
"""Tests for use_focus hook in custom reconciler"""
import pytest
from io import StringIO


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
        from inkpy.reconciler import component, use_state
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
        assert hasattr(focus_result[0], 'is_focused')
        assert hasattr(focus_result[0], 'focus')
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
        from inkpy.reconciler.focus_hooks import use_focus, get_focus_state
        
        @component
        def App():
            use_focus(id="my-custom-id")
            return create_element("ink-text", {}, "Custom ID")
        
        stdout = StringIO()
        instance = render(App(), stdout=stdout, debug=True)
        
        # Should be registered with custom ID
        state = get_focus_state()
        assert "my-custom-id" in [f['id'] for f in state['focusables']]
        
        instance.unmount()
    
    def test_use_focus_is_active_controls_focusability(self):
        """use_focus with is_active=False should not be focusable"""
        from inkpy import render
        from inkpy.reconciler import component, use_state
        from inkpy.reconciler.element import create_element
        from inkpy.reconciler.focus_hooks import use_focus, get_focus_state
        
        set_active_ref = [None]
        
        @component
        def App():
            is_active, set_active = use_state(True)
            set_active_ref[0] = set_active
            focus = use_focus(is_active=is_active, id="test-item")
            return create_element("ink-text", {}, 
                "Active" if focus.is_focused else "Inactive"
            )
        
        stdout = StringIO()
        instance = render(App(), stdout=stdout, debug=True)
        
        # Should initially be active
        state = get_focus_state()
        item = next(f for f in state['focusables'] if f['id'] == "test-item")
        assert item['is_active'] is True
        
        # Deactivate
        set_active_ref[0](False)
        
        state = get_focus_state()
        item = next(f for f in state['focusables'] if f['id'] == "test-item")
        assert item['is_active'] is False
        
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
        assert hasattr(manager, 'focus_next')
        assert hasattr(manager, 'focus_previous')
        assert hasattr(manager, 'focus')
        assert callable(manager.focus_next)
        assert callable(manager.focus_previous)
        assert callable(manager.focus)
        
        instance.unmount()
    
    def test_focus_navigation_cycles_through_items(self):
        """focus_next should cycle through focusable items"""
        from inkpy import render
        from inkpy.reconciler import component
        from inkpy.reconciler.element import create_element
        from inkpy.reconciler.focus_hooks import use_focus, use_focus_manager, get_focus_state
        
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
            return create_element("ink-box", {},
                FocusableItem(id="item1"),
                FocusableItem(id="item2"),
                FocusableItem(id="item3"),
            )
        
        stdout = StringIO()
        instance = render(App(), stdout=stdout, debug=True)
        
        # Focus first item
        manager_ref[0].focus("item1")
        
        state = get_focus_state()
        assert state['active_id'] == "item1"
        
        # Navigate to next
        manager_ref[0].focus_next()
        
        state = get_focus_state()
        assert state['active_id'] == "item2"
        
        # Navigate to next again
        manager_ref[0].focus_next()
        
        state = get_focus_state()
        assert state['active_id'] == "item3"
        
        # Should wrap around
        manager_ref[0].focus_next()
        
        state = get_focus_state()
        assert state['active_id'] == "item1"
        
        instance.unmount()


class TestFocusCleanup:
    """Tests for focus cleanup on unmount"""
    
    def test_focus_unregisters_on_unmount(self):
        """use_focus should unregister when component unmounts"""
        from inkpy import render
        from inkpy.reconciler import component
        from inkpy.reconciler.element import create_element
        from inkpy.reconciler.focus_hooks import use_focus, get_focus_state, reset_focus_state
        
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
        assert len(state['focusables']) == 1
        
        # Unmount
        instance.unmount()
        
        # Should be unregistered
        state = get_focus_state()
        assert len(state['focusables']) == 0

