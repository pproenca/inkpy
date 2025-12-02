# InkPy Capabilities for Building Claude-Code-Like CLIs

> **Goal:** Identify flows, use-cases, and features from claude-code CLI that need to be supported in InkPy to build similar interactive terminal applications
>
> **Tech Stack:** Python 3.9+, InkPy (custom reconciler), Poga (Yoga layout), Rich console integration
>
> **Source Analysis:** `claude-code/claude-code/src/` (~15 TypeScript files, ~4,000 lines)
>
> **Date:** 2025-12-02

---

## Executive Summary

Claude-Code CLI is a sophisticated interactive terminal application built with Ink (React for CLIs). This analysis extracts the **UI patterns, flows, and capabilities** required to build an equivalent application using InkPy.

### Key Findings

| Category | Claude-Code Features | InkPy Status | Priority |
|----------|---------------------|--------------|----------|
| **Terminal Interface** | Chalk formatting, spinners, tables, prompts | ⚠️ Partial | HIGH |
| **Input Handling** | Multi-type prompts, validation, raw mode | ⚠️ Partial | HIGH |
| **Command System** | Registry, routing, argument parsing | ❌ Not in scope | MEDIUM |
| **Progress Indicators** | Spinners, progress bars, status updates | ⚠️ Partial | HIGH |
| **Streaming Output** | Incremental text display, typewriter effect | ⚠️ Partial | HIGH |
| **Error Display** | Formatted errors, resolution suggestions | ✅ Complete | LOW |

---

## Part 1: Claude-Code UI Flows Analysis

### 1.1 Main Application Loop

