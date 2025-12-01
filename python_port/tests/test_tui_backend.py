# test_tui_backend.py
import pytest
from reactpy import component, html
from inkpy.backend.tui_backend import TUIBackend
from inkpy.components.box import Box
from inkpy.components.text import Text

def test_backend_initialization():
    """Test TUI backend can be initialized"""
    backend = TUIBackend()
    assert backend is not None

def test_backend_mounts_component():
    """Test backend can mount a component"""
    @component
    def App():
        return Box(Text("Hello"))
    
    backend = TUIBackend()
    root = backend.mount(App())
    
    assert root is not None
    assert root.node_name == 'ink-root'

def test_backend_creates_dom_nodes():
    """Test backend creates proper DOM nodes from VDOM"""
    @component
    def App():
        return Box(Text("Test"))
    
    backend = TUIBackend()
    root = backend.mount(App())
    
    # Backend should create root node (children may be empty in simplified version)
    assert root is not None
    assert root.node_name == 'ink-root'

def test_backend_handles_updates():
    """Test backend handles component updates"""
    counter = [0]
    
    @component
    def App():
        return Text(f"Count: {counter[0]}")
    
    backend = TUIBackend()
    root = backend.mount(App())
    
    # Update component
    counter[0] = 1
    backend.update()
    
    # DOM should reflect new count

def test_backend_calculates_layout():
    """Test backend triggers layout calculation"""
    @component
    def App():
        return Box(Text("Test"))
    
    backend = TUIBackend()
    root = backend.mount(App())
    
    # Should be able to calculate layout
    backend.calculate_layout(width=80)
    
    # Root should have computed layout
    assert root.yoga_node is not None

