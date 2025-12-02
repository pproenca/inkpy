# InkPy 100% Parity Implementation Plan

> **Goal:** Achieve full feature parity between Ink (TypeScript) and InkPy (Python)
>
> **Tech Stack:** Python 3.9+, ReactPy, Poga (Yoga layout), pytest
>
> **Source Reference:** `ink/src/`
>
> **Target:** `inkpy/inkpy/`
>
> **Skills Reference:** See `@.cursor/skills/test-driven-development.md` for TDD protocol
>
> **Last Updated:** 2025-12-01 (Comprehensive Deep Analysis)

---

## Executive Summary

This deep analysis covers **every file** in the Ink TypeScript source (42 files, ~3,500+ lines) and compares it with the InkPy Python port. The analysis identifies specific gaps blocking 100% parity.

### Overall Parity Status: ~82%

| Category | Ink Files | InkPy Status | Parity | Critical Gaps |
|----------|-----------|--------------|--------|---------------|
| **Core System** | 4 files | Implemented | 90% | batchedUpdates not available |
| **Rendering Pipeline** | 7 files | Implemented | 85% | Output.get() ANSI handling |
| **Layout/Styles** | 4 files | Implemented | 95% | Minor edge cases |
| **Components** | 8 files | 8 implemented | 90% | ErrorOverview code excerpts |
| **Contexts** | 7 files | 7 implemented | 100% | ✅ Complete |
| **Hooks** | 8 files | 8 implemented | 90% | batchedUpdates |
| **Input System** | 1 file | Implemented | 100% | ✅ Complete |
| **Terminal Mgmt** | 3 files | Implemented | 95% | Minor ANSI escapes |

---

## Complete File-by-File Analysis

### 1. Core System Files

#### `ink/src/ink.tsx` (441 lines) → `inkpy/ink.py` ✅ 90%

| Feature | TS Line | InkPy | Status |
|---------|---------|-------|--------|
| `Options` type (stdout, stdin, stderr, debug, etc.) | 33-45 | ✅ | Done |
| `RenderMetrics` type | 26-31 | ✅ | Done |
| `getTerminalWidth()` | 154-158 | ✅ | Done |
| `resized()` handler | 160-173 | ✅ | Done |
| `calculateLayout()` | 179-189 | ✅ | Done |
| `onRender()` with all modes (debug, CI, screenReader, normal) | 191-293 | ✅ | Done |
| Throttled rendering via `es-toolkit/compat` | 83-99 | ⚠️ | Basic Python throttle |
| `render()` method with reconciler | 295-320 | ✅ | ReactPy Layout |
| `writeToStdout()` / `writeToStderr()` | 322-361 | ✅ | Done |
| `unmount()` with cleanup | 364-404 | ✅ | Done |
| `waitUntilExit()` promise | 406-413 | ✅ | asyncio.Future |
| `clear()` | 415-419 | ✅ | Done |
| `patchConsole()` | 421-439 | ✅ | Done |
| `signalExit` handling | 129 | ✅ | signal.SIGTERM/SIGINT |
| `isInCi` detection | 145 | ✅ | Done |
| Screen reader mode with `wrapAnsi` | 226-263 | ⚠️ | **Needs wrap-ansi** |
| `ansiEscapes.clearTerminal` | 272 | ⚠️ | Basic `\x1b[2J\x1b[H` |

**Gap:** Screen reader mode needs proper `wrap-ansi` equivalent for text wrapping.

---

#### `ink/src/reconciler.ts` (340 lines) → `inkpy/backend/tui_backend.py` ✅ 85%

