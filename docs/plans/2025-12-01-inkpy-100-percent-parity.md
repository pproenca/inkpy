# InkPy 100% Feature Parity Implementation Plan

> **Goal:** Complete the remaining 15% of InkPy to achieve full feature parity with TypeScript Ink, enabling production-ready CLI applications with terminal rendering, input handling, and accessibility support.

> **Tech Stack:** Python 3.9+, ReactPy, Poga (Yoga bindings), pytest

> **Reference:** TypeScript Ink source at `/Users/pedroproenca/Documents/Projects/ink/src/`

> **Current Status:** 85% complete (145 tests passing, 4 xfail)

---

## Overview

### Completed ✅
- Renderer (output, colorize, borders, background, render_node)
- Layout (yoga_node, text_node, styles)
- Input (keypress)
- Components (Box, Text, Static, Newline, Spacer, Transform)
- Hooks (use_input, use_stdin, use_stdout, use_stderr, use_app, use_focus, use_focus_manager)
- DOM (create_node, append_child, squash_text_nodes)

### Remaining 🔴
1. **log_update.py** - Terminal output management
2. **get_max_width.py** - Max width helper
3. **ink.py** - Complete main class
4. **measure_element.py** - Public API function
5. **renderer.py** - Screen reader mode
6. **AccessibilityContext** - Screen reader context
7. **use_is_screen_reader_enabled.py** - Screen reader hook
8. **E2E Examples** - counter.py, interactive.py
9. **Documentation** - Type hints, README

---

## Phase 6: Infrastructure Completion

### Task 6.1: Log Update Module (CRITICAL)
**Files:** `python_port/inkpy/log_update.py`, `python_port/tests/test_log_update.py`

**Purpose:** Manages terminal output with cursor control, line erasing, and incremental rendering.

**Step 1:** Write failing tests
```python
# test_log_update.py
import io
import pytest
from inkpy.log_update import create_log_update

def test_log_update_writes_output():
    """Test basic output writing"""
    stream = io.StringIO()
    log = create_log_update(stream)
    log("Hello, World!")
    output = stream.getvalue()
    assert "Hello, World!" in output

def test_log_update_erases_previous():
    """Test that previous output is erased before new output"""
    stream = io.StringIO()
    log = create_log_update(stream)
    log("First")
    log("Second")
    output = stream.getvalue()
    # Should contain erase sequence before "Second"
    assert "\x1b[" in output  # ANSI escape

def test_log_update_clear():
    """Test clearing output"""
    stream = io.StringIO()
    log = create_log_update(stream)
    log("Content")
    log.clear()
    output = stream.getvalue()
    assert "\x1b[" in output  # Erase sequence

def test_log_update_done():
    """Test done() restores cursor"""
    stream = io.StringIO()
    log = create_log_update(stream, show_cursor=False)
    log("Content")
    log.done()
    output = stream.getvalue()
    # Should show cursor at end
    assert "\x1b[?25h" in output  # Show cursor sequence

def test_log_update_hides_cursor():
    """Test cursor is hidden during rendering"""
    stream = io.StringIO()
    log = create_log_update(stream, show_cursor=False)
    log("Content")
    output = stream.getvalue()
    assert "\x1b[?25l" in output  # Hide cursor sequence

def test_incremental_rendering():
    """Test incremental mode only updates changed lines"""
    stream = io.StringIO()
    log = create_log_update(stream, incremental=True)
    log("Line 1\nLine 2\nLine 3")
    log("Line 1\nChanged\nLine 3")
    # Incremental should skip unchanged lines

def test_log_update_sync():
    """Test sync() updates state without writing"""
    stream = io.StringIO()
    log = create_log_update(stream)
    log.sync("Synced content")
    output = stream.getvalue()
    assert output == ""  # Nothing written
```

