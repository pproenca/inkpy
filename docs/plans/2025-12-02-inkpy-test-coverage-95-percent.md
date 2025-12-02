# InkPy Test Coverage Plan: 95-100%

> **Goal:** Achieve 95-100% test coverage with balanced integration and unit tests
> **Tech Stack:** Python 3.14, pytest, pytest-cov, ReactPy, custom reconciler
> **Skills Reference:** See @.cursor/skills/test-driven-development.md for TDD protocol
> **Current Coverage:** 80% (716 missing lines across 3521 statements)

---

## Coverage Analysis Summary

### Files with Lowest Coverage (Priority Targets)

| File | Coverage | Missing Lines | Priority |
|------|----------|---------------|----------|
| `components/static.py` | 38% | 8 | High |
| `components/app.py` | 42% | 93 | High |
| `components/text.py` | 56% | 23 | High |
| `renderer/colorize.py` | 59% | 28 | Medium |
| `renderer/renderer.py` | 61% | 12 | Medium |
| `reconciler/app_hooks.py` | 64% | 39 | High |
| `renderer/render_node.py` | 66% | 53 | Medium |
| `ink.py` | 67% | 107 | High |
| `hooks/use_stderr.py` | 67% | 2 | Low |
| `hooks/use_stdout.py` | 67% | 2 | Low |
| `hooks/use_focus_manager.py` | 67% | 2 | Low |
| `layout/yoga_node.py` | 73% | 36 | Medium |
| `reconciler/components.py` | 74% | 17 | Medium |
| `hooks/use_is_screen_reader_enabled.py` | 75% | 2 | Low |
| `backend/tui_backend.py` | 79% | 45 | Medium |
| `reconciler/focus_hooks.py` | 79% | 20 | Medium |
| `hooks/use_input.py` | 79% | 10 | Medium |
| `layout/styles.py` | 79% | 42 | Medium |

### Testing Strategy

**Balance: 60% Integration / 40% Unit**

For an interactive TUI library like InkPy:
- **Integration tests** verify end-to-end behavior (render → output)
- **Unit tests** verify isolated logic (colorize, text wrapping, parsing)

---

## Phase 1: Low-Hanging Fruit (Quick Wins)

### Task 1.1: Test Static Component

**Files:**
- Test: `tests/test_static_component.py`
- Target: `inkpy/components/static.py` (38% → 90%+)

**Missing Coverage:** Lines 35-51 (the entire render logic)

**Step 1: Write failing test**
```python
# tests/test_static_component.py
import pytest
from inkpy.reconciler import component, Element
from inkpy.reconciler.reconciler import Reconciler
from inkpy.components.static import Static
from inkpy.components.text import Text


def test_static_renders_items():
    """Static component should render items as static output"""
    items = ["Item 1", "Item 2", "Item 3"]
    
    @component
    def render_item(item, idx):
        return Text(f"{idx}: {item}")
    
    element = Static(items=items, children=render_item)
    
    reconciler = Reconciler()
    dom = reconciler.render(element)
    
    # Static items should be marked with internal_static
    assert dom is not None


def test_static_incremental_rendering():
    """Static should only render new items on subsequent renders"""
    items = ["Item 1"]
    
    @component
    def render_item(item, idx):
        return Text(item)
    
    # First render
    element1 = Static(items=items, children=render_item)
    
    # Add more items
    items.append("Item 2")
    element2 = Static(items=items, children=render_item)
    
    # Verify incremental behavior
    # (implementation detail: index tracking)
```

**Step 2: Run test to verify it fails**
```bash
uv run pytest tests/test_static_component.py -v
```
Expected: FAIL (Static component not properly testable with reconciler)

**Step 3: Write minimal implementation or adjust test approach**

**Step 4: Run test to verify it passes**

---

### Task 1.2: Test Colorize Functions (RGB, Hex, ANSI256)

**Files:**
- Modify: `tests/test_colorize.py`
- Target: `inkpy/renderer/colorize.py` (59% → 95%+)