| Feature | TS Line | InkPy | Status |
|---------|---------|-------|--------|
| `getRootHostContext()` | 117-119 | ✅ | Done |
| `getChildHostContext()` | 144-153 | ✅ | Done |
| `createInstance()` | 155-201 | ✅ | Done |
| `createTextInstance()` | 203-211 | ✅ | Done |
| `commitUpdate()` with prop diffing | 251-291 | ✅ | Done |
| `commitTextUpdate()` | 292-294 | ✅ | Done |
| `hideInstance()` / `unhideInstance()` | 220-225 | ✅ | Done |
| `hideTextInstance()` / `unhideTextInstance()` | 213-218 | ✅ | Done |
| `resetAfterCommit()` | 123-143 | ✅ | Done |
| `cleanupYogaNode()` | 86-89 | ✅ | Done |
| `diff()` helper | 53-84 | ✅ | Done |
| `batchedUpdates()` | Used in useInput | ❌ | **Not available in ReactPy** |

**Gap:** `reconciler.batchedUpdates()` is used in `use-input.ts` but ReactPy doesn't expose this.

---

#### `ink/src/render.ts` (168 lines) → `inkpy/render.py` ✅ 100%

| Feature | TS Line | InkPy | Status |
|---------|---------|-------|--------|
| `RenderOptions` type | 7-77 | ✅ | Done |
| `Instance` type | 79-101 | ✅ | Done |
| `render()` function | 106-138 | ✅ | Done |
| `getOptions()` helper | 142-153 | ✅ | Done |
| `getInstance()` singleton | 155-167 | ✅ | Done |

---

#### `ink/src/dom.ts` (265 lines) → `inkpy/dom.py` ✅ 95%

| Feature | TS Line | InkPy | Status |
|---------|---------|-------|--------|
| `DOMElement` type | 25-70 | ✅ | Done |
| `TextNode` type | 72-76 | ✅ | Done |
| `createNode()` | 89-106 | ✅ | Done |
| `createTextNode()` | 203-215 | ✅ | Done |
| `appendChildNode()` | 108-129 | ✅ | Done |
| `insertBeforeNode()` | 131-164 | ✅ | Done |
| `removeChildNode()` | 166-184 | ✅ | Done |
| `setAttribute()` | 186-197 | ✅ | Done |
| `setStyle()` | 199-201 | ✅ | Done |
| `setTextNodeValue()` | 257-264 | ✅ | Done |
| `measureTextNode()` | 217-241 | ✅ | Done |
| `findClosestYogaNode()` | 243-249 | ✅ | Done |
| `markNodeAsDirty()` | 251-255 | ✅ | Done |
| `squashTextNodes()` | Used from squash-text-nodes.ts | ✅ | Inline in dom.py |
| `internal_accessibility` attribute | 31-62 | ✅ | Done |
| `internal_transform` callback | 29 | ✅ | Done |
| `onComputeLayout` / `onRender` / `onImmediateRender` | 67-69 | ✅ | Done |
| `isStaticDirty` / `staticNode` | 65-66 | ✅ | Done |

---

### 2. Rendering Pipeline Files

#### `ink/src/renderer.ts` (78 lines) → `inkpy/renderer/renderer.py` ✅ 95%

| Feature | TS Line | InkPy | Status |
|---------|---------|-------|--------|
| Screen reader output mode | 13-35 | ✅ | Done |
| Normal render mode with Output buffer | 37-67 | ✅ | Done |
| Static node detection | 47-57 | ✅ | Done |
| Output height calculation | 59 | ✅ | Done |

---

#### `ink/src/render-node-to-output.ts` (215 lines) → `inkpy/renderer/render_node.py` ✅ 85%

| Feature | TS Line | InkPy | Status |
|---------|---------|-------|--------|
| `applyPaddingToText()` with `indentString` | 18-28 | ⚠️ | Basic version |
| `renderNodeToScreenReaderOutput()` | 32-97 | ✅ | Done |
| `renderNodeToOutput()` | 100-212 | ✅ | Done |
| Skip static elements option | 117-119 | ✅ | Done |
| Transform function handling | 136-138 | ✅ | Done |
| Clipping with border adjustments | 166-195 | ✅ | Done |
| `widestLine` width calculation | 144 | ✅ | Using string_width |
| ARIA role/state in screen reader output | 79-94 | ✅ | Done |

