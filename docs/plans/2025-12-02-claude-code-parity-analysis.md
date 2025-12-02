# Claude-Code Feature Analysis & InkPy Implementation Plan

## Executive Summary

This document analyzes the `claude-code` CLI (a TypeScript/Ink-based terminal application) to identify the flows, use-cases, and capabilities that InkPy must support to enable building similar applications 100% in Python.

## Claude-Code Architecture Overview

### High-Level Components

1. **Terminal Interface Layer** - User input/output handling, formatting, display
2. **Command Processing Engine** - Natural language parsing, routing, execution
3. **Interactive Session Loop** - REPL-style interface with state management
4. **Progress & Status Indicators** - Spinners, loading states, notifications
5. **Prompt System** - Input, password, confirmation, selection prompts
6. **Formatted Output** - Tables, code blocks, colored messages, links

---

## Use Cases & Flows Extracted from Claude-Code

### Flow 1: Interactive Command Loop (REPL)

**Description**: A persistent session where users can enter commands, receive responses, and maintain state between interactions.

**Components Required**:
- Continuous input handling (`use_input`)
- Command parsing and routing
- Session state management
- Welcome screen display
- Exit handling

**InkPy Status**: ⚠️ **Partial** - Has `use_input` but needs higher-level REPL abstraction

**Example Pattern**:
```python
@component
def CommandLoop():
    command, set_command = use_state("")
    history, set_history = use_state([])
    
    def handle_input(char, key):
        if key.return_key:
            # Execute command
            set_history(lambda h: h + [command])
            set_command("")
        elif key.backspace:
            set_command(lambda c: c[:-1])
        else:
            set_command(lambda c: c + char)
    
    use_input(handle_input)
    
    return Box(flex_direction="column", children=[
        *[Text(cmd) for cmd in history],
        Text(f"> {command}_")
    ])
```

---

### Flow 2: Text Input Prompts

**Description**: Collecting user text input with validation, default values, and transformations.

**Components Required**:
- Text input component
- Cursor management
- Validation feedback
- Default value handling
- Submit handling (Enter key)

**InkPy Status**: ❌ **Missing** - No `TextInput` component

**Required Component**: `TextInput`
```python
@component
def TextInput(props):
    """
    Props:
        value: str - Current input value
        on_change: Callable[[str], None] - Called on value change
        on_submit: Callable[[str], None] - Called on Enter
        placeholder: str - Placeholder text
        focus: bool - Whether input is focused
        mask: str | None - Character to mask input (for passwords)
    """
```

---

### Flow 3: Selection Lists (Single Choice)

**Description**: Present a list of options for the user to navigate and select.

**Components Required**:
- Focusable list items
- Arrow key navigation
- Visual selection indicator
- Confirmation (Enter key)
- Screen reader support

**InkPy Status**: ⚠️ **Partial** - Has `use_focus` but needs `SelectInput` component

**Required Component**: `SelectInput`
```python
@component
def SelectInput(props):
    """
    Props:
        items: List[dict] - Items with 'label' and 'value'
        on_select: Callable[[Any], None] - Called with selected value
        indicator: str - Selection indicator (default: ">")
        initial_index: int - Initial selected index
    """
```

---

### Flow 4: Multi-Select (Checkboxes)

**Description**: Allow users to select multiple items from a list.

**Components Required**:
- Checkbox state per item
- Toggle selection (Space key)
- Submit selection (Enter key)
- Visual checked/unchecked indicators

**InkPy Status**: ❌ **Missing** - No `MultiSelect` component

**Required Component**: `MultiSelect`
```python
@component
def MultiSelect(props):
    """
    Props:
        items: List[dict] - Items with 'label', 'value', 'checked'
        on_submit: Callable[[List[Any]], None] - Called with selected values
        check_indicator: str - Checked indicator (default: "✓")
    """
```

---

### Flow 5: Confirmation Prompts

**Description**: Yes/No confirmation dialogs.

**Components Required**:
- Binary choice handling
- Default value support
- Keyboard shortcuts (Y/N)

**InkPy Status**: ❌ **Missing** - No `ConfirmInput` component

**Required Component**: `ConfirmInput`
```python
@component
def ConfirmInput(props):
    """
    Props:
        message: str - Confirmation message
        on_confirm: Callable[[bool], None] - Called with True/False
        default: bool - Default value
    """
```

