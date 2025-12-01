#!/usr/bin/env python3
"""
Counter Example - Demonstrates async state updates
"""
import asyncio
from reactpy import component, use_state, use_effect
from inkpy import render
from inkpy.components import Box, Text

@component
def Counter():
    count, set_count = use_state(0)
    
    @use_effect(dependencies=[])
    async def start_timer():
        while True:
            await asyncio.sleep(1)
            set_count(lambda c: c + 1)
    
    return Box(
        Text(f"Count: {count}", color="green", bold=True),
        border_style="round",
        padding=1,
    )

if __name__ == "__main__":
    instance = render(Counter())
    try:
        asyncio.run(instance.wait_until_exit())
    except KeyboardInterrupt:
        instance.unmount()

