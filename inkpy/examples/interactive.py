#!/usr/bin/env python3
"""
Interactive Example - Demonstrates keyboard navigation and focus

Uses Pythonic snake_case API:
- Key properties: key.up_arrow, key.down_arrow, key.return_key
- Style props: flex_direction, border_style, padding
"""
import sys
from reactpy import component, use_state, use_effect
from inkpy import render
from inkpy.components import Box, Text
from inkpy.hooks import use_input, use_app
from inkpy.hooks.use_stdin import use_stdin

@component
def SelectList():
    items = ["Option 1", "Option 2", "Option 3", "Exit"]
    selected, set_selected = use_state(0)
    app = use_app()
    
    # DEBUG: Check if stdin context is available
    stdin_ctx = use_stdin()
    
    def debug_effect():
        print(f"DEBUG: stdin_ctx = {stdin_ctx}", file=sys.stderr)
        print(f"DEBUG: set_raw_mode = {stdin_ctx.get('set_raw_mode') if isinstance(stdin_ctx, dict) else 'not a dict'}", file=sys.stderr)
        print(f"DEBUG: is_raw_mode_supported = {stdin_ctx.get('is_raw_mode_supported') if isinstance(stdin_ctx, dict) else 'not a dict'}", file=sys.stderr)
        return None
    
    use_effect(debug_effect, dependencies=[])
    
    def handle_input(input_str, key):
        print(f"DEBUG: handle_input called with input_str={repr(input_str)}, key.name={key.name}", file=sys.stderr)
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

