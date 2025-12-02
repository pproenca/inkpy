"""
Ink class - Main entry point for InkPy applications
"""
import os
import signal
import time
import asyncio
from typing import Optional, TextIO, Callable
from inkpy.dom import create_node, DOMElement
from reactpy.core.layout import Layout
from inkpy.backend.tui_backend import TUIBackend
from inkpy.log_update import create_log_update, LogUpdate
from inkpy.is_in_ci import is_in_ci
from inkpy.wrap_text import wrap_text
from inkpy.reconciler.element import Element
from inkpy.reconciler.reconciler import Reconciler


def erase_lines(count: int) -> str:
    """Generate ANSI escape code to erase n lines"""
    if count <= 0:
        return ''
    # Move cursor up n lines and clear each line
    return '\x1b[1G' + '\x1b[2K\x1b[1A' * count + '\x1b[2K'


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
        self._lifecycle_task: Optional[asyncio.Task] = None
        self._render_event: Optional[asyncio.Event] = None
        self._first_render_complete = asyncio.Event() if asyncio.get_event_loop else None
        
        # Custom reconciler support
        self._reconciler: Optional[Reconciler] = None
        self._using_custom_reconciler: bool = False
        
        # Signal exit handling
        self._unsubscribe_exit: Optional[Callable] = None
        self._setup_exit_handler()
        
        # Terminal resize handling
        self._unsubscribe_resize: Optional[Callable] = None
        if not is_in_ci():
            self._setup_resize_handler()
        
        # Console patching
        self.restore_console: Optional[Callable[[], None]] = None
        if patch_console and not debug:
            from inkpy.console_patch import patch_console
            
            def console_callback(stream: str, data: str):
                """Handle intercepted console output"""
                if stream == 'stdout':
                    self._write_to_stdout(data)
                elif stream == 'stderr':
                    # Filter React error messages (similar to TypeScript version)
                    is_react_message = data.startswith('The above error occurred')
                    if not is_react_message:
                        self._write_to_stderr(data)
            
            self.restore_console = patch_console(
                stdout,
                stderr,
                console_callback
            )
    
    def render(self, node):
        """Render a ReactPy component or custom reconciler Element.
        
        This sets up the component but does NOT enter the ReactPy layout context.
        The layout context is entered in wait_until_exit() to keep effects alive.
        
        For immediate output (tests, non-interactive use), use render_sync().
        """
        if self.is_unmounted:
            return
        
        # Detect if this is a custom reconciler Element
        if isinstance(node, Element):
            self._using_custom_reconciler = True
            self._render_with_custom_reconciler(node)
            return
        
        # Fall back to ReactPy rendering
        self._using_custom_reconciler = False
        
        # Create the App wrapper component
        from inkpy.components.app import App
        self._app_component = App(
            children=node,
            stdin=self.options['stdin'],
            stdout=self.options['stdout'],
            stderr=self.options['stderr'],
            write_to_stdout=self._write_to_stdout,
            write_to_stderr=self._write_to_stderr,
            exit_on_ctrl_c=self.options['exit_on_ctrl_c'],
            on_exit=self.unmount,
        )
        
        # Create the Layout - but don't enter the context yet
        self._layout = Layout(self._app_component)
        
        # For synchronous use (tests), do a one-shot render
        # This creates a temporary context just for the initial render
        self._do_sync_render()
    
    def _render_with_custom_reconciler(self, element: Element):
        """Render using the custom reconciler instead of ReactPy.
        
        The custom reconciler provides synchronous state updates,
        which is essential for interactive applications.
        """
        if self._reconciler is None:
            self._reconciler = Reconciler(
                on_commit=self._on_reconciler_commit,
                on_compute_layout=self.calculate_layout,
            )
        
        # Render the element tree
        self._reconciler.render(element)
    
    def _on_reconciler_commit(self, root_dom: DOMElement):
        """Called after the custom reconciler commits changes to DOM."""
        # Update our root node to point to the reconciler's DOM
        self.root_node = root_dom
        self.root_node.on_compute_layout = self.calculate_layout
        self.root_node.on_render = (
            self.on_render if self._unthrottled else self._throttled_on_render
        )
        self.root_node.on_immediate_render = self.on_render
        
        # Render to terminal
        self.on_render()
    
    def _do_sync_render(self):
        """Do a synchronous one-shot render for immediate output.
        
        This is used for tests and non-interactive use cases.
        For interactive apps, wait_until_exit() handles the full lifecycle.
        """
        if self._layout is None:
            return
        
        try:
            asyncio.get_running_loop()
            # Event loop running - use thread pool
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(self._sync_render_in_new_loop)
                future.result(timeout=5.0)
        except RuntimeError:
            # No event loop - create one
            asyncio.run(self._one_shot_render())
    
    def _sync_render_in_new_loop(self):
        """Run one-shot render in a new event loop"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._one_shot_render())
        finally:
            loop.close()
    
    async def _one_shot_render(self):
        """One-shot render for immediate output (tests/non-interactive).
        
        NOTE: This creates a temporary layout context that immediately closes.
        Effects will NOT persist. For effects, use wait_until_exit().
        """
        if self._layout is None:
            return
        
        async with self._layout:
            update = await self._layout.render()
            vdom = update.get('model') if isinstance(update, dict) else getattr(update, 'model', None)
            
            if vdom:
                self._backend.vdom_to_dom(vdom, self.root_node)
                self.calculate_layout()
                self.on_render()
    
    async def _run_interactive_lifecycle(self):
        """Run the full interactive lifecycle with persistent effects.
        
        This is the ONLY place where we enter the layout context for interactive apps.
        The context stays open until the app exits, keeping effects alive.
        """
        if self._layout is None:
            return
        
        # Re-create layout for a fresh context (don't reuse the one from _do_sync_render)
        self._layout = Layout(self._app_component)
        
        async with self._layout:
            # Initial render
            update = await self._layout.render()
            vdom = update.get('model') if isinstance(update, dict) else getattr(update, 'model', None)
            
            if vdom:
                self._backend.vdom_to_dom(vdom, self.root_node)
                self.calculate_layout()
                self.on_render()
            
            # Keep layout context alive for effects until app exits
            while not self.is_unmounted:
                await asyncio.sleep(0.05)
    
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
        
        # Import renderer
        from inkpy.renderer.renderer import renderer
        
        # Render
        result = renderer(self.root_node, self.is_screen_reader_enabled)
        
        # Handle static output
        has_static_output = result['staticOutput'] and result['staticOutput'] != '\n'
        
        if self.options['debug']:
            if has_static_output:
                self.full_static_output += result['staticOutput']
            self.options['stdout'].write(self.full_static_output + result['output'])
            
            render_time = (time.perf_counter() - start_time) * 1000
            if self.options.get('on_render'):
                metrics = RenderMetrics(render_time=render_time)
                self.options['on_render'](metrics)
            return
        
        # Handle CI mode
        from inkpy.is_in_ci import is_in_ci
        if is_in_ci():
            if has_static_output:
                self.options['stdout'].write(result['staticOutput'])
            self.last_output = result['output']
            self.last_output_height = result['outputHeight']
            
            render_time = (time.perf_counter() - start_time) * 1000
            if self.options.get('on_render'):
                metrics = RenderMetrics(render_time=render_time)
                self.options['on_render'](metrics)
            return
        
        # Handle screen reader mode
        if self.is_screen_reader_enabled:
            if has_static_output:
                # Erase main output before writing new static output
                erase_code = erase_lines(self.last_output_height) if self.last_output_height > 0 else ''
                self.options['stdout'].write(erase_code + result['staticOutput'])
                # After erasing, the last output is gone, so reset its height
                self.last_output_height = 0
            
            # Skip if output hasn't changed and no static output
            if result['output'] == self.last_output and not has_static_output:
                render_time = (time.perf_counter() - start_time) * 1000
                if self.options.get('on_render'):
                    metrics = RenderMetrics(render_time=render_time)
                    self.options['on_render'](metrics)
                return
            
            # Wrap output to terminal width for screen readers
            terminal_width = self.get_terminal_width()
            wrapped_output = wrap_text(result['output'], terminal_width, 'wrap')
            
            # Write output (erase previous if not already erased for static output)
            if has_static_output:
                self.options['stdout'].write(wrapped_output)
            else:
                erase_code = erase_lines(self.last_output_height) if self.last_output_height > 0 else ''
                self.options['stdout'].write(erase_code + wrapped_output)
            
            self.last_output = result['output']
            self.last_output_height = len(wrapped_output.split('\n')) if wrapped_output else 0
            
            render_time = (time.perf_counter() - start_time) * 1000
            if self.options.get('on_render'):
                metrics = RenderMetrics(render_time=render_time)
                self.options['on_render'](metrics)
            return
        
        # Normal mode - use log update
        if has_static_output:
            self.full_static_output += result['staticOutput']
        
        # Check if we need to clear terminal (output height >= terminal rows)
        terminal_rows = getattr(self.options['stdout'], 'rows', 24)
        if self.last_output_height >= terminal_rows:
            # Clear terminal and write everything
            clear_code = '\x1b[2J\x1b[H'  # Clear screen and move cursor to top
            self.options['stdout'].write(clear_code + self.full_static_output + result['output'])
            self.last_output = result['output']
            self.last_output_height = result['outputHeight']
            self.log.sync(result['output'])
            
            render_time = (time.perf_counter() - start_time) * 1000
            if self.options.get('on_render'):
                metrics = RenderMetrics(render_time=render_time)
                self.options['on_render'](metrics)
            return
        
        # Normal incremental update
        if has_static_output:
            # Clear main output before writing static
            self.log.clear()
            self.options['stdout'].write(result['staticOutput'])
            self.log(result['output'])
        elif result['output'] != self.last_output:
            # Only update if output changed
            self.throttled_log(result['output'])
        
        self.last_output = result['output']
        self.last_output_height = result['outputHeight']
        
        render_time = (time.perf_counter() - start_time) * 1000
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
        
        # Restore console if patched
        if self.restore_console:
            self.restore_console()
            self.restore_console = None
        
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
        """Wait for app exit while keeping the interactive lifecycle alive.
        
        This is the entry point for interactive apps. It:
        1. Enters the ReactPy layout context (keeping effects alive)
        2. Does the initial render
        3. Waits until the app exits
        
        For non-interactive use (tests), just call render() without this.
        """
        if self._exit_promise is None:
            self._exit_promise = asyncio.Future()
        
        if self.is_unmounted:
            return
        
        # For custom reconciler, just wait for exit (no async lifecycle needed)
        if self._using_custom_reconciler:
            await self._exit_promise
            return self._exit_promise.result() if self._exit_promise.done() else None
        
        # Run the interactive lifecycle - this keeps effects alive
        await self._run_interactive_lifecycle()
        
        # Return the exit promise result if set
        if self._exit_promise.done():
            return self._exit_promise.result()
        return None
    
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