**Gap:** `applyPaddingToText` uses `indent-string` library. Python has basic implementation.

---

#### `ink/src/output.ts` (245 lines) → `inkpy/renderer/output.py` ✅ 90%

| Feature | TS Line | InkPy | Status |
|---------|---------|-------|--------|
| `Output` class constructor | 51-62 | ✅ | Done |
| `write()` method | 64-83 | ✅ | Done |
| `clip()` / `unclip()` methods | 85-96 | ✅ | Done |
| `get()` with styled chars | 98-243 | ✅ | Done |
| `@alcalzone/ansi-tokenize` functions | 6-9 | ✅ | ansi_tokenize.py |
| `styledCharsFromTokens()` | 201 | ✅ | Done |
| `styledCharsToString()` | 235 | ✅ | Done |
| Multi-column character handling (CJK) | 208-223 | ✅ | wcwidth |
| ANSI preservation during clipping | 160-185 | ⚠️ | **Verify edge cases** |

---

#### `ink/src/render-border.ts` (126 lines) → `inkpy/renderer/borders.py` ✅ 100%

| Feature | TS Line | InkPy | Status |
|---------|---------|-------|--------|
| Border style lookup from `cli-boxes` | 17-19 | ✅ | Done |
| Per-edge border colors | 21-27 | ✅ | Done |
| Per-edge dim colors | 29-39 | ✅ | Done |
| Show/hide per-edge borders | 41-44 | ✅ | Done |
| Top/bottom/left/right border rendering | 49-121 | ✅ | Done |

---

#### `ink/src/render-background.ts` (53 lines) → `inkpy/renderer/background.py` ✅ 100%

| Feature | TS Line | InkPy | Status |
|---------|---------|-------|--------|
| Border-aware content area calculation | 19-29 | ✅ | Done |
| Background fill for each row | 36-48 | ✅ | Done |

---

#### `ink/src/colorize.ts` (73 lines) → `inkpy/renderer/colorize.py` ✅ 100%

| Feature | TS Line | InkPy | Status |
|---------|---------|-------|--------|
| Named colors via chalk | 21-31 | ✅ | Done |
| Hex colors | 33-37 | ✅ | Done |
| ansi256 colors | 39-51 | ✅ | Done |
| RGB colors | 53-68 | ✅ | Done |
| Foreground/background support | 16, 26-30 | ✅ | Done |

---

#### `ink/src/squash-text-nodes.ts` (48 lines) → inline in `inkpy/dom.py` ✅ 100%

| Feature | TS Line | InkPy | Status |
|---------|---------|-------|--------|
| Recursive text node concatenation | 9-45 | ✅ | Done |
| Transform function application | 33-37 | ✅ | Done |

---

### 3. Layout/Styles Files

#### `ink/src/styles.ts` (586 lines) → `inkpy/layout/styles.py` ✅ 95%

| Feature | TS Line | InkPy | Status |
|---------|---------|-------|--------|
| `Styles` type definition | 7-303 | ✅ | Done |
| `applyPositionStyles()` | 305-313 | ✅ | Done |
| `applyMarginStyles()` | 315-343 | ✅ | Done |
| `applyPaddingStyles()` | 345-373 | ✅ | Done |
| `applyFlexStyles()` (all flex properties) | 375-490 | ✅ | Done |
| `applyDimensionStyles()` (width, height, min*) | 492-528 | ✅ | Done |
| `applyDisplayStyles()` | 530-536 | ✅ | Done |
| `applyBorderStyles()` | 538-558 | ✅ | Done |
| `applyGapStyles()` | 560-572 | ✅ | Done |
| flexBasis with percent/auto | 418-427 | ⚠️ | **Verify auto handling** |

---

#### `ink/src/wrap-text.ts` (48 lines) → `inkpy/wrap_text.py` ✅ 95%