**Missing Coverage:** Lines 68-69, 80-81, 101-113, 118-130, 135-140

**Step 1: Write failing tests**
```python
# Add to tests/test_colorize.py

def test_colorize_integer_background():
    """Test 256-color palette for background"""
    result = colorize("test", 200, "background")
    assert "\x1b[48;5;200m" in result
    assert "test" in result


def test_colorize_integer_out_of_range():
    """Test integer color out of 0-255 range returns text unchanged"""
    result = colorize("test", 300, "foreground")
    assert result == "test"
    
    result = colorize("test", -1, "foreground")
    assert result == "test"


def test_colorize_short_hex():
    """Test short hex format (#RGB)"""
    result = colorize("test", "#F00", "foreground")
    # #F00 expands to #FF0000 → RGB(255, 0, 0)
    assert "\x1b[38;2;" in result


def test_colorize_short_hex_background():
    """Test short hex format for background"""
    result = colorize("test", "#0F0", "background")
    assert "\x1b[48;2;" in result


def test_colorize_rgb_format():
    """Test rgb(r, g, b) format"""
    result = colorize("test", "rgb(255, 128, 0)", "foreground")
    assert "\x1b[38;2;255;128;0m" in result


def test_colorize_rgb_background():
    """Test rgb() format for background"""
    result = colorize("test", "rgb(100, 100, 100)", "background")
    assert "\x1b[48;2;100;100;100m" in result


def test_colorize_rgb_clamping():
    """Test RGB values are clamped to 0-255"""
    result = colorize("test", "rgb(300, -50, 100)", "foreground")
    # Should clamp to rgb(255, 0, 100)
    assert "\x1b[38;2;255;0;100m" in result


def test_colorize_ansi256_format():
    """Test ansi256(n) format"""
    result = colorize("test", "ansi256(100)", "foreground")
    assert "\x1b[38;5;100m" in result


def test_colorize_ansi256_background():
    """Test ansi256() format for background"""
    result = colorize("test", "ansi256(50)", "background")
    assert "\x1b[48;5;50m" in result


def test_colorize_ansi256_out_of_range():
    """Test ansi256 with invalid values"""
    result = colorize("test", "ansi256(300)", "foreground")
    assert result == "test"


def test_colorize_invalid_hex():
    """Test invalid hex format returns text unchanged"""
    result = colorize("test", "#GGGGGG", "foreground")
    assert result == "test"


def test_colorize_unknown_format():
    """Test unknown color format returns text unchanged"""
    result = colorize("test", "not-a-color", "foreground")
    assert result == "test"
```

**Step 2: Run test**
```bash
uv run pytest tests/test_colorize.py -v
```

---

### Task 1.3: Test stdout/stderr/focus_manager hooks

**Files:**
- Create: `tests/test_hooks_complete.py`
- Target: `use_stdout.py`, `use_stderr.py`, `use_focus_manager.py` (67% → 100%)

**Missing Coverage:** 2 lines each (the actual hook implementations)

**Step 1: Write failing tests**
```python
# tests/test_hooks_complete.py
import pytest
from inkpy.hooks.use_stdout import use_stdout
from inkpy.hooks.use_stderr import use_stderr
from inkpy.hooks.use_focus_manager import use_focus_manager
from inkpy.reconciler.hooks import set_current_fiber
from inkpy.reconciler.fiber import Fiber


def test_use_stdout_returns_context():
    """use_stdout should return stdout context values"""
    # Set up fiber context
    fiber = Fiber(component=lambda: None, props={})
    set_current_fiber(fiber)
    
    result = use_stdout()
    
    assert "stdout" in result
    assert "write" in result


def test_use_stderr_returns_context():
    """use_stderr should return stderr context values"""
    fiber = Fiber(component=lambda: None, props={})
    set_current_fiber(fiber)
    
    result = use_stderr()
    
    assert "stderr" in result
    assert "write" in result


def test_use_focus_manager_returns_context():
    """use_focus_manager should return focus manager context"""
    fiber = Fiber(component=lambda: None, props={})
    set_current_fiber(fiber)
    
    result = use_focus_manager()
    
    # Should have focus management methods
    assert hasattr(result, "focus_next") or "focus_next" in result
```