**Step 2:** Implement log_update.py
```python
"""
Log Update - Terminal output management with cursor control and incremental rendering.

Ported from: src/log-update.ts
"""
from typing import TextIO, Optional, Callable, List

# ANSI escape sequences
HIDE_CURSOR = "\x1b[?25l"
SHOW_CURSOR = "\x1b[?25h"
ERASE_LINE = "\x1b[2K"
CURSOR_UP = "\x1b[{n}A"
CURSOR_NEXT_LINE = "\x1b[1E"

def erase_lines(count: int) -> str:
    """Generate ANSI sequence to erase N lines"""
    if count <= 0:
        return ""
    # Move up and erase each line
    result = ""
    for _ in range(count):
        result += ERASE_LINE + CURSOR_UP.format(n=1)
    result += "\r"  # Return to start of line
    return result

class LogUpdate:
    """Manages terminal output with support for re-rendering"""

    def __init__(
        self,
        stream: TextIO,
        show_cursor: bool = True,
        incremental: bool = False
    ):
        self.stream = stream
        self.show_cursor = show_cursor
        self.incremental = incremental
        self._previous_line_count = 0
        self._previous_output = ""
        self._previous_lines: List[str] = []
        self._has_hidden_cursor = False

    def __call__(self, text: str) -> None:
        """Write output, erasing previous content"""
        if self.incremental:
            self._render_incremental(text)
        else:
            self._render_standard(text)

    def _render_standard(self, text: str) -> None:
        if not self.show_cursor and not self._has_hidden_cursor:
            self.stream.write(HIDE_CURSOR)
            self._has_hidden_cursor = True

        output = text + "\n"
        if output == self._previous_output:
            return

        self._previous_output = output
        self.stream.write(erase_lines(self._previous_line_count) + output)
        self._previous_line_count = output.count("\n")
        self.stream.flush()

    def _render_incremental(self, text: str) -> None:
        if not self.show_cursor and not self._has_hidden_cursor:
            self.stream.write(HIDE_CURSOR)
            self._has_hidden_cursor = True

        output = text + "\n"
        if output == self._previous_output:
            return

        previous_count = len(self._previous_lines)
        next_lines = output.split("\n")
        next_count = len(next_lines)
        visible_count = next_count - 1

        if output == "\n" or len(self._previous_output) == 0:
            self.stream.write(erase_lines(previous_count) + output)
            self._previous_output = output
            self._previous_lines = next_lines
            self.stream.flush()
            return

        buffer = []

        # Handle line count changes
        if next_count < previous_count:
            buffer.append(erase_lines(previous_count - next_count + 1))
            buffer.append(CURSOR_UP.format(n=visible_count))
        else:
            buffer.append(CURSOR_UP.format(n=previous_count - 1))

        # Only write changed lines
        for i in range(visible_count):
            if i < len(self._previous_lines) and next_lines[i] == self._previous_lines[i]:
                buffer.append(CURSOR_NEXT_LINE)
                continue
            buffer.append(ERASE_LINE + next_lines[i] + "\n")

        self.stream.write("".join(buffer))
        self._previous_output = output
        self._previous_lines = next_lines
        self.stream.flush()

    def clear(self) -> None:
        """Erase all output"""
        self.stream.write(erase_lines(self._previous_line_count))
        self._previous_output = ""
        self._previous_line_count = 0
        self._previous_lines = []
        self.stream.flush()

    def done(self) -> None:
        """Cleanup - reset state and show cursor"""
        self._previous_output = ""
        self._previous_line_count = 0
        self._previous_lines = []

        if not self.show_cursor and self._has_hidden_cursor:
            self.stream.write(SHOW_CURSOR)
            self._has_hidden_cursor = False
            self.stream.flush()

    def sync(self, text: str) -> None:
        """Update internal state without writing to stream"""
        output = text + "\n"
        self._previous_output = output
        self._previous_line_count = output.count("\n")
        self._previous_lines = output.split("\n")

def create_log_update(
    stream: TextIO,
    show_cursor: bool = True,
    incremental: bool = False
) -> LogUpdate:
    """Factory function to create LogUpdate instance"""
    return LogUpdate(stream, show_cursor, incremental)
```

**Step 3:** Verify tests pass