| Feature | TS Line | InkPy | Status |
|---------|---------|-------|--------|
| Caching mechanism | 6 | ✅ | Done |
| `wrap` mode via `wrap-ansi` | 21-26 | ✅ | ANSI-aware |
| `truncate-end` via `cli-truncate` | 28-39 | ✅ | Done |
| `truncate-middle` | 31-33 | ✅ | Done |
| `truncate-start` | 35-37 | ✅ | Done |

---

#### `ink/src/measure-text.ts` (33 lines) → `inkpy/measure_text.py` ✅ 100%

| Feature | TS Line | InkPy | Status |
|---------|---------|-------|--------|
| Cache Map | 3 | ✅ | Done |
| `widestLine` for width | 24 | ✅ | Done |
| Line count for height | 25 | ✅ | Done |

---

#### `ink/src/get-max-width.ts` (14 lines) → `inkpy/get_max_width.py` ✅ 100%

| Feature | TS Line | InkPy | Status |
|---------|---------|-------|--------|
| Computed width minus padding and border | 3-10 | ✅ | Done |

---

### 4. Components Files

#### `ink/src/components/App.tsx` (379 lines) → `inkpy/components/app.py` ✅ 95%

| Feature | TS Line | InkPy | Status |
|---------|---------|-------|--------|
| `getDerivedStateFromError()` | 45-47 | ✅ | try/except |
| `componentDidMount()` cursor hide | 129-131 | ✅ | In LogUpdate |
| `componentWillUnmount()` cleanup | 133-140 | ✅ | Done |
| `componentDidCatch()` | 142-144 | ✅ | Done |
| `handleSetRawMode()` with ref counting | 146-181 | ✅ | Done |
| `handleReadable()` stdin loop | 183-190 | ✅ | Background thread |
| `handleInput()` (Tab, Shift+Tab, Escape, Ctrl+C) | 192-215 | ✅ | Done |
| `handleExit()` | 217-223 | ✅ | Done |
| Focus management (add/remove/activate/deactivate) | 277-342 | ✅ | Done |
| `findNextFocusable()` / `findPreviousFocusable()` | 344-378 | ✅ | Done |
| `internal_eventEmitter` (EventEmitter) | 60 | ✅ | Done |
| All context providers | 68-127 | ✅ | Done |

---

#### `ink/src/components/Box.tsx` (118 lines) → `inkpy/components/box.py` ✅ 95%

| Feature | TS Line | InkPy | Status |
|---------|---------|-------|--------|
| Props type with ARIA | 8-56 | ✅ | Done |
| Default flex styles | 81-92 | ✅ | Done |
| Screen reader label handling | 75-78, 98 | ⚠️ | **Needs context check** |
| `BackgroundContext.Provider` | 103-108 | ✅ | Done |
| `internal_accessibility` attribute | 93-96 | ✅ | Done |

---

#### `ink/src/components/Text.tsx` (146 lines) → `inkpy/components/text.py` ✅ 90%

| Feature | TS Line | InkPy | Status |
|---------|---------|-------|--------|
| Color props | 22-28 | ✅ | Done |
| Style props (bold, italic, etc.) | 30-59 | ✅ | Done |
| ARIA props | 13-18 | ⚠️ | Partial |
| `useContext(accessibilityContext)` | 85 | ⚠️ | **Needs implementation** |
| `useContext(backgroundContext)` | 86 | ✅ | Done |
| Transform function | 94-131 | ✅ | Done |
| Screen reader mode (aria-label) | 87-88, 133, 142 | ⚠️ | **Needs context** |

**Gap:** Text component needs to use `accessibilityContext` to check `isScreenReaderEnabled`.

---

#### `ink/src/components/Static.tsx` (59 lines) → `inkpy/components/static.py` ✅ 95%

| Feature | TS Line | InkPy | Status |
|---------|---------|-------|--------|
| `items` prop | 8 | ✅ | Done |
| `style` prop | 14 | ✅ | Done |
| `children` render function | 18 | ✅ | Done |
| `useMemo` / `useState` / `useLayoutEffect` | 30-38 | ✅ | Done |
| `internal_static` attribute | 54 | ✅ | Done |

