# InkPy 100% Parity - Final Gap Closure Plan

> **Goal:** Close the remaining ~5% parity gap to achieve 100% feature parity with Ink
>
> **Tech Stack:** Python 3.9+, Custom Reconciler, Poga (Yoga layout), pytest
>
> **Skills Reference:** See `@.cursor/skills/test-driven-development.md` for TDD protocol
>
> **Date:** 2025-12-02

---

## Executive Summary

Based on the fact-check of the parity analysis, InkPy is at ~95% parity. This plan closes the remaining gaps:

| Gap | File | Priority | Effort |
|-----|------|----------|--------|
| 1. Throttle wrapper for log | `ink.py` | Medium | 30 min |
| 2. Display: none check in screen reader | `screen_reader.py` | Low | 15 min |
| 3. ANSI-aware text width (widest-line) | `measure_text.py` | Medium | 30 min |
| 4. Clean up misleading TODO comment | `text_node.py` | Low | 5 min |
| 5. Update parity analysis document | `2025-12-02-inkpy-complete-parity-analysis.md` | Low | 10 min |

**Total Estimated Time:** ~1.5 hours

---

## Task 1: Implement Throttle Wrapper for Log Updates

**Priority:** Medium | **Effort:** 30 min

The throttle wrapper prevents excessive terminal writes during rapid state updates.

**Files:**
- Modify: `inkpy/inkpy/ink.py`
- Create: `inkpy/tests/test_throttle.py`

### Step 1: Write the failing test

```python
# tests/test_throttle.py
import time
from inkpy.ink import throttle

def test_throttle_limits_calls():
    """Throttle should limit function calls to max once per interval."""
    call_count = 0

    def increment():
        nonlocal call_count
        call_count += 1

    # Throttle to 100ms (10 FPS)
    throttled = throttle(increment, 100, leading=True, trailing=True)

    # Call rapidly 10 times
    for _ in range(10):
        throttled()
        time.sleep(0.01)  # 10ms between calls

    # Should have at most 2 calls (leading + trailing), not 10
    assert call_count <= 3

def test_throttle_leading_call():
    """Throttle with leading=True should call immediately on first call."""
    call_times = []

    def record_time():
        call_times.append(time.time())

    throttled = throttle(record_time, 100, leading=True, trailing=False)

    start = time.time()
    throttled()

    # First call should happen immediately
    assert len(call_times) == 1
    assert call_times[0] - start < 0.01  # Within 10ms

def test_throttle_trailing_call():
    """Throttle with trailing=True should call after interval ends."""
    call_count = 0

    def increment():
        nonlocal call_count
        call_count += 1

    throttled = throttle(increment, 50, leading=True, trailing=True)

    # Rapid calls
    throttled()  # Leading call (1)
    throttled()
    throttled()

    # Wait for trailing call
    time.sleep(0.1)

    # Should have exactly 2 calls: leading + trailing
    assert call_count == 2
```

### Step 2: Run test to verify it fails

```bash
uv run pytest inkpy/tests/test_throttle.py -v
```

Expected: FAIL with "cannot import name 'throttle' from 'inkpy.ink'"

### Step 3: Implement the throttle function

```python
# inkpy/ink.py - Add after imports

import threading
from typing import Callable, Optional

def throttle(
    func: Callable,
    wait_ms: int,
    leading: bool = True,
    trailing: bool = True
) -> Callable:
    """
    Throttle function calls to at most once per wait_ms milliseconds.

    Equivalent to es-toolkit/compat throttle.

    Args:
        func: Function to throttle
        wait_ms: Minimum time between calls in milliseconds
        leading: Call on leading edge (first call)
        trailing: Call on trailing edge (after wait)

    Returns:
        Throttled function
    """
    last_call_time = 0
    pending_call = False
    timer: Optional[threading.Timer] = None
    lock = threading.Lock()

    def throttled(*args, **kwargs):
        nonlocal last_call_time, pending_call, timer

        now = time.time() * 1000  # Convert to ms

        with lock:
            time_since_last = now - last_call_time

            if time_since_last >= wait_ms:
                # Enough time has passed - call immediately if leading
                if leading:
                    last_call_time = now
                    func(*args, **kwargs)
                else:
                    pending_call = True
            else:
                # Within throttle window - schedule trailing call
                pending_call = True

            # Schedule trailing call if not already scheduled
            if trailing and pending_call and timer is None:
                remaining = wait_ms - time_since_last
                if remaining < 0:
                    remaining = wait_ms

                def trailing_call():
                    nonlocal pending_call, timer, last_call_time
                    with lock:
                        if pending_call:
                            last_call_time = time.time() * 1000
                            pending_call = False
                            func(*args, **kwargs)
                        timer = None

                timer = threading.Timer(remaining / 1000, trailing_call)
                timer.daemon = True
                timer.start()

    return throttled
```