---

## Phase 2: Core Components (Medium Effort)

### Task 2.1: Test App Component Input Handling

**Files:**
- Create: `tests/test_app_component_input.py`
- Target: `inkpy/components/app.py` (42% → 80%+)

**Missing Coverage:** Lines 53-55, 84-126, 131-194, 198-274

**Step 1: Write integration tests for App component**
```python
# tests/test_app_component_input.py
import pytest
import io
from unittest.mock import Mock, patch
from inkpy.components.app import App


class MockStdin:
    """Mock stdin for testing"""
    def __init__(self, is_tty=False):
        self._is_tty = is_tty
        
    def isatty(self):
        return self._is_tty
    
    def fileno(self):
        raise OSError("Not a real file")


def test_app_handles_non_tty_stdin_gracefully():
    """App should handle non-TTY stdin without crashing"""
    mock_stdin = MockStdin(is_tty=False)
    mock_stdout = io.StringIO()
    mock_stderr = io.StringIO()
    
    # This should not raise
    # Test via rendering the component


def test_app_focus_navigation():
    """App should handle Tab/Shift+Tab focus navigation"""
    # Test focus_next and focus_previous functions


def test_app_ctrl_c_exit():
    """App should call on_exit when Ctrl+C received and exit_on_ctrl_c=True"""
    on_exit = Mock()
    # Simulate Ctrl+C input (\x03)


def test_app_escape_resets_focus():
    """App should reset active focus on Escape key"""
    # Simulate Escape input (\x1b)


def test_app_add_remove_focusable():
    """App should track focusable elements"""
    # Test add_focusable and remove_focusable
```

---

### Task 2.2: Test Text Component Rendering Modes

**Files:**
- Modify: `tests/test_text_style_props.py`
- Target: `inkpy/components/text.py` (56% → 90%+)

**Missing Coverage:** Lines 46-76, 124-126, 131-133, 164

**Step 1: Write tests for uncovered text rendering paths**
```python
# Add to tests/test_text_style_props.py

def test_text_with_all_style_props():
    """Test Text with all style props applied"""
    from inkpy.components.text import Text
    
    element = Text(
        "styled",
        color="red",
        backgroundColor="blue",
        bold=True,
        italic=True,
        underline=True,
        strikethrough=True,
        inverse=True,
        dimColor=True,
    )
    
    # Render and verify ANSI codes


def test_text_wrap_modes():
    """Test different text wrap modes"""
    # Test wrap, truncate-end, truncate-middle, truncate-start
```

---

### Task 2.3: Test Ink Class Lifecycle Methods

**Files:**
- Modify: `tests/test_ink_full.py`
- Target: `inkpy/ink.py` (67% → 85%+)

**Missing Coverage:** Lines 205-211, 299, 304-320, 348-368, 415-502, etc.

**Step 1: Write tests for Ink lifecycle**
```python
# Add to tests/test_ink_full.py

def test_ink_throttle_function():
    """Test throttle function behavior"""
    from inkpy.ink import throttle
    import time
    
    call_count = 0
    def increment():
        nonlocal call_count
        call_count += 1
    
    throttled = throttle(increment, 100, leading=True, trailing=True)
    
    # Call multiple times rapidly
    throttled()
    throttled()
    throttled()
    
    # Should have called once immediately (leading)
    assert call_count >= 1
    
    # Wait for trailing call
    time.sleep(0.15)
    assert call_count == 2  # Leading + trailing


def test_ink_screen_reader_mode():
    """Test Ink in screen reader mode"""
    import io
    from inkpy.ink import Ink
    
    stdout = io.StringIO()
    stdin = io.StringIO()
    stderr = io.StringIO()
    
    ink = Ink(
        stdout=stdout,
        stdin=stdin,
        stderr=stderr,
        is_screen_reader_enabled=True,
    )
    
    assert ink.is_screen_reader_enabled is True


def test_ink_ci_mode():
    """Test Ink behavior in CI environment"""
    import os
    # Set CI environment variable
    with patch.dict(os.environ, {"CI": "true"}):
        # Test CI-specific rendering behavior


def test_ink_resize_handling():
    """Test terminal resize handling"""
    # Test _on_resize method


def test_ink_unmount_cleanup():
    """Test proper cleanup on unmount"""
    # Verify signal handlers are removed
    # Verify console is restored
    # Verify threads are stopped
```

