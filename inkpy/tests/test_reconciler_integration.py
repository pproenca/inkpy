# tests/test_reconciler_integration.py
"""Integration tests for custom reconciler with InkPy"""
import pytest
from io import StringIO
from inkpy.reconciler.component import component
from inkpy.reconciler.element import create_element
from inkpy.reconciler.hooks import use_state


def test_render_with_custom_reconciler():
    """Test render() works with custom reconciler"""
    from inkpy import render
    
    @component
    def App():
        return create_element("ink-box", {},
            create_element("ink-text", {}, "Hello World")
        )
    
    stdout = StringIO()
    instance = render(App(), stdout=stdout, debug=True)
    
    # Should render without error
    assert instance is not None
    instance.unmount()


def test_interactive_state_updates():
    """Test that state updates trigger re-renders"""
    from inkpy import render
    
    renders = []
    set_count_ref = [None]
    
    @component
    def Counter():
        count, set_count = use_state(0)
        set_count_ref[0] = set_count
        renders.append(count)
        return create_element("ink-text", {}, str(count))
    
    stdout = StringIO()
    instance = render(Counter(), stdout=stdout, debug=True)
    
    assert renders == [0]
    
    # Trigger state update
    set_count_ref[0](1)
    
    # State update should trigger re-render synchronously
    assert renders == [0, 1]
    
    instance.unmount()


# ============================================================
# Enter Key Regression Tests
# ============================================================

class TestEnterKeyParsing:
    """Regression tests for Enter key parsing (both \r and \n)"""
    
    def test_carriage_return_is_return_key(self):
        """\\r should be recognized as return_key"""
        from inkpy.input.keypress import parse_keypress, Key
        
        key = parse_keypress('\r')
        assert key.name == 'return', f"Expected 'return', got '{key.name}'"
        assert key.return_key is True, "return_key should be True for \\r"
    
    def test_newline_is_return_key(self):
        """\\n should ALSO be recognized as return_key (regression test)
        
        Many terminals send \\n for Enter instead of \\r.
        """
        from inkpy.input.keypress import parse_keypress, Key
        
        key = parse_keypress('\n')
        # This is the regression test - currently fails!
        assert key.return_key is True, (
            f"return_key should be True for \\n. "
            f"Got name='{key.name}', return_key={key.return_key}"
        )
    
    def test_return_property_works(self):
        """The return_ property should work for both \\r and \\n"""
        from inkpy.input.keypress import parse_keypress
        
        cr_key = parse_keypress('\r')
        nl_key = parse_keypress('\n')
        
        assert cr_key.return_ is True, "return_ should be True for \\r"
        assert nl_key.return_ is True, (
            "return_ should be True for \\n (regression)"
        )


# ============================================================
# Stale Closure Regression Tests
# ============================================================

class TestStaleClosureRegression:
    """Regression tests for stale closure issues in handlers"""
    
    def test_handler_sees_current_state_not_stale(self):
        """Input handlers should see current state, not stale closure values
        
        This is a common React pattern bug where handlers capture state
        at definition time instead of using the latest value.
        """
        from inkpy import render
        from inkpy.reconciler import component, use_state
        from inkpy.reconciler.element import create_element
        
        captured_values = []
        set_count_ref = [None]
        handler_ref = [None]
        
        @component
        def App():
            count, set_count = use_state(0)
            set_count_ref[0] = set_count
            
            # This handler will be registered with use_input
            # It should see the CURRENT value of count, not the initial 0
            def handle_input(input_str, key):
                captured_values.append(count)
            
            handler_ref[0] = handle_input
            
            return create_element("ink-text", {}, str(count))
        
        stdout = StringIO()
        instance = render(App(), stdout=stdout, debug=True)
        
        # Initial render - handler sees count=0
        handler_ref[0]("", None)
        assert captured_values == [0], "Initial state should be 0"
        
        # Update state to 5
        set_count_ref[0](5)
        
        # Call handler again - should see count=5, not stale 0
        handler_ref[0]("", None)
        assert captured_values[-1] == 5, (
            f"Handler should see current state 5, got {captured_values[-1]}"
        )
        
        instance.unmount()
    
    def test_use_input_handler_updates_on_rerender(self):
        """use_input should use the latest handler, not the stale one
        
        When component re-renders with new state, use_input's registered
        handler should reflect the new closure with updated state.
        """
        from inkpy import render
        from inkpy.reconciler import component, use_state, use_input
        from inkpy.reconciler.element import create_element
        from inkpy.reconciler.app_hooks import _app_state
        
        captured_states = []
        set_count_ref = [None]
        
        @component
        def App():
            count, set_count = use_state(0)
            set_count_ref[0] = set_count
            
            def handle_input(input_str, key):
                # Capture what value of count the handler sees
                captured_states.append(count)
            
            use_input(handle_input)
            
            return create_element("ink-text", {}, str(count))
        
        stdout = StringIO()
        instance = render(App(), stdout=stdout, debug=True)
        
        # Simulate input to the registered handler
        if _app_state['input_handlers']:
            _app_state['input_handlers'][0]("test", None)
        
        # Update state
        set_count_ref[0](10)
        
        # Call the current handler - should see updated state
        if _app_state['input_handlers']:
            _app_state['input_handlers'][0]("test", None)
        
        # The second capture should see state=10
        assert len(captured_states) >= 2, "Should have at least 2 captures"
        assert captured_states[-1] == 10, (
            f"Handler should see current state 10, got {captured_states[-1]}. "
            f"All captures: {captured_states}"
        )
        
        instance.unmount()
        _app_state['input_handlers'].clear()


