"""
SelectInput component module.

Provides a single-choice selection list with arrow key navigation.
Similar to Ink's SelectInput component.
"""

from typing import Any, Callable, Optional

from reactpy import component, html
from reactpy.core.hooks import use_effect, use_state

from inkpy.hooks.use_input import use_input
from inkpy.input.keypress import Key


@component
def SelectInputItem(
    label: str,
    is_selected: bool = False,
    indicator: str = "> ",
    indicator_component: Optional[Any] = None,
    item_component: Optional[Any] = None,
):
    """
    A single item in the SelectInput list.

    Args:
        label: Display label for the item
        is_selected: Whether this item is currently highlighted
        indicator: Character(s) to show for selected item
        indicator_component: Custom component for indicator
        item_component: Custom component for item
    """
    # Build indicator
    if indicator_component:
        ind = indicator_component
    else:
        ind = html.span(
            {"style": {"color": "cyan" if is_selected else "transparent"}},
            indicator if is_selected else " " * len(indicator),
        )

    # Build item label
    if item_component:
        item = item_component
    else:
        item = html.span(
            {"style": {"color": "white" if is_selected else "gray"}},
            label,
        )

    return html.div(
        {"style": {"flexDirection": "row"}},
        ind,
        item,
    )


@component
def SelectInput(
    items: Optional[list[dict[str, Any]]] = None,
    on_select: Optional[Callable[[dict[str, Any]], None]] = None,
    on_highlight: Optional[Callable[[dict[str, Any]], None]] = None,
    initial_index: int = 0,
    indicator: str = "> ",
    indicator_component: Optional[Any] = None,
    item_component: Optional[Callable[[dict[str, Any], bool], Any]] = None,
    focus: bool = True,
    limit: Optional[int] = None,
):
    """
    SelectInput component for single-choice selection from a list.

    Args:
        items: List of items with 'label' and 'value' keys
        on_select: Called with selected item when Enter is pressed
        on_highlight: Called with highlighted item when selection changes
        initial_index: Initial highlighted index
        indicator: Character(s) to show for highlighted item
        indicator_component: Custom component for indicator
        item_component: Custom render function for items
        focus: Whether input is focused and capturing input
        limit: Maximum number of items to display (scrolling)

    Example:
        @component
        def App():
            items = [
                {"label": "Red", "value": "red"},
                {"label": "Green", "value": "green"},
                {"label": "Blue", "value": "blue"},
            ]

            def handle_select(item):
                print(f"Selected: {item['value']}")

            return SelectInput(items=items, on_select=handle_select)
    """
    if items is None:
        items = []

    # Track highlighted index
    highlighted_index, set_highlighted_index = use_state(initial_index)

    # Keep index in bounds when items change
    use_effect(
        lambda: set_highlighted_index(min(highlighted_index, max(0, len(items) - 1))),
        [len(items)],
    )

    # Call on_highlight when selection changes
    def notify_highlight():
        if on_highlight and items and 0 <= highlighted_index < len(items):
            on_highlight(items[highlighted_index])

    use_effect(notify_highlight, [highlighted_index])

    def handle_input(input_str: str, key: Key):
        if not focus or not items:
            return

        # Handle Enter key - select current item
        if key.return_key:
            if on_select and 0 <= highlighted_index < len(items):
                on_select(items[highlighted_index])
            return

        # Handle arrow keys
        if key.up_arrow:
            set_highlighted_index(lambda idx: max(0, idx - 1))
            return

        if key.down_arrow:
            set_highlighted_index(lambda idx: min(len(items) - 1, idx + 1))
            return

        # Handle vim-style navigation
        if input_str == "k":
            set_highlighted_index(lambda idx: max(0, idx - 1))
            return

        if input_str == "j":
            set_highlighted_index(lambda idx: min(len(items) - 1, idx + 1))
            return

    # Set up input handling
    use_input(handle_input, is_active=focus)

    # Determine visible items (for scrolling)
    if limit and len(items) > limit:
        # Calculate scroll window
        start = max(0, highlighted_index - limit // 2)
        end = min(len(items), start + limit)
        if end - start < limit:
            start = max(0, end - limit)
        # Adjust highlighted index for display
        visible_indices = range(start, end)
    else:
        visible_indices = range(len(items))

    # Render items
    children = []
    for i, idx in enumerate(visible_indices):
        item = items[idx]
        is_highlighted = idx == highlighted_index

        if item_component:
            # Use custom item component
            rendered_item = item_component(item, is_highlighted)
            children.append(html.div({"key": str(idx)}, rendered_item))
        else:
            # Use default item rendering
            children.append(
                html.div(
                    {"key": str(idx)},
                    SelectInputItem(
                        label=item.get("label", str(item.get("value", ""))),
                        is_selected=is_highlighted,
                        indicator=indicator,
                        indicator_component=indicator_component,
                    ),
                )
            )

    return html.div(
        {"style": {"flexDirection": "column"}},
        *children,
    )