---

## Phase 3: Reconciler & Hooks (Higher Effort)

### Task 3.1: Test app_hooks Input Thread

**Files:**
- Modify: `tests/test_app_input.py`
- Target: `inkpy/reconciler/app_hooks.py` (64% → 90%+)

**Missing Coverage:** Lines 69, 88-137, 178, 197-198, 218, 253

**Step 1: Write tests for input handling**
```python
# tests/test_app_hooks_input.py
import pytest
from unittest.mock import Mock, patch
from inkpy.reconciler.app_hooks import (
    _process_input,
    _start_input_thread,
    _stop_input_thread,
    use_input,
    use_app,
    _app_state,
)


def test_process_input_ctrl_c():
    """_process_input should call exit callback on Ctrl+C"""
    exit_callback = Mock()
    _app_state["exit_callback"] = exit_callback
    _app_state["exit_on_ctrl_c"] = True
    
    _process_input("\x03")  # Ctrl+C
    
    exit_callback.assert_called_once_with(None)


def test_process_input_regular_key():
    """_process_input should call handlers for regular keys"""
    handler = Mock()
    _app_state["input_handlers"] = [handler]
    _app_state["exit_on_ctrl_c"] = False
    
    _process_input("a")
    
    handler.assert_called_once()


def test_use_app_exit():
    """use_app().exit() should call exit callback"""
    exit_callback = Mock()
    _app_state["exit_callback"] = exit_callback
    
    app = use_app()
    app.exit()
    
    exit_callback.assert_called_once_with(None)


def test_use_app_exit_with_error():
    """use_app().exit(error) should pass error to callback"""
    exit_callback = Mock()
    _app_state["exit_callback"] = exit_callback
    
    error = Exception("test error")
    app = use_app()
    app.exit(error)
    
    exit_callback.assert_called_once_with(error)
```

---

### Task 3.2: Test focus_hooks Focus Management

**Files:**
- Modify: `tests/reconciler/test_focus_hooks.py`
- Target: `inkpy/reconciler/focus_hooks.py` (79% → 95%+)

**Missing Coverage:** Lines 91, 106, 112-113, 120, 129-149, 219, 267, 270

**Step 1: Write tests for focus edge cases**
```python
# Add to tests/reconciler/test_focus_hooks.py

def test_use_focus_with_id():
    """use_focus should work with custom focus id"""
    # Test focus with specific id


def test_focus_manager_disable_focus():
    """Focus manager should handle disabled focus state"""
    # Test disable_focus behavior


def test_focus_manager_focus_by_id():
    """Focus manager should focus element by id"""
    # Test focus(id) method
```

---

### Task 3.3: Test reconciler/components.py Edge Cases

**Files:**
- Modify: `tests/reconciler/test_components.py`
- Target: `inkpy/reconciler/components.py` (74% → 95%+)

**Missing Coverage:** Lines 59-60, 112, 118, 120, 122, 128, 130, 140, 142, 185-199

---

## Phase 4: Renderer & Layout (Medium Effort)

### Task 4.1: Test render_node.py Edge Cases

**Files:**
- Modify: `tests/test_render_node.py`
- Target: `inkpy/renderer/render_node.py` (66% → 90%+)

**Missing Coverage:** Lines 100, 104, 148, 163-170, 202-224, 237-285, etc.

**Step 1: Write tests for rendering edge cases**
```python
# Add to tests/test_render_node.py

def test_render_node_with_overflow_hidden():
    """Test rendering with overflow: hidden clipping"""


def test_render_node_with_background_and_border():
    """Test rendering with both background and border"""


def test_render_node_text_wrapping():
    """Test text wrapping in render_node"""


def test_squash_text_nodes():
    """Test squash_text_nodes utility"""
```

