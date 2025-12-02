# InkPy Interactive Input & 100% Parity Implementation Plan

> **Goal:** Fix interactive capabilities, key recognition, and achieve full feature parity with Ink
>
> **Tech Stack:** Python 3.9+, ReactPy, Poga (Yoga layout), pytest
>
> **Source Reference:** `ink/src/`
>
> **Target:** `inkpy/inkpy/`
>
> **Skills Reference:** See `@.cursor/skills/test-driven-development.md` for TDD protocol
>
> **Created:** 2025-12-02

---

## Executive Summary

After comprehensive analysis comparing Ink (TypeScript) with InkPy (Python), I identified several **critical bugs** causing interactive capabilities to fail, plus remaining gaps for 100% parity.

### Root Cause Analysis: "Keys Not Recognized Properly"

The interactive example fails because of **naming mismatches**:

| Used in Example | Actual Property | Status |
|-----------------|-----------------|--------|
| `key.up_arrow` | `key.upArrow` | ❌ Wrong |
| `key.down_arrow` | `key.downArrow` | ❌ Wrong |
| `key.return_key` | `key.return_` | ❌ Wrong |

Additionally, style props use snake_case (`flex_direction`) but the style system expects camelCase (`flexDirection`).

---

## Critical Bugs (Priority 1: MUST FIX)

### Bug 1: Key Property Names - Snake Case Not Supported

**Location:** `inkpy/input/keypress.py` + `inkpy/examples/interactive.py`

**Problem:** The `Key` dataclass has camelCase properties (`upArrow`, `downArrow`, `return_`) matching Ink's TypeScript, but Python conventions use snake_case. The example uses `key.up_arrow` which doesn't exist.

**Impact:** ALL interactive input fails - arrows, enter, etc.

**Solution:** Add snake_case property aliases to the `Key` dataclass.

---

### Bug 2: Interactive Example Uses Wrong Property Names

**Location:** `inkpy/examples/interactive.py`

**Problem:** Uses `key.up_arrow`, `key.down_arrow`, `key.return_key` which don't exist.

**Solution:** Either update example OR (preferred) add snake_case aliases to Key class.

---

### Bug 3: Box/Text Style Props - Snake Case Not Mapped

**Location:** `inkpy/components/box.py`, `inkpy/components/text.py`

**Problem:** Style props like `flex_direction="column"` passed to Box aren't converted to `flexDirection` which the Yoga layout system expects.

**Impact:** Layout styling may not work when using Python-style prop names.

**Solution:** Map snake_case kwargs to camelCase style properties.

---

## Implementation Tasks

### Task 1: Add Snake_case Aliases to Key Class (CRITICAL)

**Priority:** P0 - Blocks all interactive input
**Effort:** 30 minutes

**Files:**
- Modify: `inkpy/inkpy/input/keypress.py`
- Test: `inkpy/tests/test_keypress.py`

**Step 1: Write the failing test**

```python
# tests/test_keypress.py - Add new tests
def test_key_snake_case_properties():
    """Test Key class has both camelCase and snake_case properties"""
    key = parse_keypress('\x1b[A')  # Up arrow
    
    # CamelCase (existing)
    assert key.upArrow is True
    
    # Snake_case (NEW)
    assert key.up_arrow is True
    assert key.down_arrow is False


def test_key_return_alias():
    """Test return key has both return_ and return_key aliases"""
    key = parse_keypress('\r')
    assert key.return_ is True
    assert key.return_key is True  # Alias for convenience


def test_key_all_snake_case_aliases():
    """Test all snake_case aliases exist"""
    key = parse_keypress('a')
    
    # All arrow properties should exist in snake_case
    assert hasattr(key, 'up_arrow')
    assert hasattr(key, 'down_arrow')
    assert hasattr(key, 'left_arrow')
    assert hasattr(key, 'right_arrow')
    assert hasattr(key, 'page_up')
    assert hasattr(key, 'page_down')
    assert hasattr(key, 'return_key')
```

**Step 2: Run test to verify it fails**
```bash
uv run pytest tests/test_keypress.py::test_key_snake_case_properties -v
```
Expected: FAIL with AttributeError: 'Key' has no attribute 'up_arrow'

**Step 3: Implement snake_case aliases**

