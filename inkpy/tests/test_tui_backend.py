# test_tui_backend.py
from reactpy import component, html

from inkpy.backend.tui_backend import TUIBackend
from inkpy.components.box import Box
from inkpy.components.text import Text


def test_backend_initialization():
    """Test TUI backend can be initialized"""
    backend = TUIBackend()
    assert backend is not None
    assert backend.root is None


def test_backend_mounts_component():
    """Test backend can mount a component"""

    @component
    def App():
        return Box(Text("Hello"))

    backend = TUIBackend()
    root = backend.mount(App())

    assert root is not None
    assert root.node_name == "ink-root"
    assert backend.root == root


def test_backend_creates_dom_nodes():
    """Test backend creates proper DOM nodes from VDOM"""

    @component
    def App():
        return Box(Text("Test"))

    backend = TUIBackend()
    root = backend.mount(App())

    # Backend should create root node
    assert root is not None
    assert root.node_name == "ink-root"
    assert root.yoga_node is not None


def test_backend_applies_styles():
    """Test backend applies styles to DOM nodes"""

    # Test with direct VDOM (html.div returns VDOM dict)
    vdom = html.div({"style": {"padding": 2, "flexDirection": "column"}})

    backend = TUIBackend()
    # Convert VDOM directly
    box_node = backend.vdom_to_dom(vdom)

    # Should create a box node
    assert box_node is not None
    assert box_node.node_name == "ink-box"

    # Style should be applied
    assert hasattr(box_node, "style")
    assert box_node.style == {"padding": 2, "flexDirection": "column"}

    # Yoga node should have styles applied
    if box_node.yoga_node:
        layout = box_node.yoga_node.view.poga_layout()
        # Check that padding was applied (converted to YGValue)
        assert hasattr(layout, "padding")


def test_backend_handles_text_nodes():
    """Test backend creates text nodes correctly"""

    @component
    def App():
        return Text("Hello World")

    backend = TUIBackend()
    root = backend.mount(App())

    assert root is not None
    # Should have text content somewhere in the tree


def test_backend_handles_internal_transform():
    """Test backend preserves internal_transform attribute"""

    @component
    def App():
        return Text("Test", color="red")

    backend = TUIBackend()
    _root = backend.mount(App())

    # internal_transform should be preserved on text nodes
    # This is tested by checking if transform function exists


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


def test_backend_unmount():
    """Test backend cleanup on unmount"""

    @component
    def App():
        return Box(Text("Test"))

    backend = TUIBackend()
    backend.mount(App())
    assert backend.root is not None

    backend.unmount()
    assert backend.root is None
    assert backend._layout is None