---

### Task 4.2: Test renderer.py Full Render Pipeline

**Files:**
- Modify: `tests/test_renderer.py`
- Target: `inkpy/renderer/renderer.py` (61% → 90%+)

**Missing Coverage:** Lines 30, 38-45, 70-76, 91-92

---

### Task 4.3: Test yoga_node.py Layout Methods

**Files:**
- Modify: `tests/test_yoga_node.py`
- Target: `inkpy/layout/yoga_node.py` (73% → 90%+)

**Missing Coverage:** Lines 29, 32, 67-70, 120-164, 201-202

---

### Task 4.4: Test styles.py Style Application

**Files:**
- Modify: `tests/test_styles.py`
- Target: `inkpy/layout/styles.py` (79% → 95%+)

**Missing Coverage:** Lines 45-46, 52-53, 121, 129-177, 182-238, etc.

---

## Phase 5: Backend & Integration (Higher Effort)

### Task 5.1: Test TUI Backend VDOM Processing

**Files:**
- Modify: `tests/test_tui_backend.py`
- Target: `inkpy/backend/tui_backend.py` (79% → 90%+)

**Missing Coverage:** Lines 31, 39-40, 54, 58-76, 97-100, etc.

---

### Task 5.2: Full Integration Tests

**Files:**
- Create: `tests/test_full_integration.py`
- Target: Multiple modules working together

**Step 1: Write end-to-end integration tests**
```python
# tests/test_full_integration.py
import pytest
import io
from inkpy import render
from inkpy.reconciler import component, Element
from inkpy.reconciler.hooks import use_state
from inkpy.components.box import Box
from inkpy.components.text import Text


def test_counter_app_integration():
    """Full integration test for a counter app"""
    stdout = io.StringIO()
    
    @component
    def Counter():
        count, set_count = use_state(0)
        return Box(
            children=[
                Text(f"Count: {count}"),
            ]
        )
    
    ink = render(Counter(), stdout=stdout)
    output = stdout.getvalue()
    
    assert "Count: 0" in output


def test_nested_boxes_integration():
    """Integration test for nested Box components"""


def test_styled_text_integration():
    """Integration test for styled Text components"""


def test_focus_navigation_integration():
    """Integration test for focus navigation"""
```

---

## Task Summary

| Phase | Tasks | Est. Coverage Gain |
|-------|-------|-------------------|
| Phase 1 | 3 tasks (Static, Colorize, Simple Hooks) | +5% |
| Phase 2 | 3 tasks (App, Text, Ink lifecycle) | +5% |
| Phase 3 | 3 tasks (app_hooks, focus_hooks, components) | +3% |
| Phase 4 | 4 tasks (render_node, renderer, yoga, styles) | +4% |
| Phase 5 | 2 tasks (TUI backend, Integration) | +3% |

**Total Estimated Gain:** 20% (80% → 100%)

---

## Execution Order

1. **Start with Phase 1** - Quick wins to build momentum
2. **Phase 2** - Core components that affect many tests
3. **Phase 3** - Reconciler hooks (complex but important)
4. **Phase 4** - Renderer/layout (isolated, can be parallelized)
5. **Phase 5** - Integration tests (validates everything works together)

---

## Verification Commands

After each task:
```bash
# Run specific test file
uv run pytest tests/test_<module>.py -v

# Check coverage for specific module
uv run pytest --cov=inkpy/<module> --cov-report=term-missing tests/test_<module>.py

# Full coverage report
uv run pytest --cov=inkpy --cov-report=html
```

---

## Notes

- **Interactive testing:** Some code paths (raw mode, signal handlers) are difficult to test in CI. Consider marking these with `@pytest.mark.skip_ci` or using mocking.
- **Threading tests:** Use `unittest.mock` to avoid actual thread creation in tests.
- **Terminal tests:** Use `io.StringIO` as mock stdout/stdin for predictable output.