---

#### `ink/src/components/Transform.tsx` (43 lines) → `inkpy/components/transform.py` ✅ 90%

| Feature | TS Line | InkPy | Status |
|---------|---------|-------|--------|
| `transform` prop | 13 | ✅ | Done |
| `accessibilityLabel` prop | 8 | ❌ | **Missing** |
| `useContext(accessibilityContext)` | 26 | ❌ | **Missing** |
| Screen reader mode | 37-39 | ❌ | **Missing** |

**Gap:** Transform needs `accessibilityLabel` prop and screen reader support.

---

#### `ink/src/components/Newline.tsx` (18 lines) → `inkpy/components/newline.py` ✅ 100%

| Feature | TS Line | InkPy | Status |
|---------|---------|-------|--------|
| `count` prop | 9 | ✅ | Done |
| Repeat newlines | 16 | ✅ | Done |

---

#### `ink/src/components/Spacer.tsx` (12 lines) → `inkpy/components/spacer.py` ✅ 100%

| Feature | TS Line | InkPy | Status |
|---------|---------|-------|--------|
| `flexGrow: 1` | 10 | ✅ | Done |

---

#### `ink/src/components/ErrorOverview.tsx` (138 lines) → `inkpy/components/error_overview.py` ⚠️ 70%

| Feature | TS Line | InkPy | Status |
|---------|---------|-------|--------|
| `cleanupPath()` | 11-13 | ⚠️ | Basic |
| `stackUtils.parseLine()` | 26 | ❌ | **Missing** |
| `codeExcerpt()` source code display | 33 | ❌ | **Missing** |
| Error message display | 43-51 | ✅ | Done |
| File path display | 53-59 | ⚠️ | Basic |
| Code excerpt with line numbers | 61-89 | ❌ | **Missing** |
| Stack trace parsing and display | 92-133 | ⚠️ | Basic |

**Gap:** ErrorOverview needs `stack-utils` and `code-excerpt` equivalents for Python.

---

### 5. Context Files (All ✅ 100%)

| File | InkPy | Status |
|------|-------|--------|
| `AccessibilityContext.ts` | `accessibility_context.py` | ✅ |
| `AppContext.ts` | `app_context.py` | ✅ |
| `BackgroundContext.ts` | `background_context.py` | ✅ |
| `FocusContext.ts` | `focus_context.py` | ✅ |
| `StdinContext.ts` | `stdin_context.py` | ✅ |
| `StdoutContext.ts` | `stdout_context.py` | ✅ |
| `StderrContext.ts` | `stderr_context.py` | ✅ |

---

### 6. Hook Files

#### `ink/src/hooks/use-input.ts` (196 lines) → `inkpy/hooks/use_input.py` ✅ 90%

| Feature | TS Line | InkPy | Status |
|---------|---------|-------|--------|
| `Key` type | 9-79 | ✅ | Done |
| `isActive` option | 89 | ✅ | Done |
| Raw mode setup/teardown | 118-128 | ✅ | Done |
| `internal_eventEmitter` subscription | 188 | ✅ | Done |
| Key parsing from `parseKeypress` | 136 | ✅ | Done |
| Shift detection from uppercase | 174-177 | ✅ | Done |
| Meta key stripping | 167-169 | ✅ | Done |
| Ctrl+C handling | 180-181 | ✅ | Done |
| `reconciler.batchedUpdates()` | 182-184 | ❌ | **Not available** |
| `nonAlphanumericKeys` check | 161-163 | ✅ | Done |

**Gap:** `reconciler.batchedUpdates()` wraps input handler in TS but not available in ReactPy.

---

#### `ink/src/hooks/use-focus.ts` (84 lines) → `inkpy/hooks/use_focus.py` ✅ 95%

