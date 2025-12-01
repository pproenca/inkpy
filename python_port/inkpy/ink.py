"""
Ink class - Main entry point for InkPy applications
"""
import asyncio
from typing import Optional, TextIO, Callable, Dict, Any
from inkpy.dom import create_node, DOMElement
from reactpy.core.layout import Layout
from inkpy.backend.tui_backend import TUIBackend

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
        }
        
        self.root_node: DOMElement = create_node('ink-root')
        self.root_node.on_compute_layout = self.calculate_layout
        
        self.is_unmounted: bool = False
        self.last_output: str = ''
        self.last_output_height: int = 0
        self.last_terminal_width: int = self.get_terminal_width()
        
        self._exit_promise: Optional[asyncio.Future] = None
        self._layout: Optional[Layout] = None
        self._backend = TUIBackend()
    
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
    
    def on_render(self):
        """Callback when layout changes (renders to output)"""
        if self.is_unmounted:
            return
        
        # Render logic will be implemented in Task 7.2
        pass
    
    def unmount(self, error: Optional[Exception] = None):
        """Clean up and exit"""
        self.is_unmounted = True
        
        if self._exit_promise and not self._exit_promise.done():
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
        # Implementation will clear terminal output
        pass
    
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

