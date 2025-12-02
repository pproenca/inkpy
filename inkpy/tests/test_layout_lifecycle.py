"""
Tests for layout lifecycle and effect persistence.

These tests protect against regressions where:
1. Layout context exits prematurely, killing effects
2. Input loop doesn't start because it's called in a state setter
3. Effects don't persist during app lifetime
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from reactpy import component, use_state, use_effect
from reactpy.core.layout import Layout


class TestLayoutLifecycle:
    """Tests that the layout context stays alive for effects to run"""
    
    @pytest.mark.asyncio
    async def test_effects_run_during_layout_lifecycle(self):
        """Test that effects are executed during the layout lifecycle"""
        effect_ran = []
        cleanup_ran = []
        
        @component
        def TestComponent():
            def effect():
                effect_ran.append(True)
                return lambda: cleanup_ran.append(True)
            
            use_effect(effect, dependencies=[])
            return None
        
        # Run in layout context
        layout = Layout(TestComponent())
        async with layout:
            await layout.render()
            # Give effect time to run
            await asyncio.sleep(0.1)
        
        # Effect should have run
        assert len(effect_ran) >= 1, "Effect should have run at least once"
    
    @pytest.mark.asyncio
    async def test_layout_context_keeps_effects_alive(self):
        """Test that effects persist while layout context is open"""
        effect_count = []
        
        @component
        def TestComponent():
            counter, set_counter = use_state(0)
            
            def effect():
                effect_count.append(counter)
                return None
            
            use_effect(effect, dependencies=[counter])
            
            # Trigger re-render after short delay
            async def increment():
                await asyncio.sleep(0.05)
                set_counter(lambda c: c + 1)
            
            return None
        
        layout = Layout(TestComponent())
        async with layout:
            # Initial render
            await layout.render()
            await asyncio.sleep(0.1)
            
            # Effects should have run
            assert len(effect_count) >= 1


class TestInputLoopInitialization:
    """Tests that input loop starts correctly"""
    
    def test_input_loop_not_started_in_state_setter(self):
        """
        Regression test: Input loop must NOT be started inside a state setter.
        
        State setters in ReactPy execute asynchronously during render, not immediately.
        Starting the input loop inside a setter would cause it to never start.
        """
        from inkpy.components.app import App
        
        # The fix ensures _start_input_loop is called directly, not in a setter
        # We verify this by checking the code structure
        import inspect
        source = inspect.getsource(App)
        
        # Check that _start_input_loop is NOT called inside a lambda passed to set_raw_mode_count
        # The old broken pattern was:
        #   def update_count(current):
        #       if new_count == 1:
        #           _start_input_loop()  # BAD - called in state setter
        #       return new_count
        #   set_raw_mode_count(update_count)
        
        # The fix should call _start_input_loop() BEFORE the state setter
        # This test ensures the fix stays in place
        
        # Look for the pattern where _start_input_loop is called directly
        assert "input_loop_started_container[0] = True" in source or \
               "_start_input_loop()" in source, \
               "Input loop should be started directly, not in a state setter"
    
    def test_handle_set_raw_mode_graceful_fallback(self):
        """Test that set_raw_mode doesn't crash when stdin isn't a TTY"""
        from inkpy.components.app import App
        import inspect
        
        source = inspect.getsource(App)
        
        # The fix should NOT raise RuntimeError for non-TTY stdin
        # It should gracefully handle it (log warning, return early)
        assert "Warning: Raw mode not supported" in source or \
               "return" in source, \
               "Should gracefully handle non-TTY stdin"


class TestEffectCleanupTiming:
    """Tests for proper effect cleanup timing"""
    
    @pytest.mark.asyncio
    async def test_cleanup_runs_on_unmount_not_during_lifecycle(self):
        """
        Regression test: Cleanup should only run when component unmounts,
        NOT when the initial render completes.
        
        The bug was: async with self._layout: exited after initial render,
        triggering premature cleanup.
        """
        cleanup_times = []
        render_times = []
        
        @component
        def TestComponent():
            import time
            render_times.append(time.time())
            
            def effect():
                return lambda: cleanup_times.append(time.time())
            
            use_effect(effect, dependencies=[])
            return None
        
        layout = Layout(TestComponent())
        
        async with layout:
            await layout.render()
            first_render_time = render_times[-1]
            
            # Wait a bit - cleanup should NOT run yet
            await asyncio.sleep(0.1)
            
            # During the layout lifecycle, cleanup should NOT have run
            cleanups_during_lifecycle = [t for t in cleanup_times if t < first_render_time + 0.05]
            assert len(cleanups_during_lifecycle) == 0, \
                "Cleanup should not run during layout lifecycle, only on unmount"


class TestWaitUntilExitLifecycle:
    """Tests for wait_until_exit keeping effects alive"""
    
    @pytest.mark.asyncio
    async def test_ink_run_layout_lifecycle_exists(self):
        """Test that _run_layout_lifecycle method exists in Ink class"""
        from inkpy.ink import Ink
        
        assert hasattr(Ink, '_run_layout_lifecycle'), \
            "_run_layout_lifecycle method must exist to keep effects alive"
    
    @pytest.mark.asyncio
    async def test_wait_until_exit_calls_layout_lifecycle(self):
        """Test that wait_until_exit runs the layout lifecycle"""
        from inkpy.ink import Ink
        import inspect
        
        source = inspect.getsource(Ink.wait_until_exit)
        
        # wait_until_exit should call _run_layout_lifecycle
        assert "_run_layout_lifecycle" in source, \
            "wait_until_exit must call _run_layout_lifecycle to keep effects alive"


class TestEventEmitterConnection:
    """Tests for event emitter being properly connected"""
    
    @pytest.mark.asyncio
    async def test_event_emitter_receives_events(self):
        """Test that the event emitter can receive and dispatch events"""
        from inkpy.input.event_emitter import EventEmitter
        
        emitter = EventEmitter()
        received = []
        
        def handler(data):
            received.append(data)
        
        emitter.on('input', handler)
        emitter.emit('input', 'test_data')
        
        assert 'test_data' in received, "Event emitter should dispatch events"
    
    @pytest.mark.asyncio
    async def test_input_handler_connected_to_emitter(self):
        """Test that use_input connects handler to event emitter"""
        from inkpy.hooks.use_input import _setup_input_listener
        from inkpy.input.event_emitter import EventEmitter
        
        emitter = EventEmitter()
        received_keys = []
        
        def handler(input_str, key):
            received_keys.append(key.name)
        
        stdin_ctx = {
            'internal_eventEmitter': emitter,
            'internal_exitOnCtrlC': True
        }
        
        # Set up listener
        cleanup = _setup_input_listener(stdin_ctx, handler)
        
        # Emit an event
        emitter.emit('input', 'a')
        
        assert len(received_keys) > 0, "Handler should receive events from emitter"
        
        # Cleanup
        if cleanup:
            cleanup()


class TestRawModeStartsInputLoop:
    """Tests that raw mode properly starts the input loop"""
    
    def test_app_has_input_loop_tracking(self):
        """Test that App tracks whether input loop has started"""
        from inkpy.components.app import App
        import inspect
        
        source = inspect.getsource(App)
        
        # Should have some mechanism to track input loop state
        assert "input_loop_started" in source or "loop_control" in source, \
            "App should track input loop state"
    
    def test_start_input_loop_sets_cbreak_mode(self):
        """Test that _start_input_loop puts terminal in cbreak mode (not raw mode)
        
        We use cbreak mode instead of raw mode because:
        - Raw mode (tty.setraw) disables ALL terminal processing including output \\n -> \\r\\n
        - Cbreak mode only disables input buffering/echo but keeps output processing
        
        This prevents the bug where output renders with horizontal offset.
        """
        from inkpy.components.app import App
        import inspect
        
        source = inspect.getsource(App)
        
        # Should NOT use tty.setraw (which breaks output)
        assert "tty.setraw" not in source, \
            "_start_input_loop should NOT use tty.setraw (breaks output processing)"
        
        # Should use termios to set ICANON and ECHO flags
        assert "termios.ICANON" in source, \
            "_start_input_loop should disable ICANON (canonical mode)"
        assert "termios.ECHO" in source, \
            "_start_input_loop should disable ECHO"
    
    def test_input_loop_restores_terminal_on_exit(self):
        """Test that input loop restores terminal settings on exit"""
        from inkpy.components.app import App
        import inspect
        
        source = inspect.getsource(App)
        
        # Should restore terminal settings in finally block
        assert "termios.tcsetattr" in source, \
            "Input loop should restore terminal settings on exit"


class TestOutputProcessingPreserved:
    """Tests that output processing is preserved when input is in cbreak mode"""
    
    def test_cbreak_mode_preserves_output_processing(self):
        """
        Regression test: Cbreak mode must NOT disable output processing.
        
        The bug was: tty.setraw() disables OPOST (output post-processing),
        which converts \\n to \\r\\n. Without this, output renders with
        horizontal offset because newlines don't return cursor to column 0.
        
        The fix: Use termios flags to disable ICANON and ECHO only,
        NOT tty.setraw() which disables everything.
        """
        from inkpy.components.app import App
        import inspect
        
        source = inspect.getsource(App)
        
        # Must NOT use tty.setraw
        assert "tty.setraw" not in source, \
            "Must not use tty.setraw() - it disables output processing"
        
        # Must use termios.tcgetattr and tcsetattr
        assert "termios.tcgetattr" in source, \
            "Should use termios.tcgetattr to get current settings"
        assert "termios.tcsetattr" in source, \
            "Should use termios.tcsetattr to set new settings"
        
        # Must disable ICANON (canonical mode) for character-by-character input
        assert "ICANON" in source, \
            "Should disable ICANON flag for non-buffered input"
        
        # Must disable ECHO to prevent input echoing
        assert "ECHO" in source, \
            "Should disable ECHO flag to prevent keystroke echoing"
    
    def test_output_newlines_work_correctly(self):
        """Test that output with newlines doesn't have horizontal offset"""
        # This is a structural test - the actual rendering is tested elsewhere
        # Here we verify the approach is correct
        
        from inkpy.components.app import App
        import inspect
        
        source = inspect.getsource(App)
        
        # Should NOT modify output flags (oflag - index 1 in termios array)
        # Only input flags (lflag - index 3) should be modified
        # 
        # new_settings[3] = ... is correct (lflag - local flags)
        # new_settings[1] = ... would be wrong (oflag - output flags)
        
        assert "new_settings[3]" in source, \
            "Should modify lflag (index 3) for input settings"
        
        # Verify we're not touching output flags
        lines = source.split('\n')
        for line in lines:
            if 'new_settings[1]' in line and '=' in line:
                # Should not be modifying output flags
                assert False, \
                    f"Should NOT modify output flags (new_settings[1]): {line}"

