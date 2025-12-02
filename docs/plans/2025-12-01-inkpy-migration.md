# Ink to InkPy Migration Plan

> **Goal:** Complete the migration of [Ink](https://github.com/vadimdemedes/ink) (React for CLIs in TypeScript) to InkPy (Python) with feature parity, enabling building complex CLI applications like `claude-code` with a component-based architecture and Flexbox layout.

> **Tech Stack:** Python 3.9+, ReactPy (component framework), Poga (Yoga layout bindings), pytest (testing)

> **Reference:** Original Ink source at `ink/src/`

---

## Current Status Summary

### Completed (✅)
- **Phase 1.1:** YogaNode wrapper around `poga`
- **Phase 1.2:** Layout calculation (with some xfail edge cases)
- **Phase 1.3:** TextNode with measurement logic
- **Phase 2.1:** Basic Box and Text components
- **Phase 2.2:** ReactPy state hooks verification
- **Phase 3.1:** Basic ANSI renderer

### In Progress (🟡)
- **Phase 2.3:** TUIBackend scaffolding and VDOM-to-Yoga mapping
- **Phase 3.2:** Layout-based rendering integration

### Not Started (⬜)
- Phase 4: Input Handling
- Phase 5: Advanced Components
- Phase 6: Performance & Polish
- Phase 7: Documentation & Examples

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      User Application                        │
│   @component                                                │
│   def App(): return Box([Text("Hello"), Text("World")])     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   ReactPy Core + InkPy                       │
│   Components (Box, Text, Static, etc.)                      │
│   Hooks (use_input, use_app, use_focus, etc.)               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      TUI Backend                             │
│   VDOM → Yoga Tree Conversion                               │
│   Layout Calculation                                        │
│   Render Loop Management                                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   Layout Engine (Poga/Yoga)                  │
│   YogaNode, TextNode                                        │
│   Flexbox calculation                                       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      Renderer                                │
│   Output buffer (virtual screen)                            │
│   ANSI escape sequences                                     │
│   Borders, backgrounds, colors                              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                       stdout                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 3: Complete Renderer (Priority: HIGH)

### Task 3.1: Output Buffer Class ⬜
**Files:** `inkpy/inkpy/renderer/output.py`, `inkpy/tests/test_output.py`

**Step 1:** Write failing tests for Output buffer
```python
# test_output.py
def test_output_write():
    """Test writing text at specific coordinates"""
    output = Output(width=20, height=10)
    output.write(5, 2, "Hello")
    result = output.get()
    assert "Hello" in result['output']

def test_output_clip():
    """Test clipping text to boundaries"""
    output = Output(width=10, height=5)
    output.clip(x1=2, x2=8, y1=0, y2=5)
    output.write(0, 0, "Hello World")  # Should be clipped
    output.unclip()
    result = output.get()
    # "Hello World" starts at 0, clip at 2-8, so we should see "llo Wor"
```

**Step 2:** Implement Output class (port from `ink/src/output.ts`)
- Initialize 2D buffer with spaces
- `write(x, y, text, transformers)` - position text with optional transforms
- `clip(x1, x2, y1, y2)` - enable clipping region
- `unclip()` - remove clipping
- `get()` - return final string and height

**Step 3:** Verify tests pass

**Verification:** `cd inkpy && pytest tests/test_output.py -v`

---

### Task 3.2: Enhanced Styles Mapping ⬜
**Files:** `inkpy/inkpy/layout/styles.py`, `inkpy/tests/test_styles.py`

**Step 1:** Write failing tests for style properties
```python
def test_padding_x_y():
    """Test paddingX and paddingY shortcuts"""
    node = YogaNode()
    apply_styles(node, {'paddingX': 5, 'paddingY': 2})
    # Check that padding left/right = 5, top/bottom = 2

def test_border_styles():
    """Test border style application"""
    node = YogaNode()
    apply_styles(node, {'borderStyle': 'single', 'borderTop': False})
    # Border should be 1 on left/right/bottom, 0 on top

def test_percentage_dimensions():
    """Test width/height as percentages"""
    node = YogaNode()
    apply_styles(node, {'width': '50%', 'height': '100%'})
```

**Step 2:** Implement comprehensive style mapping (port from `ink/src/styles.ts`)
- Position styles (absolute/relative)
- Margin shortcuts (margin, marginX, marginY, marginTop, etc.)
- Padding shortcuts
- Flex styles (flexGrow, flexShrink, flexWrap, flexBasis, alignItems, alignSelf, justifyContent)
- Dimension styles with percentage support
- Border styles
- Gap styles
- Display styles

**Step 3:** Verify all tests pass

**Verification:** `cd inkpy && pytest tests/test_styles.py -v`

---

### Task 3.3: Text Coloring and Styling ⬜
**Files:** `inkpy/inkpy/renderer/colorize.py`, `inkpy/tests/test_colorize.py`

**Step 1:** Write failing tests
```python
def test_foreground_color():
    result = colorize("Hello", "red", "foreground")
    assert "\x1b[31m" in result  # Red ANSI code

def test_background_color():
    result = colorize("Hello", "blue", "background")
    assert "\x1b[44m" in result  # Blue background

def test_hex_color():
    result = colorize("Hello", "#ff0000", "foreground")
    # Should use 24-bit color escape sequence
```

**Step 2:** Implement colorize function
- Support named colors (red, green, blue, etc.)
- Support hex colors (#RRGGBB)
- Support 256-color palette
- Apply as foreground or background

**Step 3:** Verify tests pass

**Verification:** `cd inkpy && pytest tests/test_colorize.py -v`

---

### Task 3.4: Border Rendering ⬜
**Files:** `inkpy/inkpy/renderer/borders.py`, `inkpy/tests/test_borders.py`

**Step 1:** Write failing tests
```python
def test_single_border():
    border = get_border_chars('single')
    assert border['topLeft'] == '┌'
    assert border['horizontal'] == '─'

def test_render_box_with_border():
    output = Output(width=10, height=5)
    render_border(output, x=0, y=0, width=10, height=5, style='single')
    result = output.get()['output']
    assert '┌' in result
    assert '┐' in result
```

**Step 2:** Implement border rendering
- Port border character sets from `cli-boxes`
- Support: single, double, round, bold, singleDouble, doubleSingle, classic
- Individual border visibility (borderTop, borderBottom, etc.)
- Border colors (borderColor, borderTopColor, etc.)

**Step 3:** Verify tests pass

**Verification:** `cd inkpy && pytest tests/test_borders.py -v`

---

### Task 3.5: Background Rendering ⬜
**Files:** `inkpy/inkpy/renderer/background.py`, `inkpy/tests/test_background.py`

**Step 1:** Write failing tests
```python
def test_render_background():
    output = Output(width=10, height=3)
    render_background(output, x=0, y=0, width=10, height=3, color='blue')
    result = output.get()['output']
    # Check that background color is applied to all cells
```

**Step 2:** Implement background rendering (port from `ink/src/render-background.ts`)
- Fill rectangular region with background color
- Integrate with Output buffer

**Step 3:** Verify tests pass

**Verification:** `cd inkpy && pytest tests/test_background.py -v`

---

### Task 3.6: Render Node to Output ⬜
**Files:** `inkpy/inkpy/renderer/render_node.py`, `inkpy/tests/test_render_node.py`

**Step 1:** Write failing tests
```python
def test_render_text_node():
    root = create_dom_node('ink-root')
    text = create_dom_node('ink-text')
    text.children = [create_text_node("Hello")]
    root.children = [text]

    calculate_layout(root, width=80)
    output = Output(width=80, height=24)
    render_node_to_output(root, output)

    assert "Hello" in output.get()['output']

def test_render_box_with_padding():
    # Box with padding should offset children
```

**Step 2:** Implement render_node_to_output
- Traverse DOM tree recursively
- Calculate absolute positions from Yoga layout
- Apply clipping for overflow
- Handle borders and backgrounds
- Render text with transformations

**Step 3:** Verify tests pass

**Verification:** `cd inkpy && pytest tests/test_render_node.py -v`

---

## Phase 4: Input Handling (Priority: HIGH)

### Task 4.1: Keypress Parser ⬜
**Files:** `inkpy/inkpy/input/keypress.py`, `inkpy/tests/test_keypress.py`

**Step 1:** Write failing tests
```python
def test_parse_arrow_keys():
    key = parse_keypress('\x1b[A')  # Up arrow
    assert key.name == 'up'
    assert key.upArrow == True

def test_parse_ctrl_c():
    key = parse_keypress('\x03')
    assert key.name == 'c'
    assert key.ctrl == True

def test_parse_enter():
    key = parse_keypress('\r')
    assert key.name == 'return'
```

**Step 2:** Implement parse_keypress (port from `ink/src/parse-keypress.ts`)
- Parse ANSI escape sequences
- Detect modifier keys (ctrl, shift, meta)
- Map key codes to named keys
- Handle special keys (arrows, function keys, etc.)

**Step 3:** Verify tests pass

**Verification:** `cd inkpy && pytest tests/test_keypress.py -v`

---

### Task 4.2: useInput Hook ⬜
**Files:** `inkpy/inkpy/hooks/use_input.py`, `inkpy/tests/test_use_input.py`

**Step 1:** Write failing tests
```python
def test_use_input_arrow_keys():
    """Test that arrow key presses are correctly detected"""
    captured_keys = []

    @component
    def App():
        def handler(input_str, key):
            captured_keys.append(key)
        use_input(handler)
        return Text("Press a key")

    # Simulate keypress
    # Verify handler was called with correct key info
```

**Step 2:** Implement use_input hook
- Subscribe to stdin events
- Parse keypresses
- Call handler with input string and key info
- Support `isActive` option to disable/enable
- Handle raw mode toggle

**Step 3:** Verify tests pass

**Verification:** `cd inkpy && pytest tests/test_use_input.py -v`

---

### Task 4.3: Stdin Context and Hook ⬜
**Files:** `inkpy/inkpy/hooks/use_stdin.py`, `inkpy/inkpy/components/stdin_context.py`

**Step 1:** Write failing tests
```python
def test_stdin_context():
    @component
    def App():
        stdin = use_stdin()
        assert stdin.stdin is not None
        assert callable(stdin.set_raw_mode)
        return Text("ok")
```

**Step 2:** Implement StdinContext and use_stdin
- Provide stdin stream access
- Raw mode management
- Event emitter for input events
- Internal exit on Ctrl+C handling

**Step 3:** Verify tests pass

**Verification:** `cd inkpy && pytest tests/test_use_stdin.py -v`

---

## Phase 5: Core Components (Priority: HIGH)

### Task 5.1: Enhanced Text Component ⬜
**Files:** `inkpy/inkpy/components/text.py`, `inkpy/tests/test_text_component.py`

**Step 1:** Write failing tests
```python
def test_text_color():
    t = Text("Hello", color="red")
    # Verify ANSI red code is applied

def test_text_bold():
    t = Text("Hello", bold=True)
    # Verify bold ANSI code

def test_text_wrap():
    t = Text("Hello World", wrap="truncate")
    # Verify truncation behavior
```

**Step 2:** Enhance Text component (port from `ink/src/components/Text.tsx`)
- Color support (foreground)
- Background color
- Bold, italic, underline, strikethrough, inverse
- Dim color
- Text wrap modes (wrap, truncate-end, truncate-middle, truncate-start)
- Accessibility support (aria-label, aria-hidden)

**Step 3:** Verify tests pass

**Verification:** `cd inkpy && pytest tests/test_text_component.py -v`

---

### Task 5.2: Enhanced Box Component ⬜
**Files:** `inkpy/inkpy/components/box.py`, `inkpy/tests/test_box_component.py`

**Step 1:** Write failing tests
```python
def test_box_border():
    b = Box(Text("Content"), borderStyle="single")
    # Verify border is rendered

def test_box_background_color():
    b = Box(Text("Content"), backgroundColor="blue")
    # Verify background color

def test_box_flex_props():
    b = Box(Text("Content"), flexDirection="row", justifyContent="center")
```

**Step 2:** Enhance Box component (port from `ink/src/components/Box.tsx`)
- All Styles props (flexDirection, padding, margin, etc.)
- Border styles and colors
- Background color
- Overflow handling
- Accessibility support (aria-role, aria-state)
- forwardRef support for DOM element access

**Step 3:** Verify tests pass

**Verification:** `cd inkpy && pytest tests/test_box_component.py -v`

---

### Task 5.3: Static Component ⬜
**Files:** `inkpy/inkpy/components/static.py`, `inkpy/tests/test_static.py`

**Step 1:** Write failing tests
```python
def test_static_renders_once():
    """Static content should render once and stay above dynamic content"""

def test_static_items():
    items = ["Item 1", "Item 2", "Item 3"]
    s = Static(items=items, children=lambda item: Text(item))
```

**Step 2:** Implement Static component (port from `ink/src/components/Static.tsx`)
- Render children only once (persist above dynamic output)
- Support `items` prop for dynamic static content
- Mark static node in DOM tree

**Step 3:** Verify tests pass

**Verification:** `cd inkpy && pytest tests/test_static.py -v`

---

### Task 5.4: Newline and Spacer Components ⬜
**Files:** `inkpy/inkpy/components/newline.py`, `inkpy/inkpy/components/spacer.py`

**Step 1:** Write failing tests
```python
def test_newline():
    n = Newline(count=2)
    # Should render 2 empty lines

def test_spacer():
    s = Spacer()
    # Should have flexGrow=1 to fill available space
```

**Step 2:** Implement components
- Newline: Simple component that renders N newlines
- Spacer: Box with flexGrow=1

**Step 3:** Verify tests pass

**Verification:** `cd inkpy && pytest tests/test_newline_spacer.py -v`

---

### Task 5.5: Transform Component ⬜
**Files:** `inkpy/inkpy/components/transform.py`, `inkpy/tests/test_transform.py`

**Step 1:** Write failing tests
```python
def test_transform_uppercase():
    t = Transform(transform=lambda s, i: s.upper(), children=Text("hello"))
    # Should output "HELLO"
```

**Step 2:** Implement Transform component (port from `ink/src/components/Transform.tsx`)
- Accept transform function `(line: str, index: int) -> str`
- Apply transformation to each line of output

**Step 3:** Verify tests pass

**Verification:** `cd inkpy && pytest tests/test_transform.py -v`

---

## Phase 6: App Infrastructure (Priority: MEDIUM)

### Task 6.1: App Context and useApp Hook ⬜
**Files:** `inkpy/inkpy/components/app_context.py`, `inkpy/inkpy/hooks/use_app.py`

**Step 1:** Write failing tests
```python
def test_use_app_exit():
    @component
    def App():
        app = use_app()
        # app.exit() should be callable
        return Text("ok")
```

**Step 2:** Implement AppContext and useApp
- Provide `exit(error?)` function
- Access to app lifecycle

**Step 3:** Verify tests pass

**Verification:** `cd inkpy && pytest tests/test_use_app.py -v`

---

### Task 6.2: Stdout/Stderr Hooks ⬜
**Files:** `inkpy/inkpy/hooks/use_stdout.py`, `inkpy/inkpy/hooks/use_stderr.py`

**Step 1:** Write failing tests
```python
def test_use_stdout():
    @component
    def App():
        stdout = use_stdout()
        assert hasattr(stdout, 'write')
        return Text("ok")
```

**Step 2:** Implement hooks
- useStdout: Access stdout stream and write function
- useStderr: Access stderr stream and write function

**Step 3:** Verify tests pass

**Verification:** `cd inkpy && pytest tests/test_std_hooks.py -v`

---

### Task 6.3: Focus Management ⬜
**Files:** `inkpy/inkpy/components/focus_context.py`, `inkpy/inkpy/hooks/use_focus.py`, `inkpy/inkpy/hooks/use_focus_manager.py`

**Step 1:** Write failing tests
```python
def test_use_focus():
    @component
    def FocusableItem():
        focus = use_focus()
        return Box(
            Text("Item" + (" [focused]" if focus.is_focused else "")),
            borderStyle="single" if focus.is_focused else None
        )

def test_focus_manager():
    @component
    def App():
        focus_mgr = use_focus_manager()
        # focus_mgr.focusNext(), focus_mgr.focusPrevious()
```

**Step 2:** Implement focus system
- FocusContext for focus state
- useFocus hook for individual components
- useFocusManager for focus navigation
- Tab/Shift+Tab default bindings

**Step 3:** Verify tests pass

**Verification:** `cd inkpy && pytest tests/test_focus.py -v`

---

### Task 6.4: Main Ink Class ⬜
**Files:** `inkpy/inkpy/ink.py`, `inkpy/tests/test_ink.py`

**Step 1:** Write failing tests
```python
def test_ink_render():
    @component
    def App():
        return Text("Hello, World!")

    ink = Ink(stdout=MockStdout())
    ink.render(App())
    # Verify output was written

def test_ink_unmount():
    ink = Ink(stdout=MockStdout())
    ink.render(App())
    ink.unmount()
    # Verify cleanup
```

**Step 2:** Implement Ink class (port from `ink/src/ink.tsx`)
- Constructor with options (stdout, stdin, stderr, debug, exitOnCtrlC, maxFps)
- render() method
- unmount() method
- waitUntilExit() async method
- Layout calculation on render
- Throttled rendering (maxFps)

**Step 3:** Verify tests pass

**Verification:** `cd inkpy && pytest tests/test_ink.py -v`

---

### Task 6.5: Render Function ⬜
**Files:** `inkpy/inkpy/render.py`, `inkpy/tests/test_render.py`

**Step 1:** Write failing tests
```python
def test_render():
    @component
    def App():
        return Text("Hello!")

    instance = render(App())
    assert hasattr(instance, 'rerender')
    assert hasattr(instance, 'unmount')
    assert hasattr(instance, 'waitUntilExit')
    instance.unmount()
```

**Step 2:** Implement render function (port from `ink/src/render.ts`)
- Create Ink instance
- Return Instance object with rerender, unmount, waitUntilExit, clear

**Step 3:** Verify tests pass

**Verification:** `cd inkpy && pytest tests/test_render.py -v`

---

## Phase 7: Integration & End-to-End (Priority: MEDIUM)

### Task 7.1: DOM Node System ⬜
**Files:** `inkpy/inkpy/dom.py`, `inkpy/tests/test_dom.py`

**Step 1:** Write failing tests
```python
def test_create_node():
    node = create_node('ink-box')
    assert node.node_name == 'ink-box'
    assert node.yoga_node is not None

def test_append_child():
    parent = create_node('ink-box')
    child = create_node('ink-text')
    append_child_node(parent, child)
    assert child in parent.child_nodes
```

**Step 2:** Implement DOM module (port from `ink/src/dom.ts`)
- DOMElement and TextNode classes
- createNode, createTextNode
- appendChildNode, removeChildNode, insertBeforeNode
- setAttribute, setStyle
- Text measurement function

**Step 3:** Verify tests pass

**Verification:** `cd inkpy && pytest tests/test_dom.py -v`

---

### Task 7.2: Counter Example (E2E Test) ⬜
**Files:** `inkpy/examples/counter.py`, `inkpy/tests/test_counter_e2e.py`

**Step 1:** Write failing test
```python
def test_counter_example():
    """End-to-end test of counter app"""
    # Run counter app
    # Simulate time passing
    # Verify output shows incrementing count
```

**Step 2:** Implement counter example
```python
from inkpy import render, Box, Text
from inkpy.hooks import use_state, use_effect

@component
def Counter():
    count, set_count = use_state(0)

    @use_effect(deps=[])
    async def timer():
        while True:
            await asyncio.sleep(1)
            set_count(lambda c: c + 1)

    return Box(
        Text(f"Count: {count}"),
        borderStyle="round"
    )

if __name__ == "__main__":
    render(Counter())
```

**Step 3:** Verify E2E test passes

**Verification:** `cd inkpy && python examples/counter.py` (manual verification)

---

### Task 7.3: Interactive Example (E2E Test) ⬜
**Files:** `inkpy/examples/interactive.py`

**Step 1:** Write failing test for input handling

**Step 2:** Implement interactive example with keyboard navigation
```python
@component
def SelectList():
    items = ["Option 1", "Option 2", "Option 3"]
    selected, set_selected = use_state(0)

    def handle_input(input_str, key):
        if key.upArrow:
            set_selected(lambda s: max(0, s - 1))
        elif key.downArrow:
            set_selected(lambda s: min(len(items) - 1, s + 1))
        elif key.return_:
            exit()

    use_input(handle_input)

    return Box(
        [Text(f"{'>' if i == selected else ' '} {item}")
         for i, item in enumerate(items)],
        flexDirection="column"
    )
```

**Step 3:** Manual verification

---

## Phase 8: Documentation & Polish (Priority: LOW)

### Task 8.1: API Documentation ⬜
**Files:** `inkpy/docs/api.md`

- Document all exported components
- Document all hooks
- Document render() function and options
- Include code examples

---

### Task 8.2: README ⬜
**Files:** `inkpy/README.md`

- Quick start guide
- Installation instructions
- Basic usage examples
- Link to full documentation

---

### Task 8.3: Type Hints ⬜
**Files:** All `inkpy/inkpy/**/*.py`

- Add comprehensive type hints
- Create typed interfaces for Props
- Consider py.typed marker for type checking

---

## Execution Order (Recommended)

1. **Phase 3 (Renderer)** - Complete the rendering pipeline
   - Task 3.1: Output Buffer
   - Task 3.2: Enhanced Styles
   - Task 3.3: Colorize
   - Task 3.4: Borders
   - Task 3.5: Background
   - Task 3.6: Render Node to Output

2. **Phase 5 (Components)** - Enhance core components
   - Task 5.1: Enhanced Text
   - Task 5.2: Enhanced Box
   - Task 5.3: Static
   - Task 5.4: Newline/Spacer
   - Task 5.5: Transform

3. **Phase 4 (Input)** - Add interactivity
   - Task 4.1: Keypress Parser
   - Task 4.2: useInput Hook
   - Task 4.3: Stdin Context

4. **Phase 6 (Infrastructure)** - App lifecycle
   - Task 6.1: App Context
   - Task 6.2: Stdout/Stderr Hooks
   - Task 6.3: Focus Management
   - Task 6.4: Ink Class
   - Task 6.5: Render Function

5. **Phase 7 (Integration)** - End-to-end testing
   - Task 7.1: DOM System
   - Task 7.2: Counter Example
   - Task 7.3: Interactive Example

6. **Phase 8 (Documentation)** - Polish
   - Task 8.1: API Docs
   - Task 8.2: README
   - Task 8.3: Type Hints

---

## File Structure (Target)

```
inkpy/
├── inkpy/
│   ├── __init__.py           # Public API exports
│   ├── ink.py                # Main Ink class
│   ├── render.py             # render() function
│   ├── dom.py                # DOM node management
│   ├── components/
│   │   ├── __init__.py
│   │   ├── box.py            # Box component
│   │   ├── text.py           # Text component
│   │   ├── static.py         # Static component
│   │   ├── newline.py        # Newline component
│   │   ├── spacer.py         # Spacer component
│   │   ├── transform.py      # Transform component
│   │   ├── app_context.py    # App context
│   │   ├── stdin_context.py  # Stdin context
│   │   ├── stdout_context.py # Stdout context
│   │   ├── stderr_context.py # Stderr context
│   │   └── focus_context.py  # Focus context
│   ├── hooks/
│   │   ├── __init__.py
│   │   ├── use_app.py
│   │   ├── use_input.py
│   │   ├── use_stdin.py
│   │   ├── use_stdout.py
│   │   ├── use_stderr.py
│   │   ├── use_focus.py
│   │   └── use_focus_manager.py
│   ├── layout/
│   │   ├── __init__.py
│   │   ├── yoga_node.py      # Yoga wrapper
│   │   ├── text_node.py      # Text measurement
│   │   └── styles.py         # Style application
│   ├── renderer/
│   │   ├── __init__.py
│   │   ├── renderer.py       # Main renderer
│   │   ├── output.py         # Output buffer
│   │   ├── colorize.py       # Color handling
│   │   ├── borders.py        # Border rendering
│   │   ├── background.py     # Background rendering
│   │   └── render_node.py    # Node to output
│   ├── input/
│   │   ├── __init__.py
│   │   └── keypress.py       # Keypress parsing
│   └── backend/
│       ├── __init__.py
│       └── tui_backend.py    # TUI backend
├── tests/
│   ├── test_yoga_node.py
│   ├── test_text_measurement.py
│   ├── test_renderer.py
│   ├── test_output.py
│   ├── test_styles.py
│   ├── test_colorize.py
│   ├── test_borders.py
│   ├── test_background.py
│   ├── test_render_node.py
│   ├── test_keypress.py
│   ├── test_use_input.py
│   ├── test_components.py
│   ├── test_static.py
│   ├── test_dom.py
│   ├── test_ink.py
│   └── test_render.py
├── examples/
│   ├── counter.py
│   ├── interactive.py
│   └── hello_world.py
├── docs/
│   └── api.md
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## Known Issues & Blockers

### Poga Frame Update Issues
Some tests in `test_yoga_node.py` are marked `xfail` due to poga's frame update behavior:
- `test_align_items_center` - Cross-axis alignment not updating frame
- `test_padding` - Padding not reflected in child positions
- `test_margin` - Margin not reflected in child positions
- `test_nested_layout` - Nested layouts with padding

**Workaround Options:**
1. Calculate positions manually during render traversal
2. Investigate poga's `preserve_origin` parameter
3. Consider alternative Yoga bindings

### ReactPy VDOM Structure
ReactPy's VDOM structure may differ from React. Need to verify:
- How component wrappers appear in VDOM tree
- How children are represented
- How to traverse to find actual elements

---

## Dependencies

**Required (already in requirements.txt):**
- `poga` - Yoga layout bindings
- `reactpy` - React-like component framework
- `pytest` - Testing

**To Add:**
- No additional dependencies required for core functionality
- Consider `wcwidth` for proper Unicode width handling
- Consider `prompt-toolkit` for advanced terminal handling (optional)

---

## Success Criteria

1. ✅ All unit tests pass
2. ✅ Counter example runs and displays correctly
3. ✅ Interactive example responds to keyboard input
4. ✅ Text wrapping works correctly
5. ✅ Borders and colors render correctly
6. ✅ Layout calculation matches original Ink behavior
7. ✅ Focus management works with Tab navigation
8. ✅ Static content persists above dynamic content

---

## Estimated Timeline

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| Phase 3 | 6 tasks | 3-4 hours |
| Phase 5 | 5 tasks | 2-3 hours |
| Phase 4 | 3 tasks | 2 hours |
| Phase 6 | 5 tasks | 3-4 hours |
| Phase 7 | 3 tasks | 2 hours |
| Phase 8 | 3 tasks | 2 hours |
| **Total** | **25 tasks** | **14-17 hours** |

---

## Next Steps

Ready to begin execution? Start with **Task 3.1: Output Buffer Class**.

Trigger: `execution-workflow.mdc`