---

### Flow 6: Progress Indicators (Spinners)

**Description**: Display loading/processing state with animated indicators.

**Components Required**:
- Animation frame cycling
- Multiple spinner styles
- Status text updates
- Success/failure/warning states

**InkPy Status**: ❌ **Missing** - No `Spinner` component

**Required Component**: `Spinner`
```python
@component
def Spinner(props):
    """
    Props:
        type: str - Spinner type ('dots', 'line', etc.)
        text: str - Text to display next to spinner
    """
```

---

### Flow 7: Table Display

**Description**: Display tabular data with columns and formatting.

**Components Required**:
- Column width calculation
- Header styling
- Row rendering
- Border options

**InkPy Status**: ⚠️ **Possible** - Can build with `Box` but no dedicated component

**Pattern Available**:
```python
@component
def Table():
    return Box(flex_direction="column", children=[
        Box(children=[
            Box(width="30%", children=[Text("Name", bold=True)]),
            Box(width="70%", children=[Text("Email", bold=True)])
        ]),
        *[row_component(user) for user in users]
    ])
```

---

### Flow 8: Formatted Output Messages

**Description**: Display styled messages (info, success, warning, error).

**InkPy Status**: ✅ **Available** - Can use `Text` with `color` prop

**Pattern**:
```python
Text("✓ Success!", color="green")
Text("⚠ Warning!", color="yellow")
Text("✗ Error!", color="red")
Text("ℹ Info", color="blue")
```

---

### Flow 9: Code Block Display with Syntax Highlighting

**Description**: Display code with language-specific highlighting.

**InkPy Status**: ⚠️ **Partial** - Has `Text` but no syntax highlighting

**Required Enhancement**:
- Syntax highlighting integration (Pygments)
- Code block borders
- Language indicators

---

### Flow 10: Terminal Resize Handling

**Description**: Respond to terminal size changes and re-render.

**InkPy Status**: ⚠️ **Unknown** - Needs verification

**Required Hook**: `use_terminal_dimensions`
```python
def use_terminal_dimensions() -> dict:
    """
    Returns:
        {'columns': int, 'rows': int}
    """
```

---

### Flow 11: Screen Clearing

**Description**: Clear terminal screen for fresh display.

**InkPy Status**: ⚠️ **Partial** - Needs verification of `clear_screen` capability

---

### Flow 12: Session State Persistence

**Description**: Maintain state across the session (history, context).

**InkPy Status**: ✅ **Available** - Can use `use_state` for session state

---

## Gap Analysis Summary

### Components Needed

| Component | Priority | Status | Description |
|-----------|----------|--------|-------------|
| `TextInput` | **Critical** | ❌ Missing | Text input with cursor, validation |
| `SelectInput` | **Critical** | ❌ Missing | Single-choice list selection |
| `MultiSelect` | **High** | ❌ Missing | Multi-choice checkbox list |
| `ConfirmInput` | **High** | ❌ Missing | Yes/No confirmation |
| `Spinner` | **High** | ❌ Missing | Animated loading indicator |
| `PasswordInput` | **High** | ❌ Missing | Masked text input |
| `Table` | **Medium** | ⚠️ Partial | Structured with Box (could be utility) |
| `Link` | **Low** | ❌ Missing | Clickable terminal link |

### Hooks Needed

| Hook | Priority | Status | Description |
|------|----------|--------|-------------|
| `use_terminal_dimensions` | **High** | ❌ Missing | Get terminal size |
| `use_text_input` | **High** | ❌ Missing | Controlled text input state |
| `use_spinner` | **Medium** | ❌ Missing | Spinner state management |

### Infrastructure Improvements

| Feature | Priority | Status | Description |
|---------|----------|--------|-------------|
| Render throttling | **High** | ⚠️ Unknown | Prevent flicker/excessive renders |
| Error boundaries | **Medium** | ⚠️ Partial | Component error handling |
| Suspense support | **Low** | ❌ Missing | Async loading states |

---

## Implementation Phases

### Phase 1: Core Input Components (Critical)

**Goal**: Enable building interactive CLI applications with user input

**Tasks**:
1. Implement `TextInput` component
2. Implement `SelectInput` component  
3. Implement `ConfirmInput` component
4. Add `use_terminal_dimensions` hook
5. Verify/implement terminal resize handling