```python
# inkpy/input/keypress.py - Add to Key dataclass

@dataclass
class Key:
    """Parsed key information."""
    name: str = ''
    ctrl: bool = False
    meta: bool = False
    shift: bool = False
    option: bool = False
    sequence: str = ''
    raw: Optional[str] = None
    code: Optional[str] = None
    
    # === CamelCase properties (Ink parity) ===
    @property
    def upArrow(self) -> bool:
        return self.name == 'up'
    
    @property
    def downArrow(self) -> bool:
        return self.name == 'down'
    
    # ... existing properties ...
    
    # === Snake_case aliases (Pythonic API) ===
    @property
    def up_arrow(self) -> bool:
        """Snake_case alias for upArrow"""
        return self.upArrow
    
    @property
    def down_arrow(self) -> bool:
        """Snake_case alias for downArrow"""
        return self.downArrow
    
    @property
    def left_arrow(self) -> bool:
        """Snake_case alias for leftArrow"""
        return self.leftArrow
    
    @property
    def right_arrow(self) -> bool:
        """Snake_case alias for rightArrow"""
        return self.rightArrow
    
    @property
    def page_up(self) -> bool:
        """Snake_case alias for pageUp"""
        return self.pageUp
    
    @property
    def page_down(self) -> bool:
        """Snake_case alias for pageDown"""
        return self.pageDown
    
    @property
    def return_key(self) -> bool:
        """Alias for return_ (more readable)"""
        return self.return_
```

**Step 4: Run test to verify it passes**
```bash
uv run pytest tests/test_keypress.py -v
```
Expected: PASS

**Step 5: Commit**
```bash
git add inkpy/input/keypress.py tests/test_keypress.py
git commit -m "feat(input): add snake_case property aliases to Key class"
```

---

### Task 2: Add Style Prop Name Mapping to Box Component

**Priority:** P0 - Affects layout
**Effort:** 45 minutes

**Files:**
- Modify: `inkpy/inkpy/components/box.py`
- Test: `inkpy/tests/test_components.py`

**Step 1: Write the failing test**

```python
# tests/test_box_style_props.py
def test_box_accepts_snake_case_style_props():
    """Test Box converts snake_case props to camelCase"""
    from inkpy.components.box import Box
    
    # Create Box with snake_case props
    @component
    def TestBox():
        return Box(
            flex_direction="column",
            align_items="center",
            justify_content="space-between",
            border_style="single",
            background_color="blue",
        )
    
    # Render and verify style is correctly converted
    # ... test rendering ...


def test_box_flex_direction_maps_correctly():
    """Test flex_direction maps to flexDirection in style"""
    # Create box with flex_direction="column"
    # Verify style dict has flexDirection="column"
    pass
```

**Step 2: Implement style prop mapping**

```python
# inkpy/components/box.py

# Style prop name mapping (snake_case -> camelCase)
STYLE_PROP_MAP = {
    'flex_direction': 'flexDirection',
    'align_items': 'alignItems',
    'align_content': 'alignContent',
    'align_self': 'alignSelf',
    'justify_content': 'justifyContent',
    'flex_wrap': 'flexWrap',
    'flex_grow': 'flexGrow',
    'flex_shrink': 'flexShrink',
    'flex_basis': 'flexBasis',
    'padding_top': 'paddingTop',
    'padding_bottom': 'paddingBottom',
    'padding_left': 'paddingLeft',
    'padding_right': 'paddingRight',
    'margin_top': 'marginTop',
    'margin_bottom': 'marginBottom',
    'margin_left': 'marginLeft',
    'margin_right': 'marginRight',
    'border_style': 'borderStyle',
    'border_color': 'borderColor',
    'background_color': 'backgroundColor',
    'min_width': 'minWidth',
    'min_height': 'minHeight',
    'max_width': 'maxWidth',
    'max_height': 'maxHeight',
    'overflow_x': 'overflowX',
    'overflow_y': 'overflowY',
    'text_wrap': 'textWrap',
}

def _normalize_style_props(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Convert snake_case style props to camelCase"""
    normalized = {}
    for key, value in kwargs.items():
        camel_key = STYLE_PROP_MAP.get(key, key)
        normalized[camel_key] = value
    return normalized


@component
def Box(
    children=None,
    style: Optional[Dict[str, Any]] = None,
    # Accept common props directly
    backgroundColor: Optional[Union[str, int]] = None,
    borderStyle: Optional[str] = None,
    # Snake_case aliases
    background_color: Optional[Union[str, int]] = None,
    border_style: Optional[str] = None,
    # ARIA props
    aria_label: Optional[str] = None,
    aria_hidden: bool = False,
    aria_role: Optional[str] = None,
    aria_state: Optional[Dict[str, bool]] = None,
    **kwargs
):
    # Normalize style prop names
    normalized_kwargs = _normalize_style_props(kwargs)
    
    # Handle snake_case aliases for explicit props
    final_bg = backgroundColor or background_color
    final_border = borderStyle or border_style
    
    # ... rest of implementation
```

**Step 3: Run tests**
```bash
uv run pytest tests/test_box_style_props.py -v
```

