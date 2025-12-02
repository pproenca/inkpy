"""
Render function - Public API for rendering InkPy applications
"""

import sys
from typing import Callable, Optional, TextIO

from inkpy.ink import Ink
from inkpy.instances import instances


class Instance:
    """Represents a rendered Ink application instance"""

    def __init__(self, ink: Ink):
        self._ink = ink

    def rerender(self, node):
        """Re-render with a new component tree"""
        self._ink.render(node)

    def render_sync(self):
        """Render immediately without waiting for wait_until_exit().

        This is useful for tests that need immediate output.
        Note: Effects will NOT persist - for persistent effects, use wait_until_exit().
        """
        self._ink.render_sync()

    def unmount(self, error: Optional[Exception] = None):
        """Unmount the application"""
        self._ink.unmount(error)

    async def wait_until_exit(self):
        """Wait until the application exits"""
        return await self._ink.wait_until_exit()

    def clear(self):
        """Clear the output"""
        self._ink.clear()

    def cleanup(self):
        """Remove instance from registry"""
        instances.delete(self._ink.options["stdout"])


def render(
    node,
    stdout: Optional[TextIO] = None,
    stdin: Optional[TextIO] = None,
    stderr: Optional[TextIO] = None,
    debug: bool = False,
    exit_on_ctrl_c: bool = True,
    patch_console: bool = True,
    max_fps: int = 30,
    incremental_rendering: bool = False,
) -> Instance:
    """
    Mount a component and render the output.

    For interactive apps, call wait_until_exit() after render() to run the
    main loop. For immediate output (tests), call render_sync() on the instance.

    Args:
        node: ReactPy component to render
        stdout: Output stream (default: sys.stdout)
        stdin: Input stream (default: sys.stdin)
        stderr: Error stream (default: sys.stderr)
        debug: Enable debug mode (calls render_sync() automatically)
        exit_on_ctrl_c: Exit on Ctrl+C
        patch_console: Patch console methods
        max_fps: Maximum frames per second
        incremental_rendering: Enable incremental rendering

    Returns:
        Instance object with rerender, unmount, wait_until_exit, clear methods
    """
    options = {
        "stdout": stdout or sys.stdout,
        "stdin": stdin or sys.stdin,
        "stderr": stderr or sys.stderr,
        "debug": debug,
        "exit_on_ctrl_c": exit_on_ctrl_c,
        "patch_console": patch_console,
        "max_fps": max_fps,
        "incremental_rendering": incremental_rendering,
    }

    # Get or create Ink instance for this stdout
    ink = get_instance(options["stdout"], lambda: Ink(**options))
    ink.render(node)

    instance = Instance(ink)

    # In debug mode, render immediately for backward compatibility with tests
    if debug:
        instance.render_sync()

    return instance


def get_instance(stdout: TextIO, factory: Callable[[], Ink]) -> Ink:
    """Get or create Ink instance for stdout stream"""
    instance = instances.get(stdout)
    if instance is None:
        instance = factory()
        instances.set(stdout, instance)
    return instance
