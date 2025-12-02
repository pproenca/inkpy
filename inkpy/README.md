# InkPy

React for CLIs in Python - Build beautiful command-line interfaces with ReactPy.

## Introduction

InkPy is a Python port of [Ink](https://github.com/vadimdemedes/ink), a React renderer for CLIs. It allows you to build interactive terminal applications using ReactPy components and hooks.

## Installation

```bash
# From the inkpy directory
uv sync

# Or with pip
pip install -e .
```

## Quick Start

```python
from reactpy import component
from inkpy import render, Text

@component
def App():
    return Text("Hello, World!", color="green", bold=True)

if __name__ == "__main__":
    render(App())
```

## Features

- 🎨 **Beautiful UI** - Build terminal UIs with flexbox layout (powered by Yoga/Poga)
- ⚛️ **ReactPy Components** - Use familiar React patterns with `@component` decorator
- 🎹 **Input Handling** - `use_input` hook for keyboard events
- 🎯 **Focus Management** - Built-in Tab/Shift+Tab navigation with `use_focus`
- 🖼️ **Styling** - Colors, borders, backgrounds, padding, margin
- 📐 **Flexbox Layout** - Full flexbox support (flexDirection, justifyContent, alignItems, etc.)
- ♿ **Accessibility** - Screen reader support with ARIA attributes
- 📦 **Type Hints** - Full type support for better DX

## Components

| Component | Description |
|-----------|-------------|
| `Box` | Flexbox container with borders, backgrounds, padding |
| `Text` | Styled text with colors, bold, italic, underline |
| `Static` | Content that renders once and persists |
| `Newline` | Insert empty lines |
| `Spacer` | Flexible space (flexGrow=1) |
| `Transform` | Transform text output |

## Hooks

| Hook | Description |
|------|-------------|
| `use_input` | Handle keyboard input |
| `use_app` | Access app lifecycle (exit) |
| `use_focus` | Focus management for components |
| `use_focus_manager` | Control focus navigation |
| `use_stdin` | Access stdin stream |
| `use_stdout` | Access stdout stream |
| `use_stderr` | Access stderr stream |

## Examples

See the `examples/` directory:

```bash
# Hello World
python examples/hello_world.py

# Counter with async state
python examples/counter.py

# Interactive keyboard navigation
python examples/interactive.py
```

## Testing

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_components.py -v
```

## Project Status

**Parity with Ink: ~95%+**

✅ Complete:
- Core rendering pipeline
- All 8 components (Box, Text, Static, Newline, Spacer, Transform, ErrorOverview, App)
- All 8 hooks
- All 7 contexts
- Input handling with keypress parsing
- Focus management with Tab navigation
- Screen reader accessibility support
- Border and background rendering
- Text wrapping and truncation
- ANSI color support (named, hex, RGB, 256-color)

See `../docs/plans/2025-12-01-inkpy-100-percent-parity.md` for detailed status.

## License

MIT

## Acknowledgments

InkPy is a Python port of [Ink](https://github.com/vadimdemedes/ink) by Vadim Demedes.