**Verification:** `cd python_port && pytest tests/test_log_update.py -v`

---

### Task 6.2: Get Max Width Helper
**Files:** `python_port/inkpy/get_max_width.py`, `python_port/tests/test_get_max_width.py`

**Purpose:** Calculate maximum content width accounting for padding and borders.

**Step 1:** Write failing tests
```python
# test_get_max_width.py
from inkpy.get_max_width import get_max_width
from inkpy.layout.yoga_node import YogaNode

def test_get_max_width_simple():
    """Test max width without padding/border"""
    node = YogaNode()
    node.set_style({'width': 100})
    node.calculate_layout(width=100)
    assert get_max_width(node) == 100

def test_get_max_width_with_padding():
    """Test max width with padding"""
    node = YogaNode()
    node.set_style({'width': 100, 'paddingLeft': 10, 'paddingRight': 10})
    node.calculate_layout(width=100)
    assert get_max_width(node) == 80  # 100 - 10 - 10

def test_get_max_width_with_border():
    """Test max width with border"""
    node = YogaNode()
    node.set_style({'width': 100, 'borderLeftWidth': 1, 'borderRightWidth': 1})
    node.calculate_layout(width=100)
    assert get_max_width(node) == 98  # 100 - 1 - 1
```

**Step 2:** Implement get_max_width.py
```python
"""
Get Max Width - Calculate maximum content width for a Yoga node.

Ported from: src/get-max-width.ts
"""
from inkpy.layout.yoga_node import YogaNode

def get_max_width(yoga_node: YogaNode) -> float:
    """
    Calculate the maximum content width for a Yoga node,
    accounting for padding and borders.

    Args:
        yoga_node: The Yoga node to calculate width for

    Returns:
        Maximum content width in pixels/characters
    """
    layout = yoga_node.get_layout()
    width = layout.get('width', 0)

    # Get computed padding
    padding_left = yoga_node.view.poga_layout().computed_padding_left()
    padding_right = yoga_node.view.poga_layout().computed_padding_right()

    # Get computed border
    border_left = yoga_node.view.poga_layout().computed_border_left()
    border_right = yoga_node.view.poga_layout().computed_border_right()

    return width - padding_left - padding_right - border_left - border_right
```

**Step 3:** Verify tests pass

**Verification:** `cd python_port && pytest tests/test_get_max_width.py -v`

---

### Task 6.3: Complete Ink Class
**Files:** `python_port/inkpy/ink.py`, `python_port/tests/test_ink.py`

**Purpose:** Complete the main Ink orchestrator with all missing features.

**Step 1:** Write additional failing tests
```python
# Additional tests for test_ink.py

def test_ink_terminal_resize():
    """Test that Ink handles terminal resize"""
    stdout = MockStdout(columns=80)
    ink = Ink(stdout=stdout, stdin=MockStdin(), stderr=MockStderr())
    ink.render(MockComponent())

    # Simulate resize
    stdout.columns = 120
    ink.resized()

    # Layout should recalculate
    assert ink.last_terminal_width == 120

def test_ink_throttled_rendering():
    """Test render throttling respects max_fps"""
    import time
    stdout = MockStdout()
    ink = Ink(stdout=stdout, stdin=MockStdin(), stderr=MockStderr(), max_fps=10)

    render_count = [0]
    original_on_render = ink.on_render
    def counting_render():
        render_count[0] += 1
        original_on_render()
    ink.on_render = counting_render

    # Trigger multiple rapid renders
    for _ in range(5):
        ink.root_node.on_render()

    # Due to throttling, not all should execute immediately
    # (This depends on throttle implementation)

def test_ink_ci_detection():
    """Test CI environment detection"""
    import os
    original_ci = os.environ.get('CI')
    os.environ['CI'] = 'true'
    try:
        stdout = MockStdout()
        ink = Ink(stdout=stdout, stdin=MockStdin(), stderr=MockStderr())
        assert ink.is_in_ci == True
    finally:
        if original_ci:
            os.environ['CI'] = original_ci
        else:
            os.environ.pop('CI', None)

def test_ink_screen_reader_mode():
    """Test screen reader rendering mode"""
    stdout = MockStdout()
    ink = Ink(
        stdout=stdout,
        stdin=MockStdin(),
        stderr=MockStderr(),
        is_screen_reader_enabled=True
    )
    # Screen reader mode should use different renderer
    assert ink.is_screen_reader_enabled == True
```