```
┌─────────────────────────────────────────────────────────────────┐
│                     CLAUDE-CODE CLI FLOW                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐    ┌──────────────┐    ┌─────────────┐           │
│  │ CLI Init │───>│ Auth Check   │───>│ Welcome     │           │
│  └──────────┘    └──────────────┘    │ Message     │           │
│                         │            └─────────────┘           │
│                         ▼                   │                   │
│                  ┌──────────────┐           ▼                   │
│                  │ Login Flow   │    ┌─────────────┐           │
│                  │ (if needed)  │    │ Main REPL   │◄──────┐   │
│                  └──────────────┘    │ Loop        │       │   │
│                                      └─────────────┘       │   │
│                                            │               │   │
│                                            ▼               │   │
│                                      ┌─────────────┐       │   │
│                                      │ User Input  │       │   │
│                                      │ (prompt)    │       │   │
│                                      └─────────────┘       │   │
│                                            │               │   │
│                          ┌─────────────────┼───────────────┐   │
│                          ▼                 ▼               ▼   │
│                    ┌───────────┐    ┌───────────┐   ┌────────┐ │
│                    │ /command  │    │ Natural   │   │ Exit   │ │
│                    │ Processing│    │ Language  │   │        │ │
│                    └───────────┘    │ Processing│   └────────┘ │
│                          │          └───────────┘              │
│                          ▼                │                    │
│                    ┌───────────┐          ▼                    │
│                    │ Execute   │    ┌───────────┐              │
│                    │ Handler   │    │ AI Request│              │
│                    └───────────┘    │ (Spinner) │              │
│                          │          └───────────┘              │
│                          │                │                    │
│                          │                ▼                    │
│                          │          ┌───────────┐              │
│                          │          │ Streaming │              │
│                          │          │ Response  │              │
│                          │          └───────────┘              │
│                          │                │                    │
│                          └────────────────┴────────────────────┘
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Identified UI Patterns

#### Pattern 1: Welcome Screen
**File:** `terminal/index.ts` lines 100-117

```typescript
displayWelcome(): void {
  this.clear();
  console.log(chalk.blue.bold('\n  Claude Code CLI'));
  console.log(chalk.gray(`  Version ${version} (Research Preview)\n`));
  console.log(chalk.white(`  Welcome! Type ${chalk.cyan('/help')} ...`));
  console.log(chalk.dim('  Pro tip: Use Ctrl+C to interrupt...\n'));
}
```

**InkPy Equivalent Needed:**
- Styled text with multiple colors
- Clear screen functionality
- Box layouts for framing

---

#### Pattern 2: Spinner with Status Updates
**File:** `terminal/index.ts` lines 233-282

```typescript
spinner(text: string, id: string = 'default'): SpinnerInstance {
  const spinner = ora({ text, spinner: 'dots', color: 'cyan' }).start();
  return {
    update: (newText: string) => { spinner.text = newText; },
    succeed: (text?: string) => { spinner.succeed(text); },
    fail: (text?: string) => { spinner.fail(text); },
    stop: () => { spinner.stop(); }
  };
}
```

**InkPy Requirement:**
- ✅ `Spinner` component exists
- ⚠️ Need: Dynamic status update methods (succeed/fail/warn/info)
- ⚠️ Need: Icon-based status indicators (✓, ✗, ⚠, ℹ)

---

#### Pattern 3: Multi-Type Prompts
**File:** `terminal/prompt.ts` lines 50-162

| Prompt Type | Description | InkPy Status |
|-------------|-------------|--------------|
| `input` | Text input | ✅ `TextInput` |
| `password` | Masked input | ⚠️ Need mask prop |
| `confirm` | Yes/No | ✅ `ConfirmInput` |
| `list` | Single select | ✅ `SelectInput` |
| `checkbox` | Multi select | ✅ `MultiSelect` |
| `editor` | Multi-line text | ❌ Not implemented |

---

#### Pattern 4: Table Display
**File:** `terminal/index.ts` lines 204-221

```typescript
table(data: any[][], options: { header?: string[]; border?: boolean }): void {
  // Uses 'table' npm package for formatting
}
```

**InkPy Requirement:**
- ✅ `Table` component exists
- ⚠️ Need: Header row styling
- ⚠️ Need: Border style options

---

#### Pattern 5: Streaming Text Output
**File:** `ai/client.ts` lines 193-235

```typescript
async completeStream(prompt, options, onEvent): Promise<void> {
  // Reads streaming response chunks
  for (const line of lines) {
    if (trimmedLine.startsWith('data: ')) {
      const eventData = JSON.parse(trimmedLine.slice(6));
      onEvent(eventData);  // Updates UI incrementally
    }
  }
}
```

**InkPy Requirement:**
- ⚠️ Need: Incremental text rendering (typewriter effect)
- ⚠️ Need: SSE (Server-Sent Events) integration pattern
- ⚠️ Need: Streaming state management

---

#### Pattern 6: Formatted Error Display
**File:** `errors/formatter.ts` lines 35-91

```typescript
function formatUserError(error: UserError): string {
  let message = `Error: ${error.message}`;
  if (error.resolution) {
    message += '\n\nTo resolve this:';
    resolutionSteps.forEach(step => {
      message += `\n• ${step}`;
    });
  }
  return message;
}
```

**InkPy Status:** ✅ `ErrorOverview` component handles this well

---

#### Pattern 7: Code Block Display
**File:** `terminal/formatting.ts` lines 110-134

```typescript
function formatCodeBlocks(text: string, enableHighlighting: boolean): string {
  // Format with border, language indicator, syntax highlighting
}
```

**InkPy Requirement:**
- ✅ `CodeBlock` component exists
- ⚠️ Need: Language-aware syntax highlighting
- ⚠️ Need: Line numbers option

---

### 1.3 Command Flow Analysis

#### Login Command Flow
```
User: claude-code login
       │
       ▼
┌──────────────────┐
│ Check for API key│
│ in environment   │
└────────┬─────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌────────┐
│Has key│ │No key  │
└───┬───┘ └───┬────┘
    │         │
    ▼         ▼
