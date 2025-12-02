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