**Step 2:** Enhance ink.py implementation

Key additions:
- Terminal resize signal handling (SIGWINCH on Unix)
- Render throttling with configurable max_fps
- CI environment detection
- Screen reader mode support
- Console patching
- Signal exit handling (SIGTERM, SIGINT)

**Step 3:** Verify all ink tests pass

**Verification:** `cd python_port && pytest tests/test_ink.py -v`

---

### Task 6.4: Measure Element Function
**Files:** `python_port/inkpy/measure_element.py`, `python_port/tests/test_measure_element.py`

**Purpose:** Public API to measure DOM element dimensions after layout.

**Step 1:** Write failing tests
```python
# test_measure_element.py
from inkpy.measure_element import measure_element
from inkpy.dom import create_node

def test_measure_element_basic():
    """Test measuring element dimensions"""
    node = create_node('ink-box')
    node.yoga_node.set_style({'width': 50, 'height': 10})
    node.yoga_node.calculate_layout(width=50)

    result = measure_element(node)

    assert result['width'] == 50
    assert result['height'] == 10

def test_measure_element_no_yoga():
    """Test measuring element without yoga node"""
    node = create_node('ink-virtual-text')  # No yoga node
    result = measure_element(node)

    assert result['width'] == 0
    assert result['height'] == 0
```

**Step 2:** Implement measure_element.py
```python
"""
Measure Element - Get computed dimensions of a DOM element.

Ported from: src/measure-element.ts
"""
from typing import TypedDict
from inkpy.dom import DOMElement

class ElementDimensions(TypedDict):
    width: float
    height: float

def measure_element(node: DOMElement) -> ElementDimensions:
    """
    Measure the dimensions of a DOM element after layout calculation.

    Args:
        node: The DOM element to measure

    Returns:
        Dict with 'width' and 'height' keys
    """
    if node.yoga_node is None:
        return {'width': 0, 'height': 0}

    layout = node.yoga_node.get_layout()
    return {
        'width': layout.get('width', 0),
        'height': layout.get('height', 0),
    }
```

**Step 3:** Add to public API in `__init__.py`

**Verification:** `cd python_port && pytest tests/test_measure_element.py -v`

---

### Task 6.5: Renderer Screen Reader Mode
**Files:** `python_port/inkpy/renderer/renderer.py`, `python_port/tests/test_renderer.py`

**Purpose:** Add screen reader output mode that generates accessible text output.

**Step 1:** Write failing tests
```python
# Additional tests for test_renderer.py

def test_render_screen_reader_text():
    """Test screen reader output for text nodes"""
    from inkpy.renderer.renderer import render, render_for_screen_reader
    from inkpy.dom import create_node, create_text_node, append_child_node

    root = create_node('ink-root')
    text = create_node('ink-text')
    text_content = create_text_node("Hello World")
    append_child_node(text, text_content)
    append_child_node(root, text)

    root.yoga_node.calculate_layout(width=80)

    output = render_for_screen_reader(root)
    assert output == "Hello World"

def test_render_screen_reader_box_column():
    """Test screen reader output joins column items with newlines"""
    root = create_node('ink-root')
    root.style['flexDirection'] = 'column'

    text1 = create_node('ink-text')
    append_child_node(text1, create_text_node("Line 1"))
    text2 = create_node('ink-text')
    append_child_node(text2, create_text_node("Line 2"))

    append_child_node(root, text1)
    append_child_node(root, text2)

    root.yoga_node.calculate_layout(width=80)

    output = render_for_screen_reader(root)
    assert output == "Line 1\nLine 2"

def test_render_screen_reader_box_row():
    """Test screen reader output joins row items with spaces"""
    root = create_node('ink-root')
    root.style['flexDirection'] = 'row'

    text1 = create_node('ink-text')
    append_child_node(text1, create_text_node("Word1"))
    text2 = create_node('ink-text')
    append_child_node(text2, create_text_node("Word2"))

    append_child_node(root, text1)
    append_child_node(root, text2)

    root.yoga_node.calculate_layout(width=80)

    output = render_for_screen_reader(root)
    assert output == "Word1 Word2"

def test_render_screen_reader_accessibility_role():
    """Test screen reader output includes accessibility roles"""
    root = create_node('ink-root')
    root.internal_accessibility = {'role': 'button', 'state': {'selected': True}}

    text = create_node('ink-text')
    append_child_node(text, create_text_node("Submit"))
    append_child_node(root, text)

    root.yoga_node.calculate_layout(width=80)

    output = render_for_screen_reader(root)
    assert "button:" in output.lower() or "selected" in output.lower()
```