### Step 4: Update ink.py to use throttle

```python
# Replace lines 92-95 in ink.py with:
        self.throttled_log: LogUpdate = (
            self.log if self._unthrottled
            else throttle(
                lambda content: self.log(content),
                self._render_throttle_ms,
                leading=True,
                trailing=True
            )
        )
```

### Step 5: Run test to verify it passes

```bash
uv run pytest inkpy/tests/test_throttle.py -v
```

Expected: PASS

### Step 6: Run full test suite

```bash
uv run pytest --tb=short
```

Expected: All tests pass

### Step 7: Commit

```bash
git add inkpy/inkpy/ink.py inkpy/tests/test_throttle.py
git commit -m "feat(ink): implement throttle wrapper for log updates"
```

---

## Task 2: Add Display None Check in Screen Reader

**Priority:** Low | **Effort:** 15 min

Check if a node has `display: none` before rendering in screen reader mode.

**Files:**
- Modify: `inkpy/inkpy/renderer/screen_reader.py`
- Modify: `inkpy/tests/test_screen_reader.py` (if exists)

### Step 1: Write the failing test

```python
# Add to tests/test_screen_reader.py or create new file
from inkpy.renderer.screen_reader import render_node_to_screen_reader_output
from inkpy.dom import create_node, DOMElement

def test_screen_reader_skips_display_none():
    """Screen reader should skip nodes with display: none."""
    root = create_node('ink-root')
    root.style = {'flexDirection': 'column'}

    visible_box = create_node('ink-box')
    visible_text = create_node('ink-text')
    # Note: Add text content through child nodes

    hidden_box = create_node('ink-box')
    hidden_box.style = {'display': 'none'}

    # Build tree structure
    # ... (depends on DOM API)

    output = render_node_to_screen_reader_output(root)

    # Hidden content should not appear
    assert 'hidden' not in output.lower()
```

### Step 2: Implement display none check

```python
# screen_reader.py - Update the function

def render_node_to_screen_reader_output(
    node: DOMElement,
    skip_static: bool = False,
    parent_role: Optional[str] = None,
) -> str:
    # Skip static elements if requested
    if skip_static and node.internal_static:
        return ''

    # Skip nodes with display: none
    if node.style.get('display') == 'none':
        return ''

    # ... rest of function
```

### Step 3: Run test to verify it passes

```bash
uv run pytest inkpy/tests/test_screen_reader.py -v
```

### Step 4: Commit

```bash
git add inkpy/inkpy/renderer/screen_reader.py inkpy/tests/test_screen_reader.py
git commit -m "feat(screen-reader): skip display: none nodes"
```

---

## Task 3: ANSI-Aware Text Width Measurement

**Priority:** Medium | **Effort:** 30 min

Use the existing ANSI tokenizer for accurate CJK/emoji width calculation (widest-line equivalent).

**Files:**
- Modify: `inkpy/inkpy/measure_text.py`
- Add test: `inkpy/tests/test_measure_text_ansi.py`

### Step 1: Write the failing test

```python
# tests/test_measure_text_ansi.py
from inkpy.measure_text import measure_text

def test_measure_text_with_ansi_codes():
    """Measure text should correctly measure text with ANSI codes."""
    # Text with ANSI color codes
    text = "\x1b[31mred\x1b[0m"
    result = measure_text(text)

    # Should measure visible width (3 chars), not ANSI codes
    assert result['width'] == 3
    assert result['height'] == 1

def test_measure_text_cjk_characters():
    """Measure text should count CJK characters as double width."""
    text = "hello世界"  # 5 + 2*2 = 9 display width
    result = measure_text(text)

    # CJK characters are double-width
    assert result['width'] == 9

def test_measure_text_emoji():
    """Measure text should handle emoji width correctly."""
    text = "hi👋there"  # 2 + 2 + 5 = 9 (emoji is typically 2 wide)
    result = measure_text(text)

    # Emoji is typically double-width
    assert result['width'] >= 9

def test_measure_multiline_widest():
    """Measure text should return widest line width."""
    text = "short\nlonger line\nmed"
    result = measure_text(text)

    assert result['width'] == 11  # "longer line" length
    assert result['height'] == 3
```

### Step 2: Update measure_text to use ANSI tokenizer

