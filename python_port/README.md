# InkPy

React for CLIs in Python - Build beautiful command-line interfaces with ReactPy.

## Introduction

InkPy is a Python port of [Ink](https://github.com/vadimdemedes/ink), a React renderer for CLIs. It allows you to build interactive terminal applications using ReactPy components and hooks.

## Installation

```bash
cd python_port
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

- 🎨 **Beautiful UI** - Build terminal UIs with flexbox layout
- ⚛️ **ReactPy Components** - Use familiar React patterns
- 🎯 **Focus Management** - Built-in keyboard navigation
- 🎨 **Styling** - Colors, borders, backgrounds, and more
- 📦 **Type Hints** - Full type support for better DX

## Examples

See the `examples/` directory for more examples:

- `hello_world.py` - Simplest example
- `counter.py` - Async state updates
- `interactive.py` - Keyboard navigation

## Documentation

See `docs/api.md` for full API reference.

## Testing

```bash
cd python_port
pytest tests/ -v
```

## Development

This is a work in progress. Contributions welcome!

## License

MIT

## Acknowledgments

InkPy is a Python port of [Ink](https://github.com/vadimdemedes/ink) by Vadim Demedes.