**Step 2:** Implement render_for_screen_reader in renderer.py

**Step 3:** Verify tests pass

**Verification:** `cd python_port && pytest tests/test_renderer.py -v`

---

## Phase 7: Accessibility & Examples

### Task 7.1: Accessibility Context
**Files:** `python_port/inkpy/components/accessibility_context.py`, `python_port/inkpy/hooks/use_is_screen_reader_enabled.py`

**Step 1:** Write failing tests
```python
# test_accessibility.py
from inkpy.components.accessibility_context import AccessibilityContext
from inkpy.hooks.use_is_screen_reader_enabled import use_is_screen_reader_enabled

def test_accessibility_context_default():
    """Test default accessibility context value"""
    # Default should be screen reader disabled

def test_use_is_screen_reader_enabled():
    """Test hook returns correct value from context"""
    # When context has is_screen_reader_enabled=True, hook should return True
```

**Step 2:** Implement

```python
# accessibility_context.py
"""
Accessibility Context - Provides screen reader state to components.

Ported from: src/components/AccessibilityContext.ts
"""
from reactpy import create_context

AccessibilityContext = create_context({
    'is_screen_reader_enabled': False
})
```

```python
# use_is_screen_reader_enabled.py
"""
useIsScreenReaderEnabled hook - Returns whether screen reader is enabled.

Ported from: src/hooks/use-is-screen-reader-enabled.ts
"""
from reactpy.core.hooks import use_context
from inkpy.components.accessibility_context import AccessibilityContext

def use_is_screen_reader_enabled() -> bool:
    """
    Returns whether a screen reader is enabled.

    Useful when you want to render different output for screen readers.

    Returns:
        True if screen reader is enabled, False otherwise
    """
    context = use_context(AccessibilityContext)
    return context.get('is_screen_reader_enabled', False)
```

**Step 3:** Add to public API

**Verification:** `cd python_port && pytest tests/test_accessibility.py -v`

---

### Task 7.2: Counter Example (E2E)
**Files:** `python_port/examples/counter.py`, `python_port/tests/test_examples_e2e.py`

**Purpose:** Create a working end-to-end counter example demonstrating the full render loop.

**Step 1:** Write E2E test
```python
# test_examples_e2e.py
import asyncio
import io

def test_counter_example_renders():
    """Test counter example produces output"""
    from examples.counter import Counter
    from inkpy import render

    stdout = io.StringIO()
    instance = render(Counter(), stdout=stdout)

    # Give it time to render
    asyncio.get_event_loop().run_until_complete(asyncio.sleep(0.1))

    output = stdout.getvalue()
    assert "Count:" in output or "0" in output

    instance.unmount()
```

**Step 2:** Implement counter.py
```python
"""
Counter Example - Demonstrates state and timed updates.
"""
import asyncio
from reactpy import component, use_state, use_effect
from inkpy import render, Box, Text

@component
def Counter():
    count, set_count = use_state(0)

    @use_effect(dependencies=[])
    async def timer():
        while True:
            await asyncio.sleep(1)
            set_count(lambda c: c + 1)

    return Box(
        Text(f"Count: {count}", color="green"),
        border_style="round",
        padding=1
    )

if __name__ == "__main__":
    instance = render(Counter())
    asyncio.get_event_loop().run_forever()
```