┌───────────┐ ┌───────────────┐
│ Validate  │ │ Start OAuth   │
│ API key   │ │ flow          │
└─────┬─────┘ └───────┬───────┘
      │               │
      │         ┌─────┴─────┐
      │         ▼           ▼
      │   ┌──────────┐ ┌─────────┐
      │   │Open      │ │Wait for │
      │   │browser   │ │callback │
      │   └──────────┘ └────┬────┘
      │                     │
      └──────────┬──────────┘
                 ▼
         ┌──────────────┐
         │ Store token  │
         │ Show success │
         └──────────────┘
```

**InkPy Components Needed:**
- Spinner during validation
- Success/Error message display
- Link component for OAuth URL

---

#### Ask Command Flow
```
User: claude-code ask "How do I..."
       │
       ▼
┌──────────────────┐
│ Show thinking    │──────┐
│ spinner          │      │
└────────┬─────────┘      │
         │                │ On interrupt
         ▼                │ (Ctrl+C)
┌──────────────────┐      │
│ Stream response  │      │
│ incrementally    │      │
└────────┬─────────┘      │
         │                │
         ▼                ▼
┌──────────────────┐ ┌────────────┐
│ Display complete │ │ Cancel     │
│ formatted output │ │ gracefully │
└──────────────────┘ └────────────┘
```

**InkPy Components Needed:**
- Spinner with dynamic text
- Streaming text display
- Interrupt handling (Ctrl+C)
- Markdown-like formatting

---

## Part 2: InkPy Capability Gap Analysis

### 2.1 Currently Available Components

| Component | Description | Claude-Code Usage |
|-----------|-------------|-------------------|
| `Box` | Flexbox container | ✅ Layout, borders, padding |
| `Text` | Styled text | ✅ Colored output, emphasis |
| `TextInput` | Single-line input | ✅ User prompts |
| `SelectInput` | Arrow-key selection | ✅ List prompts |
| `MultiSelect` | Checkbox selection | ✅ Multi-choice prompts |
| `ConfirmInput` | Yes/No prompt | ✅ Confirmation dialogs |
| `Spinner` | Loading indicator | ⚠️ Need status methods |
| `Table` | Data display | ⚠️ Need header styling |
| `CodeBlock` | Code display | ⚠️ Need syntax highlighting |
| `Link` | Clickable URL | ✅ OAuth URLs |
| `Static` | Non-updating content | ✅ Log history |

### 2.2 Missing Capabilities

#### HIGH Priority (Blocking for Claude-Code Equivalent)

| Capability | Description | Effort |
|------------|-------------|--------|
| **SpinnerWithStatus** | Spinner with succeed/fail/warn/info states | 1 day |
| **StreamingText** | Incremental text rendering | 2 days |
| **PasswordInput** | TextInput with mask character | 0.5 days |
| **EditorInput** | Multi-line text editor | 3 days |
| **ProgressBar** | Determinate progress indicator | 1 day |

#### MEDIUM Priority (Enhanced UX)

| Capability | Description | Effort |
|------------|-------------|--------|
| **MarkdownRenderer** | Render markdown to terminal | 3 days |
| **SyntaxHighlighter** | Language-aware code highlighting | 2 days |
| **TableWithHeaders** | Table with styled header row | 0.5 days |
| **Tooltip** | Hover/focus tooltips | 1 day |

#### LOW Priority (Nice to Have)

| Capability | Description | Effort |
|------------|-------------|--------|
| **Autocomplete** | Input with suggestions | 2 days |
| **TreeView** | Hierarchical data display | 2 days |
| **Tabs** | Tabbed interface | 1 day |
| **Modal** | Overlay dialogs | 2 days |

---

## Part 3: Feature-to-Test Mapping

### 3.1 Test Categories Needed

#### Integration Tests: Full Application Flows

| Test Case | Description | Components Involved |
|-----------|-------------|---------------------|
| `test_welcome_screen` | Display styled welcome message | Box, Text |
| `test_login_oauth_flow` | OAuth authentication UI | Spinner, Link, Text |
| `test_ask_with_spinner` | Show spinner during AI request | Spinner, Text |
| `test_streaming_response` | Display streaming AI output | StreamingText |
| `test_command_help` | Display formatted help | Box, Text, Table |
| `test_error_with_resolution` | Show error with suggestions | ErrorOverview |
| `test_confirm_action` | Yes/No confirmation prompt | ConfirmInput |
| `test_select_option` | Single selection from list | SelectInput |
| `test_multi_select` | Multiple selection | MultiSelect |
| `test_text_input_validation` | Input with validation | TextInput |
| `test_ctrl_c_interrupt` | Handle interrupt gracefully | use_input hook |

#### Component Tests: Individual UI Elements

| Test Case | Description | Status |
|-----------|-------------|--------|
| `test_spinner_states` | Test succeed/fail/warn/info | ⚠️ Need to add |
| `test_streaming_text_incremental` | Render text char by char | ❌ Need component |
| `test_password_input_mask` | Mask characters in input | ⚠️ Need to add |
| `test_table_header_styling` | Bold/colored header row | ⚠️ Need to add |
| `test_code_block_line_numbers` | Line number display | ⚠️ Need to add |
| `test_progress_bar_determinate` | Progress percentage | ❌ Need component |

---

## Part 4: Implementation Plan

### Phase 1: Enhanced Spinner (1 day)

**Task 1.1: Add Status States to Spinner**

**Files:**
- Modify: `inkpy/components/spinner.py`
- Test: `tests/components/test_spinner.py`

**Implementation:**
```python
class SpinnerStatus(Enum):
    SPINNING = "spinning"
    SUCCESS = "success"
    FAILURE = "failure"
    WARNING = "warning"
    INFO = "info"

