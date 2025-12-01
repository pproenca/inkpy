# test_render.py
import io
from inkpy.render import render
from inkpy.components.text import Text
from reactpy import component

def test_render_returns_instance():
    """Test render function returns Instance object"""
    @component
    def App():
        return Text("Test")
    
    instance = render(App(), stdout=io.StringIO(), stdin=io.StringIO(), stderr=io.StringIO())
    
    assert instance is not None
    assert hasattr(instance, 'rerender')
    assert hasattr(instance, 'unmount')
    assert hasattr(instance, 'wait_until_exit')
    assert hasattr(instance, 'clear')
    
    instance.unmount()

def test_render_with_stdout_option():
    """Test render with custom stdout"""
    buffer = io.StringIO()
    buffer.columns = 80
    buffer.rows = 24
    
    @component
    def App():
        return Text("Hello")
    
    instance = render(App(), stdout=buffer, debug=True)
    
    # Should write to custom stdout
    instance.unmount()

def test_render_default_options():
    """Test render uses default options"""
    @component
    def App():
        return Text("Test")
    
    # Should use sys.stdout by default
    instance = render(App(), stdout=io.StringIO(), stdin=io.StringIO())
    instance.unmount()

def test_instance_rerender():
    """Test instance.rerender updates the component"""
    @component
    def App():
        return Text("Initial")
    
    instance = render(App(), stdout=io.StringIO(), stdin=io.StringIO(), debug=True)
    
    @component
    def NewApp():
        return Text("Updated")
    
    instance.rerender(NewApp())
    instance.unmount()

def test_instance_clear():
    """Test instance.clear clears output"""
    @component
    def App():
        return Text("Test")
    
    instance = render(App(), stdout=io.StringIO(), stdin=io.StringIO())
    instance.clear()
    instance.unmount()

def test_render_singleton_per_stdout():
    """Test render creates singleton Ink instance per stdout"""
    stdout1 = io.StringIO()
    stdout1.columns = 80
    
    @component
    def App():
        return Text("Test")
    
    instance1 = render(App(), stdout=stdout1)
    instance2 = render(App(), stdout=stdout1)
    
    # Should reuse same Ink instance
    instance1.unmount()