# ============================================================
# Effect Lifecycle Regression Tests
# ============================================================

class TestEffectLifecycle:
    """Regression tests for effect lifecycle (cleanup, deps)"""
    
    def test_effect_cleanup_called_on_unmount(self):
        """Effect cleanup should be called when app unmounts"""
        from inkpy import render
        from inkpy.reconciler import component, use_effect
        from inkpy.reconciler.element import create_element
        
        cleanup_called = []
        
        @component
        def App():
            def effect():
                # Return cleanup function
                return lambda: cleanup_called.append('cleanup')
            
            use_effect(effect, [])
            return create_element("ink-text", {}, "Hello")
        
        stdout = StringIO()
        instance = render(App(), stdout=stdout, debug=True)
        
        # Effect should have run
        assert len(cleanup_called) == 0, "Cleanup not called yet"
        
        # Unmount
        instance.unmount()
        
        # Cleanup SHOULD be called (this is the regression test)
        assert len(cleanup_called) == 1, (
            f"Cleanup should be called on unmount. Got: {cleanup_called}"
        )
    
    def test_effect_reruns_when_deps_change(self):
        """Effect should re-run when dependencies change"""
        from inkpy import render
        from inkpy.reconciler import component, use_state, use_effect
        from inkpy.reconciler.element import create_element
        
        effect_runs = []
        set_count_ref = [None]
        
        @component
        def App():
            count, set_count = use_state(0)
            set_count_ref[0] = set_count
            
            def effect():
                effect_runs.append(count)
            
            use_effect(effect, [count])  # Depends on count
            
            return create_element("ink-text", {}, str(count))
        
        stdout = StringIO()
        instance = render(App(), stdout=stdout, debug=True)
        
        # Effect should have run once with count=0
        assert effect_runs == [0], f"Effect should run initially. Got: {effect_runs}"
        
        # Update state
        set_count_ref[0](5)
        
        # Effect SHOULD re-run with count=5 (this is the regression test)
        assert effect_runs == [0, 5], (
            f"Effect should re-run when deps change. Got: {effect_runs}"
        )
        
        instance.unmount()
    
    def test_effect_cleanup_called_before_rerun(self):
        """Effect cleanup should be called before effect re-runs"""
        from inkpy import render
        from inkpy.reconciler import component, use_state, use_effect
        from inkpy.reconciler.element import create_element
        
        events = []
        set_count_ref = [None]
        
        @component
        def App():
            count, set_count = use_state(0)
            set_count_ref[0] = set_count
            
            def effect():
                events.append(f'run-{count}')
                return lambda: events.append(f'cleanup-{count}')
            
            use_effect(effect, [count])
            
            return create_element("ink-text", {}, str(count))
        
        stdout = StringIO()
        instance = render(App(), stdout=stdout, debug=True)
        
        assert events == ['run-0'], f"Initial run. Got: {events}"
        
        # Update state
        set_count_ref[0](1)
        
        # Should cleanup old, then run new
        assert events == ['run-0', 'cleanup-0', 'run-1'], (
            f"Cleanup should be called before re-run. Got: {events}"
        )
        
        instance.unmount()