def Spinner(
    text: str = "",
    status: SpinnerStatus = SpinnerStatus.SPINNING,
    success_icon: str = "✓",
    failure_icon: str = "✗",
    warning_icon: str = "⚠",
    info_icon: str = "ℹ"
) -> Element:
    ...
```

**Test:**
```python
def test_spinner_success_state():
    def App():
        return Spinner(text="Completed", status=SpinnerStatus.SUCCESS)
    
    output = render_to_string(App())
    assert "✓" in output
    assert "Completed" in output
```

---

### Phase 2: Streaming Text Component (2 days)

**Task 2.1: Create StreamingText Component**

**Files:**
- Create: `inkpy/components/streaming_text.py`
- Test: `tests/components/test_streaming_text.py`

**Implementation:**
```python
def StreamingText(
    text: str,
    speed_ms: int = 50,  # ms per character
    on_complete: Optional[Callable] = None
) -> Element:
    """Renders text incrementally like a typewriter effect."""
    displayed, set_displayed = use_state("")
    
    use_effect(lambda: animate_text(text, speed_ms, set_displayed, on_complete), [text])
    
    return Text(displayed)
```

**Test:**
```python
def test_streaming_text_incremental():
    def App():
        return StreamingText(text="Hello, World!", speed_ms=10)
    
    instance = render(App())
    
    # After 30ms, should have ~3 characters
    await asyncio.sleep(0.03)
    output = instance.get_output()
    assert len(output) >= 3
    assert len(output) < 13
    
    # After full duration, should have all characters
    await asyncio.sleep(0.2)
    output = instance.get_output()
    assert "Hello, World!" in output
```

---

### Phase 3: Password Input (0.5 days)

**Task 3.1: Add Mask Prop to TextInput**

**Files:**
- Modify: `inkpy/components/text_input.py`
- Test: `tests/components/test_text_input.py`

**Implementation:**
```python
def TextInput(
    value: str = "",
    on_change: Optional[Callable[[str], None]] = None,
    on_submit: Optional[Callable[[str], None]] = None,
    placeholder: str = "",
    mask: Optional[str] = None,  # NEW: If set, masks each char with this string
    ...
) -> Element:
    display_value = mask * len(value) if mask else value
    ...
