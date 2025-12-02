# tests/reconciler/test_element.py
from inkpy.reconciler.element import create_element


def test_create_element_with_type():
    """Test creating an element with type and props"""
    element = create_element("ink-box", {"padding": 1})

    assert element.type == "ink-box"
    assert element.props == {"padding": 1, "children": []}
    assert element.key is None


def test_create_element_with_children():
    """Test creating an element with children"""
    child1 = create_element("ink-text", {}, "Hello")
    child2 = create_element("ink-text", {}, "World")
    parent = create_element("ink-box", {}, child1, child2)

    assert len(parent.props["children"]) == 2
    assert parent.props["children"][0] is child1
    assert parent.props["children"][1] is child2


def test_create_element_with_string_child():
    """Test creating an element with string children"""
    element = create_element("ink-text", {}, "Hello World")

    assert element.props["children"] == ["Hello World"]


def test_create_element_with_function_type():
    """Test creating an element with a function component"""

    def MyComponent(props):
        return create_element("ink-box", props)

    element = create_element(MyComponent, {"name": "test"})

    assert element.type == MyComponent
    assert element.props["name"] == "test"


def test_create_element_with_key():
    """Test creating an element with a key"""
    element = create_element("ink-box", {"key": "unique-id"})

    assert element.key == "unique-id"
    assert "key" not in element.props  # key should be extracted
