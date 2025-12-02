"""
Renderer module - Main renderer function that converts DOM tree to output string.

Ports renderer.ts functionality from Ink.
"""

from typing import Any

from ..dom import DOMElement
from .output import Output
from .render_node import render_dom_node_to_output
from .screen_reader import render_node_to_screen_reader_output


def renderer(node: DOMElement, is_screen_reader_enabled: bool) -> dict[str, Any]:
    """
    Render a DOM element tree to output string.

    Args:
        node: Root DOM element node
        is_screen_reader_enabled: Whether screen reader mode is enabled

    Returns:
        Dictionary with:
        - output: Main output string
        - outputHeight: Height of output in lines
        - staticOutput: Static output string (with newline)
    """
    if not node.yoga_node:
        return {
            "output": "",
            "outputHeight": 0,
            "staticOutput": "",
        }

    if is_screen_reader_enabled:
        # Screen reader mode - use text-only output
        output = render_node_to_screen_reader_output(node, skip_static=True)
        output_height = 0 if output == "" else len(output.split("\n"))

        static_output = ""
        if node.static_node:
            static_output = render_node_to_screen_reader_output(node.static_node, skip_static=False)

        return {
            "output": output,
            "outputHeight": output_height,
            "staticOutput": f"{static_output}\n" if static_output else "",
        }

    # Normal rendering mode
    # Get layout to determine output buffer size
    layout = node.yoga_node.get_layout()
    output_buffer = Output(
        width=int(layout.get("width", 80)),
        height=int(layout.get("height", 24)),
    )

    # Render main tree (skipping static elements)
    # Use DOM tree traversal instead of Yoga tree for proper text rendering
    render_dom_node_to_output(
        node,
        output_buffer,
        skip_static=True,
    )

    # Render static node if present
    static_output_buffer = None
    if node.static_node and node.static_node.yoga_node:
        static_layout = node.static_node.yoga_node.get_layout()
        static_output_buffer = Output(
            width=int(static_layout.get("width", 80)),
            height=int(static_layout.get("height", 24)),
        )

        # Use DOM-based rendering for static content (same as main content)
        render_dom_node_to_output(
            node.static_node,
            static_output_buffer,
            skip_static=False,
        )

    # Get generated output
    result = output_buffer.get()
    generated_output = result["output"]
    output_height = result["height"]

    # Get static output
    static_output = ""
    if static_output_buffer:
        static_result = static_output_buffer.get()
        static_output = static_result["output"]

    return {
        "output": generated_output,
        "outputHeight": output_height,
        # Newline at end needed so interactive output doesn't override last line of static
        "staticOutput": f"{static_output}\n" if static_output else "",
    }