| Feature | TS Line | InkPy | Status |
|---------|---------|-------|--------|
| Random ID generation | 46-48 | ✅ | Done |
| `add()` / `remove()` effects | 50-56 | ✅ | Done |
| `activate()` / `deactivate()` effects | 58-64 | ✅ | Done |
| Raw mode setup in focus | 66-76 | ✅ | Done |
| `isRawModeSupported` check | 67 | ✅ | Done |
| Return `isFocused` and `focus` | 78-81 | ✅ | Done |

---

#### Other Hooks (All ✅ 100%)

| Hook | InkPy | Status |
|------|-------|--------|
| `use-focus-manager.ts` | `use_focus_manager.py` | ✅ |
| `use-app.ts` | `use_app.py` | ✅ |
| `use-stdin.ts` | `use_stdin.py` | ✅ |
| `use-stdout.ts` | `use_stdout.py` | ✅ |
| `use-stderr.ts` | `use_stderr.py` | ✅ |
| `use-is-screen-reader-enabled.ts` | `use_is_screen_reader_enabled.py` | ✅ |

---

### 7. Input System

#### `ink/src/parse-keypress.ts` (243 lines) → `inkpy/input/keypress.py` ✅ 100%

| Feature | TS Line | InkPy | Status |
|---------|---------|-------|--------|
| `metaKeyCodeRe` regex | 4 | ✅ | Done |
| `fnKeyRe` regex | 6-7 | ✅ | Done |
| `keyName` mapping | 9-92 | ✅ | Done |
| `nonAlphanumericKeys` | 94 | ✅ | Done |
| `isShiftKey()` | 96-111 | ✅ | Done |
| `isCtrlKey()` | 113-127 | ✅ | Done |
| `ParsedKey` type | 129-138 | ✅ | Done |
| `parseKeypress()` function | 140-240 | ✅ | Done |

---

### 8. Terminal Management Files

#### `ink/src/log-update.ts` (161 lines) → `inkpy/log_update.py` ✅ 95%

| Feature | TS Line | InkPy | Status |
|---------|---------|-------|--------|
| `createStandard()` | 12-59 | ✅ | Done |
| `createIncremental()` | 61-146 | ✅ | Done |
| `render()` with diff | 20-34, 69-121 | ✅ | Done |
| `clear()` | 36-40, 123-127 | ✅ | Done |
| `done()` | 42-50, 129-137 | ✅ | Done |
| `sync()` | 52-56, 139-143 | ✅ | Done |
| `cliCursor.hide()` / `.show()` | 22-24, 46-49 | ✅ | Done |
| `ansiEscapes.eraseLines()` | 32 | ✅ | Done |
| `ansiEscapes.cursorUp()` | 101-104 | ✅ | Done |
| `ansiEscapes.cursorNextLine` | 110 | ✅ | Done |
| `ansiEscapes.eraseLine` | 114 | ✅ | Done |

---

#### `ink/src/instances.ts` (11 lines) → `inkpy/instances.py` ✅ 100%

| Feature | TS Line | InkPy | Status |
|---------|---------|-------|--------|
| Map for stdout → Ink instances | 4-10 | ✅ | Done |

---

#### `ink/src/measure-element.ts` (24 lines) → `inkpy/measure_element.py` ✅ 100%

| Feature | TS Line | InkPy | Status |
|---------|---------|-------|--------|
| `measureElement()` function | 17-21 | ✅ | Done |
| Return width/height | 18-20 | ✅ | Done |

---

### 9. Public API Exports

#### `ink/src/index.ts` (29 lines) → `inkpy/__init__.py` ✅ 100%

| Export | InkPy | Status |
|--------|-------|--------|
| `render` | ✅ | Done |
| `Box` | ✅ | Done |
| `Text` | ✅ | Done |
| `Static` | ✅ | Done |
| `Transform` | ✅ | Done |
| `Newline` | ✅ | Done |
| `Spacer` | ✅ | Done |
| `useInput` | ✅ | Done |
| `useApp` | ✅ | Done |
| `useStdin` | ✅ | Done |
| `useStdout` | ✅ | Done |
| `useStderr` | ✅ | Done |
| `useFocus` | ✅ | Done |
| `useFocusManager` | ✅ | Done |
| `useIsScreenReaderEnabled` | ✅ | Done |
| `measureElement` | ✅ | Done |
| `DOMElement` type | ✅ | Done |
| Type exports | ⚠️ | Python typing |

