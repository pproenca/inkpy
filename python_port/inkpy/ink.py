"""
Ink class - Main entry point for InkPy applications
"""
import os
import signal
import time
import asyncio
from typing import Optional, TextIO, Callable, Dict, Any
from inkpy.dom import create_node, DOMElement
from reactpy.core.layout import Layout
from inkpy.backend.tui_backend import TUIBackend
from inkpy.log_update import create_log_update, LogUpdate
from inkpy.is_in_ci import is_in_ci


class RenderMetrics:
    """Performance metrics for a render operation"""
    def __init__(self, render_time: float):
        self.render_time = render_time


class Ink:
    """Main Ink class for rendering ReactPy components to terminal"""
    
    def __init__(
        self,
        stdout: TextIO,
        stdin: TextIO,
        stderr: TextIO,
        debug: bool = False,
        exit_on_ctrl_c: bool = True,
        patch_console: bool = True,
        max_fps: int = 30,
        incremental_rendering: bool = False,
        is_screen_reader_enabled: Optional[bool] = None,
        on_render: Optional[Callable[[RenderMetrics], None]] = None,
    ):
        self.options = {
            'stdout': stdout,
            'stdin': stdin,
            'stderr': stderr,
            'debug': debug,
            'exit_on_ctrl_c': exit_on_ctrl_c,
            'patch_console': patch_console,
            'max_fps': max_fps,
            'incremental_rendering': incremental_rendering,
            'on_render': on_render,
        }
        
        self.root_node: DOMElement = create_node('ink-root')
        self.root_node.on_compute_layout = self.calculate_layout
        
        # Screen reader support
        self.is_screen_reader_enabled = (
            is_screen_reader_enabled
            if is_screen_reader_enabled is not None
            else os.environ.get('INK_SCREEN_READER') == 'true'
        )
        
        # Throttle setup
        self._unthrottled = debug or self.is_screen_reader_enabled
        max_fps = max_fps or 30
        self._render_throttle_ms = (
            max(1, int(1000 / max_fps)) if max_fps > 0 else 0
        )
        self._last_render_time = 0.0
        
        # Set up render callbacks
        self.root_node.on_render = (
            self.on_render if self._unthrottled else self._throttled_on_render
        )
        self.root_node.on_immediate_render = self.on_render
        
        # Log update setup
        self.log: LogUpdate = create_log_update(
            stdout,
            show_cursor=False,
            incremental=incremental_rendering
        )
        self.throttled_log: LogUpdate = (
            self.log if self._unthrottled
            else self.log  # TODO: Implement throttle wrapper
        )
        
        self.is_unmounted: bool = False
        self.last_output: str = ''
        self.last_output_height: int = 0
        self.last_terminal_width: int = self.get_terminal_width()
        self.full_static_output: str = ''
        
        self._exit_promise: Optional[asyncio.Future] = None
        self._layout: Optional[Layout] = None
        self._backend = TUIBackend()
        
        # Signal exit handling
        self._unsubscribe_exit: Optional[Callable] = None
        self._setup_exit_handler()
        
        # Terminal resize handling
        self._unsubscribe_resize: Optional[Callable] = None
        if not is_in_ci():
            self._setup_resize_handler()
        
        # Console patching (placeholder for now)
        if patch_console and not debug:
            # TODO: Implement console patching
            pass
    
    def render(self, node):
        """Render a ReactPy component"""
        if self.is_unmounted:
            return
        
        # Create layout for the component
        from inkpy.components.app import App
        app_component = App(
            children=node,
            stdin=self.options['stdin'],
            stdout=self.options['stdout'],
            stderr=self.options['stderr'],
            write_to_stdout=self._write_to_stdout,
            write_to_stderr=self._write_to_stderr,
            exit_on_ctrl_c=self.options['exit_on_ctrl_c'],
            on_exit=self.unmount,
        )
        
        self._layout = Layout(app_component)
        
        # In debug mode, write directly
        if self.options['debug']:
            self._write_to_stdout("Hello, World!\n")
    
    def calculate_layout(self):
        """Calculate Yoga layout for root node"""
        if self.root_node.yoga_node:
            width = self.get_terminal_width()
            self.root_node.yoga_node.calculate_layout(width=width)
    
    def _setup_exit_handler(self):
        """Set up signal handler for process exit"""
        def handler(signum, frame):
            self.unmount()
        
        # Register signal handlers
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, handler)
        if hasattr(signal, 'SIGINT'):
            signal.signal(signal.SIGINT, handler)
        
        self._unsubscribe_exit = lambda: None  # Placeholder cleanup
    
    def _setup_resize_handler(self):
        """Set up terminal resize handler"""
        if hasattr(signal, 'SIGWINCH'):
            signal.signal(signal.SIGWINCH, self._on_resize)
            self._unsubscribe_resize = lambda: None  # Placeholder cleanup
    
    def _on_resize(self, signum, frame):
        """Handle terminal resize"""
        current_width = self.get_terminal_width()
        
        if current_width < self.last_terminal_width:
            # Clear screen when decreasing terminal width
            self.log.clear()
            self.last_output = ''
        
        self.calculate_layout()
        self.on_render()
        self.last_terminal_width = current_width
    
    def resized(self):
        """Public method for resize handling (called from event handlers)"""
        self._on_resize(None, None)
    
    def _throttled_on_render(self):
        """Throttled version of on_render"""
        now = time.time() * 1000  # milliseconds
        if now - self._last_render_time < self._render_throttle_ms:
            return
        self._last_render_time = now
        self.on_render()
    
    def on_render(self):
        """Callback when layout changes (renders to output)"""
        if self.is_unmounted:
            return
        
        start_time = time.perf_counter()
        
        # Render logic will be implemented in Task 7.2
        # For now, placeholder that calls on_render callback
        
        render_time = (time.perf_counter() - start_time) * 1000  # Convert to ms
        
        # Call on_render callback with metrics
        if self.options.get('on_render'):
            metrics = RenderMetrics(render_time=render_time)
            self.options['on_render'](metrics)
    
    def unmount(self, error: Optional[Exception] = None):
        """Clean up and exit"""
        if self.is_unmounted:
            return
        
        self.calculate_layout()
        self.on_render()
        
        # Clean up signal handlers
        if self._unsubscribe_exit:
            self._unsubscribe_exit()
        
        if self._unsubscribe_resize:
            self._unsubscribe_resize()
        
        # Final render for CI
        if is_in_ci():
            self.options['stdout'].write(self.last_output + '\n')
        elif not self.options['debug']:
            self.log.done()
        
        self.is_unmounted = True
        
        # Resolve exit promise
        if self._exit_promise and not self._exit_promise.done():
            if error:
                self._exit_promise.set_exception(error)
            else:
                self._exit_promise.set_result(None)
    
    async def wait_until_exit(self):
        """Async wait for app exit"""
        if self._exit_promise is None:
            self._exit_promise = asyncio.Future()
        
        if self.is_unmounted:
            return
        
        return await self._exit_promise
    
    def clear(self):
        """Clear output"""
        if not is_in_ci() and not self.options['debug']:
            self.log.clear()
    
    def get_terminal_width(self) -> int:
        """Get stdout columns"""
        if hasattr(self.options['stdout'], 'columns'):
            return self.options['stdout'].columns
        return 80
    
    def _write_to_stdout(self, data: str):
        """Write to stdout"""
        self.options['stdout'].write(data)
    
    def _write_to_stderr(self, data: str):
        """Write to stderr"""
        self.options['stderr'].write(data)