**Step 4: Commit**
```bash
git add inkpy/components/box.py tests/test_box_style_props.py
git commit -m "feat(box): add snake_case style prop mapping"
```

---

### Task 3: Apply Same Mapping to Text Component

**Priority:** P1
**Effort:** 30 minutes

**Files:**
- Modify: `inkpy/inkpy/components/text.py`
- Test: `inkpy/tests/test_text_style_props.py`

Similar implementation to Box component.

---

### Task 4: Fix Interactive Example

**Priority:** P1 - Documentation/Example
**Effort:** 15 minutes

**Files:**
- Modify: `inkpy/examples/interactive.py`

After Task 1, the example should work. But also update to use best practices:

```python
# inkpy/examples/interactive.py
def handle_input(input_str, key):
    # Now works with snake_case aliases!
    if key.up_arrow:
        set_selected(lambda s: max(0, s - 1))
    elif key.down_arrow:
        set_selected(lambda s: min(len(items) - 1, s + 1))
    elif key.return_key:  # Changed from return_
        if selected == len(items) - 1:
            app.exit()
```

---

## Secondary Gaps (Priority 2: Should Fix)

### Gap 1: Input Event Loop Thread Safety

**Location:** `inkpy/components/app.py`

**Problem:** The input loop runs in a background thread but updates React state. There may be race conditions or state update issues.

**Solution:** Ensure state updates are properly synchronized.

---

### Gap 2: Context Value Access Consistency

**Location:** Various hooks

**Problem:** Some code accesses context values as dict (`ctx['key']`), some as object (`ctx.key`). Should be consistent.

**Solution:** Standardize on dict access (matches ReactPy pattern).

---

### Gap 3: Missing `batchedUpdates` Equivalent

**Location:** `inkpy/hooks/use_input.py`

**Problem:** Ink uses `reconciler.batchedUpdates()` to batch input handler calls. ReactPy doesn't have this.

**Impact:** Minor - may cause extra renders.

**Solution:** Accept as ReactPy limitation, document it.

---

## Remaining Parity Gaps (From Previous Analysis)

These were identified in the previous plan and still need attention:

| ID | Gap | Priority | Effort |
|----|-----|----------|--------|
| G1 | Transform `accessibilityLabel` prop | Medium | 30 min |
| G2 | Text screen reader context | Medium | 1 hour |
| G3 | ErrorOverview code excerpts | Low | 2-3 hours |
| G4 | Box screen reader label | Medium | 30 min |
| G5 | Screen reader `wrapAnsi` | Medium | 1 hour |

---

## Test Verification Checklist

After implementing fixes, verify:

### Interactive Input
- [ ] Arrow keys navigate selection (up/down)
- [ ] Enter key triggers action
- [ ] Q key exits (if implemented)
- [ ] Tab cycles focus
- [ ] Shift+Tab reverse cycles focus
- [ ] Escape clears focus
- [ ] Ctrl+C exits (when exitOnCtrlC=true)

### Style Props
- [ ] `flex_direction="column"` works
- [ ] `border_style="single"` works
- [ ] `background_color="blue"` works
- [ ] CamelCase props still work

### Component Rendering
- [ ] Box renders correctly
- [ ] Text renders with styles
- [ ] Nested components work

---

## Implementation Order

```
Phase 1 (Critical - ~2 hours total):
├── Task 1: Key snake_case aliases (30min) ← BLOCKS ALL INPUT
├── Task 2: Box style prop mapping (45min)
├── Task 3: Text style prop mapping (30min)
└── Task 4: Fix interactive example (15min)

Phase 2 (Secondary - ~2 hours total):
├── Input thread safety review (1h)
└── Context access consistency (1h)

Phase 3 (Parity - ~4 hours total):
├── G1: Transform accessibilityLabel (30min)
├── G2: Text screen reader context (1h)
├── G3: ErrorOverview code excerpts (2-3h)
└── G4: Box screen reader label (30min)

TOTAL: ~8 hours to full parity
```

---

## Quick Fix Summary

For the immediate "keys not recognized" issue, the minimal fix is:

**Option A: Fix the example (5 min)**
Change `key.up_arrow` → `key.upArrow`, etc.

**Option B: Add aliases (30 min)** - RECOMMENDED
Add snake_case property aliases to Key class for Pythonic API.

Both options work. Option B is better for long-term usability.

---

## Ready to Execute?

To execute this plan:

1. Start with Task 1 (Key aliases) - fixes the core issue
2. Run interactive example to verify
3. Continue with Tasks 2-4 for complete fix

Use: `@.cursor/rules/execution-workflow.mdc` to begin implementation.

