"""
Measure element module - Get computed dimensions of DOM elements.

Ported from: src/measure-element.ts
"""

from .dom import DOMElement


def measure_element(node: DOMElement) -> dict[str, int]:
    """
    Measure the dimensions of a particular `<Box>` element.

    Returns an object with `width` and `height` properties.
    This function is useful when your component needs to know the amount
    of available space it has. You can use it when you need to change the
    layout based on the length of its content.

    Note: measure_element() returns correct results only after the initial
    render, when the layout has been calculated. Until then, width and height
    equal zero. It's recommended to call measure_element() in a use_effect hook,
    which fires after the component has rendered.

    Args:
        node: DOM element node (typically a Box element)

    Returns:
        Dictionary with 'width' and 'height' keys
    """
    if node.yoga_node:
        # Use get_computed_width/height to match TypeScript API
        return {
            "width": int(node.yoga_node.get_computed_width() or 0),
            "height": int(node.yoga_node.get_computed_height() or 0),
        }

    return {"width": 0, "height": 0}
