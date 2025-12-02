"""
Tests for Static component - renders output once and persists above dynamic content.
"""

import io

from reactpy import component

from inkpy import Box, Text, render
from inkpy.components.static import Static


def test_static_renders_items():
    """Static component should render all items on first render"""

    @component
    def App():
        items = ["Item 1", "Item 2", "Item 3"]
        return Static(
            items=items,
            children=lambda item, idx: Text(f"{idx}: {item}"),
        )

    stdout = io.StringIO()
    stdout.columns = 80
    stdout.rows = 24

    instance = render(App(), stdout=stdout, debug=True)
    output = stdout.getvalue()

    # Should render all items
    assert "0: Item 1" in output
    assert "1: Item 2" in output
    assert "2: Item 3" in output
    instance.unmount()


def test_static_with_empty_items():
    """Static component should handle empty items list"""

    @component
    def App():
        return Static(
            items=[],
            children=lambda item, idx: Text(f"{idx}: {item}"),
        )

    stdout = io.StringIO()
    stdout.columns = 80
    stdout.rows = 24

    instance = render(App(), stdout=stdout, debug=True)
    assert instance is not None
    instance.unmount()


def test_static_with_custom_style():
    """Static component should apply custom styles"""

    @component
    def App():
        items = ["Task 1"]
        return Static(
            items=items,
            children=lambda item, idx: Text(item),
            style={"paddingLeft": 2, "flexDirection": "column"},
        )

    stdout = io.StringIO()
    stdout.columns = 80
    stdout.rows = 24

    instance = render(App(), stdout=stdout, debug=True)
    output = stdout.getvalue()

    assert "Task 1" in output
    instance.unmount()


def test_static_children_receive_item_and_index():
    """Static children function receives item and index"""
    received_args = []

    @component
    def App():
        items = ["A", "B", "C"]

        def render_child(item, idx):
            received_args.append((item, idx))
            return Text(f"{idx}:{item}")

        return Static(items=items, children=render_child)

    stdout = io.StringIO()
    stdout.columns = 80
    stdout.rows = 24

    instance = render(App(), stdout=stdout, debug=True)

    # Children function should be called for each item
    assert len(received_args) == 3
    assert received_args[0] == ("A", 0)
    assert received_args[1] == ("B", 1)
    assert received_args[2] == ("C", 2)
    instance.unmount()


def test_static_default_styles():
    """Static component should apply default absolute positioning"""

    @component
    def App():
        items = ["Test"]
        return Static(items=items, children=lambda item, idx: Text(item))

    stdout = io.StringIO()
    stdout.columns = 80
    stdout.rows = 24

    # This tests that the component renders without errors
    # The internal_static flag should be set on the Box
    instance = render(App(), stdout=stdout, debug=True)
    assert instance is not None
    instance.unmount()


def test_static_wraps_in_box():
    """Static should wrap children in a Box with internal_static=True"""

    @component
    def App():
        items = ["Item"]
        return Static(items=items, children=lambda item, idx: Text(item))

    stdout = io.StringIO()
    stdout.columns = 80
    stdout.rows = 24

    instance = render(App(), stdout=stdout, debug=True)
    output = stdout.getvalue()

    # Should have rendered the item
    assert "Item" in output
    instance.unmount()


def test_static_multiple_types_of_items():
    """Static should handle different item types"""

    @component
    def App():
        items = [1, 2, 3]  # integers instead of strings
        return Static(
            items=items,
            children=lambda item, idx: Text(f"Number: {item}"),
        )

    stdout = io.StringIO()
    stdout.columns = 80
    stdout.rows = 24

    instance = render(App(), stdout=stdout, debug=True)
    output = stdout.getvalue()

    assert "Number: 1" in output
    assert "Number: 2" in output
    assert "Number: 3" in output
    instance.unmount()


def test_static_dict_items():
    """Static should handle dictionary items"""

    @component
    def App():
        items = [
            {"name": "Task 1", "status": "done"},
            {"name": "Task 2", "status": "pending"},
        ]
        return Static(
            items=items,
            children=lambda item, idx: Text(f"{item['name']}: {item['status']}"),
        )

    stdout = io.StringIO()
    stdout.columns = 80
    stdout.rows = 24

    instance = render(App(), stdout=stdout, debug=True)
    output = stdout.getvalue()

    assert "Task 1: done" in output
    assert "Task 2: pending" in output
    instance.unmount()