**Verification:** `cd python_port && python examples/counter.py` (manual, Ctrl+C to exit)

---

### Task 7.3: Interactive Example (E2E)
**Files:** `python_port/examples/interactive.py`

**Purpose:** Create an interactive example with keyboard navigation.

**Step 1:** Implement interactive.py
```python
"""
Interactive Example - Demonstrates keyboard input handling.
"""
import asyncio
from reactpy import component, use_state
from inkpy import render, Box, Text
from inkpy.hooks import use_input, use_app

@component
def SelectList():
    items = ["Option 1", "Option 2", "Option 3", "Exit"]
    selected, set_selected = use_state(0)
    app = use_app()

    def handle_input(input_str, key):
        if key.get('upArrow'):
            set_selected(lambda s: max(0, s - 1))
        elif key.get('downArrow'):
            set_selected(lambda s: min(len(items) - 1, s + 1))
        elif key.get('return'):
            if selected == len(items) - 1:
                app['exit']()

    use_input(handle_input)

    return Box(
        [
            Text(
                f"{'>' if i == selected else ' '} {item}",
                color="cyan" if i == selected else "white"
            )
            for i, item in enumerate(items)
        ],
        flex_direction="column",
        border_style="single",
        padding=1
    )

if __name__ == "__main__":
    instance = render(SelectList())
    asyncio.get_event_loop().run_until_complete(instance.wait_until_exit())
```

**Verification:** `cd python_port && python examples/interactive.py` (manual, navigate with arrows)

---

## Phase 8: Documentation & Polish

### Task 8.1: Complete Type Hints
**Files:** All `python_port/inkpy/**/*.py`

**Step 1:** Run mypy to identify missing types
```bash
cd python_port && mypy inkpy/ --ignore-missing-imports
```

**Step 2:** Add missing type annotations

**Step 3:** Ensure `py.typed` marker exists

**Verification:** `cd python_port && mypy inkpy/ --ignore-missing-imports` (no errors)

---

### Task 8.2: Update Public API Exports
**Files:** `python_port/inkpy/__init__.py`

Add missing exports:
```python
# Add to __init__.py
from inkpy.measure_element import measure_element
from inkpy.hooks.use_is_screen_reader_enabled import use_is_screen_reader_enabled

__all__ = [
    # ... existing exports ...
    'measure_element',
    'use_is_screen_reader_enabled',
]
```

---

### Task 8.3: README Update
**Files:** `python_port/README.md`

Update with:
- Installation instructions
- Quick start guide
- API reference links
- Examples
- Feature comparison with TypeScript Ink

---

## Verification Checklist

After completing all tasks, run the full test suite:

```bash
cd python_port
source venv/bin/activate
pytest tests/ -v --tb=short
```

Expected: All tests pass (0 failures, ~160+ tests)

### Feature Parity Checklist

| Feature | TypeScript | Python | Status |
|---------|-----------|--------|--------|
| Output buffer | ✅ | ⬜ | Task 6.1 |
| Terminal resize | ✅ | ⬜ | Task 6.3 |
| Render throttling | ✅ | ⬜ | Task 6.3 |
| Screen reader | ✅ | ⬜ | Task 6.5, 7.1 |
| measureElement | ✅ | ⬜ | Task 6.4 |
| E2E examples | ✅ | ⬜ | Task 7.2, 7.3 |

---

## Estimated Timeline

| Phase | Tasks | Time Estimate |
|-------|-------|---------------|
| Phase 6 | 5 tasks | 4-5 hours |
| Phase 7 | 3 tasks | 2-3 hours |
| Phase 8 | 3 tasks | 2 hours |
| **Total** | **11 tasks** | **8-10 hours** |

---

## Next Steps

Ready to execute? Start with **Task 6.1: Log Update Module**.

Trigger: `execution-workflow.mdc`

