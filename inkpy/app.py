import asyncio

from layout_engine import YogaNode
from reactpy import component, html, use_effect, use_state
from reactpy.core.layout import Layout


@component
def Box(children, style=None, **kwargs):
    return html.div({"style": style or {}, "children": children, **kwargs})


@component
def Text(children, style=None):
    return html.span({"style": style or {}, "children": children})


@component
def App():
    count, set_count = use_state(0)

    @use_effect
    async def timer():
        while True:
            await asyncio.sleep(1)
            set_count(lambda c: c + 1)

    return Box(
        [
            Text(f"Count: {count}"),
            Box(Text("Nested Box"), style={"margin": 1, "padding": 1, "border_style": "single"}),
        ],
        style={"flex_direction": "column", "width": 80, "height": 20},
    )


def build_yoga_tree(vdom_node) -> YogaNode:
    node = YogaNode()

    # Handle text nodes (strings)
    if isinstance(vdom_node, str):
        # For now, we don't have a specific Text node in our simple wrapper,
        # but in a real implementation we would measure text here.
        # We'll just treat it as a leaf node with some size.
        node.set_style({"width": len(vdom_node), "height": 1})
        return node

    if not isinstance(vdom_node, dict):
        return node

    # Apply styles
    attributes = vdom_node.get("attributes", {})
    style = attributes.get("style", {})
    if style:
        node.set_style(style)

    # Process children
    children = vdom_node.get("children", [])
    for child in children:
        child_node = build_yoga_tree(child)
        node.add_child(child_node)

    return node


def print_layout_tree(node: YogaNode, depth=0):
    layout = node.get_layout()
    indent = "  " * depth
    print(
        f"{indent}Node: left={layout['left']}, top={layout['top']}, width={layout['width']}, height={layout['height']}"
    )
    for child in node.children:
        print_layout_tree(child, depth + 1)


async def run():
    app = App()
    layout = Layout(app)

    async with layout:
        while True:
            update = await layout.render()
            vdom_root = update["model"]

            # The root is usually a fragment or the component wrapper.
            # We need to dig down to find our Box/Text elements.
            # For this prototype, let's assume the first child is our root Box.

            # ReactPy wraps components in a specific structure.
            # Let's inspect what we get first, then build the tree.

            print("\n--- Render Frame ---")
            # print(vdom_root) # Debugging

            # Simplified traversal for the prototype
            # In reality, we'd need a more robust VDOM walker

            # Let's try to build the tree from the root
            yoga_root = build_yoga_tree(vdom_root)

            # Calculate layout
            yoga_root.calculate_layout()

            # Print result
            print_layout_tree(yoga_root)

            await asyncio.sleep(0.1)


if __name__ == "__main__":
    asyncio.run(run())
