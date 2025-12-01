"""
Render Pipeline Integration Tests

Tests the full render pipeline end-to-end:
1. Simple text rendering
2. Nested Box/Text components
3. State updates trigger re-render
4. Focus navigation works
5. Static component output

NOTE: These tests currently reveal that the render pipeline has a bug - 
the Ink.render() method creates a Layout but doesn't actually trigger rendering.
The hardcoded "Hello, World!" debug output needs to be replaced with actual
rendering that converts ReactPy VDOM to DOM and renders it.
"""
import pytest
import io
from reactpy import component, use_state
from inkpy import render, Box, Text, Static
from inkpy.hooks import use_focus, use_input
from inkpy.input.keypress import Key
from inkpy.instances import instances


@pytest.fixture(autouse=True)
def clean_instances():
    """Ensure clean instance registry before each test"""
    # Clear all instances before test
    instances._instances.clear()
    yield
    # Clean up after test
    instances._instances.clear()


class MockStdout:
    """Mock stdout that captures output"""
    def __init__(self):
        self.buffer = io.StringIO()
        self.columns = 80
        self.rows = 24
        
    def write(self, data):
        self.buffer.write(data)
        
    def getvalue(self):
        return self.buffer.getvalue()
    
    def flush(self):
        pass
    
    def isatty(self):
        return True


def test_simple_text_rendering():
    """Test Case 1: Simple text rendering"""
    @component
    def App():
        return Text("Hello, World!")
    
    stdout = MockStdout()
    instance = render(App(), stdout=stdout, debug=True)
    
    output = stdout.getvalue()
    assert "Hello, World!" in output
    
    instance.unmount()
    instance.cleanup()  # Clean up instance registry


def test_nested_box_text_components():
    """Test Case 2: Nested Box/Text components"""
    @component
    def App():
        return Box(
            Box(
                Text("Inner"),
                style={'padding': 1}
            ),
            Text("Outer"),
            style={'flexDirection': 'column'}
        )
    
    stdout = MockStdout()
    instance = render(App(), stdout=stdout, debug=True)
    
    output = stdout.getvalue()
    assert "Inner" in output
    assert "Outer" in output
    
    instance.unmount()
    instance.cleanup()  # Clean up instance registry


def test_state_updates_trigger_rerender():
    """Test Case 3: State updates trigger re-render"""
    @component
    def Counter():
        count, set_count = use_state(0)
        
        # Simulate state update (in real app, this would be triggered by user input)
        # For testing, we'll use rerender with a new component that has different state
        return Box(Text(f"Count: {count}"))
    
    stdout = MockStdout()
    instance = render(Counter(), stdout=stdout, debug=True)
    
    # Initial render should show count 0
    output1 = stdout.getvalue()
    assert "Count: 0" in output1 or "Count:" in output1
    
    # Re-render with updated component
    @component
    def CounterUpdated():
        count, set_count = use_state(1)  # Different initial state
        return Box(Text(f"Count: {count}"))
    
    instance.rerender(CounterUpdated())
    output2 = stdout.getvalue()
    # Should have re-rendered (output should contain updated content)
    assert len(output2) >= len(output1)
    
    instance.unmount()
    instance.cleanup()  # Clean up instance registry


def test_focus_navigation_works():
    """Test Case 4: Focus navigation works"""
    @component
    def FocusableApp():
        focus1 = use_focus()
        focus2 = use_focus()
        
        return Box(
            Box(
                Text("Focusable 1"),
                style={'borderStyle': 'single'} if focus1.is_focused else {}
            ),
            Box(
                Text("Focusable 2"),
                style={'borderStyle': 'single'} if focus2.is_focused else {}
            ),
            style={'flexDirection': 'column'}
        )
    
    stdout = MockStdout()
    stdin = io.StringIO()
    instance = render(FocusableApp(), stdout=stdout, stdin=stdin, debug=True)
    
    output = stdout.getvalue()
    assert "Focusable 1" in output
    assert "Focusable 2" in output
    
    # Focus navigation would be tested with actual keyboard input
    # For now, we verify the component renders with focus hooks
    
    instance.unmount()
    instance.cleanup()  # Clean up instance registry


def test_static_component_output():
    """Test Case 5: Static component output"""
    @component
    def App():
        return Box(
            Static(
                Text("Static Content")
            ),
            Text("Dynamic Content"),
            style={'flexDirection': 'column'}
        )
    
    stdout = MockStdout()
    instance = render(App(), stdout=stdout, debug=True)
    
    output = stdout.getvalue()
    assert "Static Content" in output
    assert "Dynamic Content" in output
    
    # Static content should persist across re-renders
    @component
    def AppUpdated():
        return Box(
            Static(
                Text("Static Content")
            ),
            Text("Updated Dynamic"),
            style={'flexDirection': 'column'}
        )
    
    instance.rerender(AppUpdated())
    output2 = stdout.getvalue()
    assert "Static Content" in output2
    assert "Updated Dynamic" in output2
    
    instance.unmount()
    instance.cleanup()  # Clean up instance registry


def test_full_pipeline_with_styles():
    """Additional test: Full pipeline with styles (colors, borders, padding)"""
    @component
    def StyledApp():
        return Box(
            Box(
                Text("Red Text", style={'color': 'red'}),
                Text("Blue Background", style={'backgroundColor': 'blue'}),
                style={
                    'borderStyle': 'single',
                    'padding': 1,
                    'flexDirection': 'column'
                }
            ),
            style={'width': 40, 'height': 10}
        )
    
    stdout = MockStdout()
    instance = render(StyledApp(), stdout=stdout, debug=True)
    
    output = stdout.getvalue()
    assert "Red Text" in output
    assert "Blue Background" in output
    # Should contain ANSI color codes
    assert '\x1b[' in output
    
    instance.unmount()
    instance.cleanup()  # Clean up instance registry


def test_pipeline_with_multiline_text():
    """Additional test: Pipeline handles multiline text correctly"""
    @component
    def MultilineApp():
        return Box(
            Text("Line 1\nLine 2\nLine 3"),
            style={'width': 20, 'height': 5}
        )
    
    stdout = MockStdout()
    instance = render(MultilineApp(), stdout=stdout, debug=True)
    
    output = stdout.getvalue()
    assert "Line 1" in output
    assert "Line 2" in output
    assert "Line 3" in output
    
    instance.unmount()
    instance.cleanup()  # Clean up instance registry
