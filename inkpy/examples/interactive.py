#!/usr/bin/env python3
"""
Interactive Example - Demonstrates keyboard navigation and focus

Uses Pythonic snake_case API:
- Key properties: key.up_arrow, key.down_arrow, key.return_key
- Style props: flex_direction, border_style, padding
"""

from reactpy import component, use_state

from inkpy import render
from inkpy.components import Box, Text
from inkpy.hooks import use_app, use_input


@component
def SelectList():
    items = ["Option 1", "Option 2", "Option 3", "Exit"]
    selected, set_selected = use_state(0)
    app = use_app()

    def handle_input(input_str, key):
        if key.up_arrow:
            set_selected(lambda s: max(0, s - 1))
        elif key.down_arrow:
            set_selected(lambda s: min(len(items) - 1, s + 1))
        elif key.return_key:
            if selected == len(items) - 1:  # Exit option
                app.exit()

    use_input(handle_input)

    return Box(
        [
            Text(
                f"{'> ' if i == selected else '  '}{item}",
                color="green" if i == selected else "white",
                bold=i == selected,
            )
            for i, item in enumerate(items)
        ],
        flex_direction="column",
        border_style="single",
        padding=1,
    )


if __name__ == "__main__":
    instance = render(SelectList())
    try:
        import asyncio

        asyncio.run(instance.wait_until_exit())
    except KeyboardInterrupt:
        instance.unmount()