---

## Gap Summary: Blocking 100% Parity

### Critical Gaps (MUST FIX)

| ID | Gap | Impact | Effort |
|----|-----|--------|--------|
| G1 | **Transform `accessibilityLabel`** | Screen reader support broken | 30 min |
| G2 | **Text screen reader context** | Screen reader support broken | 1 hour |
| G3 | **ErrorOverview code excerpts** | Error display incomplete | 2-3 hours |
| G4 | **Box screen reader label** | Screen reader support incomplete | 30 min |

### Minor Gaps (SHOULD FIX)

| ID | Gap | Impact | Effort |
|----|-----|--------|--------|
| G5 | `reconciler.batchedUpdates()` | Input handler not batched | N/A (ReactPy limitation) |
| G6 | `wrapAnsi` in screen reader mode | Text wrapping in SR mode | 1 hour |
| G7 | `indent-string` in applyPaddingToText | Minor layout edge case | 30 min |
| G8 | flexBasis auto handling verification | Potential layout edge case | 1 hour |

---

## Implementation Tasks

### Task 1: Transform accessibilityLabel Support
**Priority:** CRITICAL | **Effort:** 30 min

**Files:**
- Modify: `inkpy/components/transform.py`
- Test: `tests/test_transform.py`

**Implementation:**
```python
# Add accessibilityLabel prop
@component
def Transform(
    children,
    transform: Callable[[str, int], str],
    accessibility_label: Optional[str] = None,  # NEW
):
    # Get accessibility context
    ctx = use_context(accessibility_context)
    is_screen_reader = ctx.get('isScreenReaderEnabled', False)

    # Show accessibility label in screen reader mode
    content = accessibility_label if (is_screen_reader and accessibility_label) else children

    # ... rest of implementation
```

---

### Task 2: Text Screen Reader Context
**Priority:** CRITICAL | **Effort:** 1 hour

**Files:**
- Modify: `inkpy/components/text.py`
- Test: `tests/test_text_screen_reader.py`

**Implementation:**
```python
@component
def Text(
    children,
    color=None,
    # ... other props
    aria_label: Optional[str] = None,
    aria_hidden: bool = False,
):
    # Get accessibility context
    ctx = use_context(accessibility_context)
    is_screen_reader = ctx.get('isScreenReaderEnabled', False)

    # Use aria-label in screen reader mode
    content = aria_label if (is_screen_reader and aria_label) else children

    # Hide if aria-hidden and screen reader enabled
    if is_screen_reader and aria_hidden:
        return None

    # ... rest of implementation
```

---

### Task 3: ErrorOverview Code Excerpts
**Priority:** CRITICAL | **Effort:** 2-3 hours

**Files:**
- Modify: `inkpy/components/error_overview.py`
- Test: `tests/test_error_overview.py`

**Implementation:**
```python
import linecache
import traceback
import os

def cleanup_path(path: str) -> str:
    """Remove file:// prefix and cwd from path"""
    if path.startswith('file://'):
        path = path[7:]
    cwd = os.getcwd()
    if path.startswith(cwd):
        path = path[len(cwd):].lstrip('/')
    return path

def get_code_excerpt(filepath: str, line: int, context: int = 3) -> List[Dict]:
    """Get code excerpt around error line"""
    lines = []
    for i in range(max(1, line - context), line + context + 1):
        code = linecache.getline(filepath, i)
        if code:
            lines.append({'line': i, 'value': code.rstrip()})
    return lines

def parse_stack_line(line: str) -> Optional[Dict]:
    """Parse a stack trace line to extract file, line, column, function"""
    # Match Python traceback format: File "path", line N, in func
    import re
    match = re.match(r'\s*File "([^"]+)", line (\d+)(?:, in (.+))?', line)
    if match:
        return {
            'file': match.group(1),
            'line': int(match.group(2)),
            'function': match.group(3) or '<module>',
        }
    return None
```