```

**Test:**
```python
def test_text_input_password_mask():
    received = []
    def App():
        value, set_value = use_state("")
        def on_change(v):
            set_value(v)
            received.append(v)
        return TextInput(value=value, on_change=on_change, mask="*")
    
    instance = render(App())
    instance.stdin.write("secret")
    
    output = instance.get_output()
    assert "******" in output  # Masked display
    assert received[-1] == "secret"  # Actual value
```

---

### Phase 4: Progress Bar (1 day)

**Task 4.1: Create ProgressBar Component**

**Files:**
- Create: `inkpy/components/progress_bar.py`
- Test: `tests/components/test_progress_bar.py`

**Implementation:**
```python
def ProgressBar(
    value: float,  # 0.0 to 1.0
    width: int = 40,
    filled_char: str = "█",
    empty_char: str = "░",
    show_percentage: bool = True,
    color: Optional[str] = "green"
) -> Element:
    filled = int(width * value)
    empty = width - filled
    
    bar = filled_char * filled + empty_char * empty
    percentage = f" {int(value * 100)}%" if show_percentage else ""
    
    return Box(children=[
        Text(f"[{bar}]{percentage}", color=color)
    ])
```

**Test:**
```python
def test_progress_bar_50_percent():
    def App():
        return ProgressBar(value=0.5, width=20)
    
    output = render_to_string(App())
    assert "██████████░░░░░░░░░░" in output
    assert "50%" in output
```

---

### Phase 5: Enhanced Table (0.5 days)

**Task 5.1: Add Header Styling to Table**

**Files:**
- Modify: `inkpy/components/table.py`
- Test: `tests/components/test_table.py`

**Implementation:**
```python
def Table(
    data: List[List[Any]],
    headers: Optional[List[str]] = None,
    header_style: Optional[Dict[str, Any]] = None,  # NEW: {"bold": True, "color": "cyan"}
    ...
) -> Element:
    ...
```

---

### Phase 6: Example Application (2 days)

**Task 6.1: Create Mini Claude-Code Demo**

**Files:**
- Create: `inkpy/examples/claude_code_demo.py`

**Implementation:**
```python
"""
Mini Claude-Code CLI Demo using InkPy

Demonstrates:
- Welcome screen with styled text
- Spinner with status transitions
- Streaming text output
- Input prompts (text, select, confirm)
- Error display with resolution
- Table display
"""

def main():
    def App():
        state, set_state = use_state("welcome")
        
        if state == "welcome":
            return WelcomeScreen(on_continue=lambda: set_state("prompt"))
        elif state == "prompt":
            return PromptScreen(on_submit=lambda q: set_state(("loading", q)))
        elif state[0] == "loading":
            return LoadingScreen(query=state[1], on_complete=lambda r: set_state(("result", r)))
        elif state[0] == "result":
            return ResultScreen(result=state[1], on_new=lambda: set_state("prompt"))
    
    render(App)

if __name__ == "__main__":
    main()
