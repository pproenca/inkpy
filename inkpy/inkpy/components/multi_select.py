"""
MultiSelect component module.

Provides a multi-choice selection list with checkbox-style selection.
Similar to Ink's MultiSelect component.
"""

from typing import Any, Callable, Optional

from reactpy import component, html
from reactpy.core.hooks import use_effect, use_state

from inkpy.hooks.use_input import use_input
from inkpy.input.keypress import Key


@component
def MultiSelectItem(
    label: str,
    is_highlighted: bool = False,
    is_checked: bool = False,
    highlight_indicator: str = "> ",
    checked_indicator: str = "[x]",
    unchecked_indicator: str = "[ ]",
):
    """
    A single item in the MultiSelect list.

    Args:
        label: Display label for the item
        is_highlighted: Whether this item is currently highlighted (cursor)
        is_checked: Whether this item is selected/checked
        highlight_indicator: Character(s) to show for highlighted item
        checked_indicator: Indicator for checked items
        unchecked_indicator: Indicator for unchecked items
    """
    # Build highlight indicator
    highlight = html.span(
        {"style": {"color": "cyan" if is_highlighted else "transparent"}},
        highlight_indicator if is_highlighted else " " * len(highlight_indicator),
    )

    # Build check indicator
    check = html.span(
        {"style": {"color": "green" if is_checked else "gray"}},
        checked_indicator if is_checked else unchecked_indicator,
    )

    # Build item label
    item_label = html.span(
        {"style": {"color": "white" if is_highlighted else "gray"}},
        f" {label}",
    )

    return html.div(
        {"style": {"flexDirection": "row"}},
        highlight,
        check,
        item_label,
    )


@component
def MultiSelect(
    items: Optional[list[dict[str, Any]]] = None,
    on_submit: Optional[Callable[[list[dict[str, Any]]], None]] = None,
    on_highlight: Optional[Callable[[dict[str, Any]], None]] = None,
    default_selected: Optional[list[Any]] = None,
    highlight_indicator: str = "> ",
    checked_indicator: str = "[x]",
    unchecked_indicator: str = "[ ]",
    focus: bool = True,
    limit: Optional[int] = None,
):
    """
    MultiSelect component for multi-choice selection from a list.

    Args:
        items: List of items with 'label' and 'value' keys
        on_submit: Called with list of selected items when Enter is pressed
        on_highlight: Called with highlighted item when cursor moves
        default_selected: List of values that should be pre-selected
        highlight_indicator: Character(s) to show for highlighted item
        checked_indicator: Indicator for checked items
        unchecked_indicator: Indicator for unchecked items
        focus: Whether input is focused and capturing input
        limit: Maximum number of items that can be selected

    Example:
        @component
        def App():
            items = [
                {"label": "Red", "value": "red"},
                {"label": "Green", "value": "green"},
                {"label": "Blue", "value": "blue"},
            ]

            def handle_submit(selected):
                print(f"Selected: {[item['value'] for item in selected]}")

            return MultiSelect(items=items, on_submit=handle_submit)
    """
    if items is None:
        items = []

    if default_selected is None:
        default_selected = []

    # Track highlighted index (cursor position)
    highlighted_index, set_highlighted_index = use_state(0)

    # Track selected values
    selected_values, set_selected_values = use_state(set(default_selected))

    # Keep index in bounds when items change
    use_effect(
        lambda: set_highlighted_index(min(highlighted_index, max(0, len(items) - 1))),
        [len(items)],
    )

    # Call on_highlight when cursor moves
    def notify_highlight():
        if on_highlight and items and 0 <= highlighted_index < len(items):
            on_highlight(items[highlighted_index])

    use_effect(notify_highlight, [highlighted_index])

    def handle_input(input_str: str, key: Key):
        if not focus or not items:
            return

        # Handle Enter key - submit selected items
        if key.return_key:
            if on_submit:
                selected_items = [item for item in items if item.get("value") in selected_values]
                on_submit(selected_items)
            return

        # Handle Space key - toggle selection
        if input_str == " ":
            if 0 <= highlighted_index < len(items):
                item_value = items[highlighted_index].get("value")
                if item_value in selected_values:
                    # Deselect
                    set_selected_values(lambda s: s - {item_value})
                else:
                    # Select (if within limit)
                    if limit is None or len(selected_values) < limit:
                        set_selected_values(lambda s: s | {item_value})
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

        # Handle 'a' for select all
        if input_str == "a":
            if limit is None:
                all_values = {item.get("value") for item in items}
                set_selected_values(all_values)
            return

        # Handle 'n' for select none (deselect all)
        if input_str == "n":
            set_selected_values(set())
            return

    # Set up input handling
    use_input(handle_input, is_active=focus)

    # Render items
    children = []
    for idx, item in enumerate(items):
        is_highlighted = idx == highlighted_index
        is_checked = item.get("value") in selected_values

        children.append(
            html.div(
                {"key": str(idx)},
                MultiSelectItem(
                    label=item.get("label", str(item.get("value", ""))),
                    is_highlighted=is_highlighted,
                    is_checked=is_checked,
                    highlight_indicator=highlight_indicator,
                    checked_indicator=checked_indicator,
                    unchecked_indicator=unchecked_indicator,
                ),
            )
        )

    return html.div(
        {"style": {"flexDirection": "column"}},
        *children,
    )