---

### Task 4: Box Screen Reader Label
**Priority:** CRITICAL | **Effort:** 30 min

**Files:**
- Modify: `inkpy/components/box.py`
- Test: `tests/test_box_aria.py`

**Implementation:**
Ensure Box component shows `aria-label` instead of children when screen reader is enabled.

---

### Task 5: Screen Reader wrapAnsi
**Priority:** HIGH | **Effort:** 1 hour

**Files:**
- Modify: `inkpy/ink.py`
- Create: `inkpy/wrap_ansi.py` (or use existing wrap_text)

**Implementation:**
Add proper text wrapping for screen reader output mode.

---

## Verification Checklist

### For 100% Parity

- [x] Event emitter distributes keyboard input
- [x] useInput hook receives and processes input
- [x] Focus navigation with Tab/Shift+Tab works
- [x] Escape clears focus
- [x] Ctrl+C exits (when exitOnCtrlC=true)
- [x] Terminal resize handled
- [x] CI mode works (no ANSI escape updates)
- [ ] Screen reader mode outputs accessible text ← **G1, G2, G4**
- [x] Debug mode shows all output
- [x] Incremental rendering reduces flicker
- [x] Border rendering matches original
- [x] Color output matches (named, hex, rgb, ansi256)
- [x] Text wrapping matches
- [x] Text truncation matches (truncate-start/middle/end)
- [ ] Error display shows source code excerpts ← **G3**
- [x] Static component renders permanently
- [x] All 8 hooks functional
- [x] All 7 contexts functional
- [x] All 8 components functional

### Test Scenarios to Verify

1. **Hello World** - basic render ✅
2. **Counter** - state updates ✅
3. **Interactive** - keyboard input ✅
4. **Multi-focus** - Tab navigation ✅
5. **Static + Dynamic** - mixed content ✅
6. **Resize** - terminal resize handling ✅
7. **Error** - error boundary display with code excerpt ← **G3**
8. **Screen Reader** - accessible output ← **G1, G2, G4**

---

## Implementation Order

```
Phase 1 (Critical - ~4 hours total):
├── Task 1: Transform accessibilityLabel (30min)
├── Task 2: Text Screen Reader Context (1h)
├── Task 3: ErrorOverview Code Excerpts (2-3h)
└── Task 4: Box Screen Reader Label (30min)

Phase 2 (High Priority - ~2.5 hours total):
├── Task 5: Screen Reader wrapAnsi (1h)
├── Task 6: applyPaddingToText indent-string (30min)
└── Task 7: flexBasis auto verification (1h)

TOTAL: ~6.5 hours to 100% parity
```

---

## Progress Summary

| Category | Completed | Remaining | Notes |
|----------|-----------|-----------|-------|
| Core System | 4/4 files | 0 | batchedUpdates is ReactPy limitation |
| Rendering | 7/7 files | 0 | Minor verification needed |
| Layout/Styles | 4/4 files | 0 | ✅ Complete |
| Components | 8/8 files | 4 gaps | Screen reader & error |
| Contexts | 7/7 files | 0 | ✅ Complete |
| Hooks | 8/8 files | 0 | batchedUpdates is limitation |
| Input | 1/1 files | 0 | ✅ Complete |
| Terminal | 3/3 files | 0 | ✅ Complete |

**Overall: ~82% complete → 100% with 4 critical tasks**

---

## Next Steps

Ready to execute? The priority order is:

1. **Task 1 & 4**: Quick wins (1 hour total) - accessibility support
2. **Task 2**: Text screen reader (1 hour)
3. **Task 3**: ErrorOverview (2-3 hours) - biggest gap

To execute, use: `@.cursor/rules/execution-workflow.mdc`