**Estimated Effort**: 2-3 days

### Phase 2: Extended Input & Progress (High)

**Goal**: Support password input, multi-select, and loading states

**Tasks**:
1. Implement `PasswordInput` (or add mask prop to TextInput)
2. Implement `MultiSelect` component
3. Implement `Spinner` component
4. Add spinner animation frame utilities

**Estimated Effort**: 2 days

### Phase 3: Enhanced Display (Medium)

**Goal**: Rich output formatting and display

**Tasks**:
1. Add syntax highlighting support (integrate Pygments)
2. Create `CodeBlock` component or utility
3. Implement `Link` component for terminal links
4. Add `Table` utility/component

**Estimated Effort**: 1-2 days

### Phase 4: Infrastructure (High)

**Goal**: Production-ready stability

**Tasks**:
1. Verify/implement render throttling
2. Enhance error boundaries
3. Add integration tests for all new components
4. Performance optimization

**Estimated Effort**: 1-2 days

---

## Test Cases to Build

### Component Tests

#### TextInput Tests
- [ ] Renders with placeholder when empty
- [ ] Updates value on character input
- [ ] Handles backspace/delete
- [ ] Calls on_submit on Enter
- [ ] Shows cursor at correct position
- [ ] Validates input if validator provided
- [ ] Works with mask for password mode

#### SelectInput Tests
- [ ] Renders all items
- [ ] Shows indicator on selected item
- [ ] Navigates up/down with arrow keys
- [ ] Wraps around at boundaries
- [ ] Calls on_select on Enter
- [ ] Supports initial_index prop

#### Spinner Tests
- [ ] Animates through frames
- [ ] Shows text alongside spinner
- [ ] Stops animation when unmounted
- [ ] Supports different spinner types

### Integration Tests

- [ ] Full REPL-style command loop
- [ ] Form with multiple input types
- [ ] Loading state → result display flow
- [ ] Error handling and display

---

## Example: Claude-Code-like CLI in InkPy (Target)

```python
from inkpy import render, Box, Text, use_state, use_input
from inkpy.components import TextInput, SelectInput, Spinner

@component
def ClaudeCodeApp():
    mode, set_mode = use_state("idle")
    command, set_command = use_state("")
    result, set_result = use_state("")
    
    async def execute_command(cmd):
        set_mode("loading")
        # ... execute command ...
        set_result("Command executed successfully")
        set_mode("idle")
    
    def handle_submit(text):
        execute_command(text)
        set_command("")
    
    return Box(flex_direction="column", padding=1, children=[
        # Header
        Text("Claude Code CLI", bold=True, color="blue"),
        
        # Result area
        Text(result) if result else None,
        
        # Loading indicator
        Spinner(text="Processing...") if mode == "loading" else None,
        
        # Input area
        Box(margin_top=1, children=[
            Text("> "),
            TextInput(
                value=command,
                on_change=set_command,
                on_submit=handle_submit,
                placeholder="Enter a command..."
            )
        ]) if mode == "idle" else None
    ])

render(ClaudeCodeApp())
```

---

## Conclusion

To achieve 100% parity for building a `claude-code`-like application with InkPy, we need to implement:

1. **4 Critical Components**: TextInput, SelectInput, ConfirmInput, PasswordInput
2. **2 High-Priority Components**: Spinner, MultiSelect
3. **2-3 Hooks**: use_terminal_dimensions, use_text_input
4. **Infrastructure**: Render throttling, enhanced error handling

The current InkPy foundation is solid with Box, Text, use_input, use_focus, and the reconciler. The primary gaps are in **high-level interactive input components** that are commonly needed for CLI applications.

---

## Appendix: Claude-Code Command Categories

From the analysis, claude-code supports these command categories:

| Category | Commands | InkPy Relevance |
|----------|----------|-----------------|
| **Auth** | login, logout | Session state |
| **Assistance** | ask, explain, fix | Display results |
| **Code Generation** | generate, refactor | Display code blocks |
| **System** | config, run, search, theme, verbosity | Settings UI |
| **Session** | exit, quit, clear, reset, history, commands, help | REPL flow |
| **Feedback** | bug, feedback | Form input |

All of these can be implemented with the proposed components and current InkPy capabilities.