```

---

## Part 5: Test Scenarios Matrix

### 5.1 Component-Level Tests

| Component | Test Scenario | Input | Expected Output |
|-----------|--------------|-------|-----------------|
| Spinner | Success state | `status=SUCCESS` | "✓" icon displayed |
| Spinner | Failure state | `status=FAILURE` | "✗" icon displayed |
| Spinner | Custom text | `text="Loading..."` | "Loading..." displayed |
| StreamingText | Incremental render | `text="Hello"` | H→He→Hel→Hell→Hello |
| StreamingText | Completion callback | `on_complete=cb` | Callback invoked |
| PasswordInput | Masked display | `mask="*"` | "****" for "test" |
| ProgressBar | Half progress | `value=0.5` | "█████░░░░░ 50%" |
| ProgressBar | Full progress | `value=1.0` | "██████████ 100%" |
| Table | With headers | `headers=["A","B"]` | Bold header row |

### 5.2 Integration Tests

| Flow | Test Scenario | Steps | Expected Outcome |
|------|--------------|-------|------------------|
| Welcome | Display welcome | Launch app | Welcome message visible |
| Auth | Login with API key | Enter key | Success message |
| Auth | Login failure | Invalid key | Error with resolution |
| Query | Ask question | Enter query | Spinner → Response |
| Query | Streaming response | Long response | Incremental display |
| Query | Interrupt | Ctrl+C during stream | Graceful cancellation |
| Help | Show commands | Type /help | Formatted command list |
| Exit | Quit app | Type /exit | Clean termination |

### 5.3 Edge Case Tests

| Scenario | Test | Expected Behavior |
|----------|------|-------------------|
| Long text | Wrap/truncate | Respects terminal width |
| Unicode | Emoji in output | Correct width calculation |
| ANSI | Colored input | Preserved through processing |
| Resize | Terminal resize | Layout recalculates |
| Rapid input | Fast typing | No dropped characters |
| Focus | Tab navigation | Correct focus order |

---

## Part 6: Verification Criteria

### 6.1 Definition of Done

Each capability is complete when:

1. ✅ Component/feature implemented
2. ✅ Unit tests passing
3. ✅ Integration tests passing
4. ✅ Documentation updated
5. ✅ Example usage created
6. ✅ No type errors (mypy)
7. ✅ No lint errors (ruff)

### 6.2 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Test coverage | ≥95% | pytest-cov |
| New components | 5 | Component count |
| New tests | 30+ | Test count |
| Example app | 1 complete | Demo working |
| Performance | <100ms render | Benchmark |

---

## Appendix: Claude-Code Feature Extraction Summary

### A.1 Terminal Interface Features

From `terminal/index.ts`:
- ✅ Screen clearing (`clearScreen`)
- ✅ Terminal size detection (`getTerminalSize`)
- ✅ Resize handling (`process.stdout.on('resize')`)
- ✅ Color support detection (`chalk.level`)
- ⚠️ Spinner management (need status states)
- ⚠️ Table formatting (need header styling)
- ✅ Formatted messages (info/success/warn/error)
- ✅ Clickable links (`terminalLink`)

### A.2 Prompt Types

From `terminal/prompt.ts`:
- ✅ Text input (`promptText`)
- ⚠️ Password input (`promptPassword`) - need mask
- ✅ Confirmation (`promptConfirm`)
- ✅ List selection (`promptList`)
- ✅ Checkbox selection (`promptCheckbox`)
- ❌ Editor prompt (`promptEditor`) - not implemented

### A.3 AI Integration Patterns

From `ai/client.ts`:
- ⚠️ Streaming response handling (need component)
- ✅ Error handling with categories
- ✅ Timeout/retry logic
- ✅ Request/response types

### A.4 Command Patterns

From `commands/register.ts`:
- Command registry pattern (application-level, not InkPy concern)
- Argument parsing (application-level)
- Handler execution (application-level)
- Help generation (application-level)

---

## Conclusion

InkPy has **strong foundational capabilities** for building Claude-Code-like CLIs. The main gaps are:

1. **Spinner with status states** - Critical for showing operation results
2. **Streaming text component** - Essential for AI response display
3. **Password input masking** - Required for secure credential entry
4. **Progress bar** - Useful for file operations, uploads

With these additions (estimated **4-5 days of work**), InkPy will be fully capable of building sophisticated interactive CLIs like Claude-Code.

**Recommended Next Steps:**
1. Implement SpinnerWithStatus (Phase 1)
2. Implement StreamingText (Phase 2)
3. Add password mask to TextInput (Phase 3)
4. Create ProgressBar (Phase 4)
5. Build example demo application (Phase 6)

---

## References

- Ink source: `ink/src/` (42 files)
- Claude-Code source: `claude-code/claude-code/src/` (15 files)
- InkPy source: `inkpy/inkpy/` (35 files)
- InkPy tests: `inkpy/tests/` (60+ test files)