```python
# inkpy/measure_text.py
"""
Text measurement module - measures text dimensions (width, height)
Uses ANSI-aware width calculation for accurate terminal display.
"""
from typing import Dict
from inkpy.renderer.ansi_tokenize import string_width

# Cache for text measurements
_cache: Dict[str, Dict[str, int]] = {}

def measure_text(text: str) -> Dict[str, int]:
    """
    Measure text dimensions (width and height).

    Uses ANSI-aware width calculation that handles:
    - ANSI escape codes (ignored in width calculation)
    - CJK characters (double-width)
    - Emoji (variable width)

    Args:
        text: Text to measure

    Returns:
        Dictionary with 'width' and 'height' keys
    """
    if len(text) == 0:
        return {'width': 0, 'height': 0}

    # Check cache
    cached = _cache.get(text)
    if cached:
        return cached

    # Calculate width (widest line) using ANSI-aware width
    lines = text.split('\n')
    width = 0
    for line in lines:
        line_width = string_width(line)
        width = max(width, line_width)

    # Height is number of lines
    height = len(lines)

    dimensions = {'width': width, 'height': height}
    _cache[text] = dimensions

    return dimensions
```

### Step 3: Run test to verify it passes

```bash
uv run pytest inkpy/tests/test_measure_text_ansi.py -v
```

### Step 4: Commit

```bash
git add inkpy/inkpy/measure_text.py inkpy/tests/test_measure_text_ansi.py
git commit -m "feat(measure-text): use ANSI-aware width calculation"
```

---

## Task 4: Clean Up Misleading TODO Comment

**Priority:** Low | **Effort:** 5 min

The TODO in text_node.py is misleading - the ANSI stripping is actually implemented.

**Files:**
- Modify: `inkpy/inkpy/layout/text_node.py`

### Step 1: Update the comment

```python
# text_node.py - Line 40-44
# Change from:
        width = 0
        for line in final_lines:
            # TODO: Strip ANSI codes for real length
            line_len = self._strip_ansi(line)
            width = max(width, len(line_len))

# To:
        width = 0
        for line in final_lines:
            # Strip ANSI codes for accurate character count
            stripped = self._strip_ansi(line)
            width = max(width, len(stripped))
```

### Step 2: Commit

```bash
git add inkpy/inkpy/layout/text_node.py
git commit -m "docs(text-node): clarify ANSI stripping comment"
```

---

## Task 5: Update Parity Analysis Document

**Priority:** Low | **Effort:** 10 min

Update the parity analysis to reflect the true status.

**Files:**
- Modify: `docs/plans/2025-12-02-inkpy-complete-parity-analysis.md`

### Changes:

1. Update overall parity status from ~88% to ~95%+ (after this plan: 100%)
2. Remove G1, G2, G3 from gaps list - they're already implemented
3. Add note about throttledLog fix
4. Update conclusion to reflect production-ready status

### Step 1: Update the document

See specific edits below:

```markdown
## Gap Summary

### Closed Gaps (Previously Listed as Open)

| ID | Gap | Status | Resolution |
|----|-----|--------|------------|
| G1 | Screen reader wrapAnsi | ✅ CLOSED | wrap_text.py uses ANSI tokenizer |
| G2 | applyPaddingToText indent-string | ✅ CLOSED | render_node.py has indent_string |
| G3 | flexBasis auto verification | ✅ CLOSED | styles.py handles auto correctly |

### Remaining Gaps (Now Fixed)

| ID | Gap | Status |
|----|-----|--------|
| G4 | throttledLog wrapper | ✅ Fixed in this sprint |
| G5 | Display none in screen reader | ✅ Fixed in this sprint |
```

### Step 2: Commit

```bash
git add docs/plans/2025-12-02-inkpy-complete-parity-analysis.md
git commit -m "docs: update parity analysis to reflect 100% completion"
```

---

## Verification Checklist

After completing all tasks, run:

```bash
# Full test suite
uv run pytest --tb=short

# Specific new tests
uv run pytest inkpy/tests/test_throttle.py inkpy/tests/test_measure_text_ansi.py -v

# Interactive verification (optional)
cd inkpy && uv run python examples/interactive.py
```

---

## Summary

| Task | Status | Verification |
|------|--------|--------------|
| 1. Throttle wrapper | [ ] | `test_throttle.py` passes |
| 2. Display none check | [ ] | Screen reader tests pass |
| 3. ANSI-aware measure | [ ] | `test_measure_text_ansi.py` passes |
| 4. Clean TODO comment | [ ] | Code review |
| 5. Update docs | [ ] | Document review |

**Final Command:**

```bash
git push origin master
```

---

## Appendix: Throttle Implementation Reference

The throttle implementation matches `es-toolkit/compat` behavior:

```typescript
// Ink's usage:
throttle(this.log, undefined, { leading: true, trailing: true })
```

Python equivalent:

```python
throttle(self.log, wait_ms=33, leading=True, trailing=True)  # ~30 FPS
```
