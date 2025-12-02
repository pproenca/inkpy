# tests/reconciler/test_component.py
from inkpy.reconciler.component import component
from inkpy.reconciler.element import create_element
from inkpy.reconciler.hooks import use_state


def test_component_decorator():
    """Test @component decorator creates a function component"""

    @component
    def Greeting(name: str = "World"):
        return create_element("ink-text", {}, f"Hello, {name}!")

    # Should be callable and return an element
    element = Greeting(name="Test")

    assert element.type == Greeting.__wrapped__
    assert element.props["name"] == "Test"


def test_component_with_children():
    """Test component receives children prop"""

    @component
    def Container(children=None):
        return create_element("ink-box", {}, *children if children else [])

    child = create_element("ink-text", {}, "Child")
    element = Container(child)

    assert "children" in element.props


def test_component_with_state():
    """Test component can use hooks"""

    @component
    def Counter():
        count, set_count = use_state(0)
        return create_element("ink-text", {}, str(count))

    # Just verify it creates an element
    element = Counter()
    assert element.type == Counter.__wrapped__
