#!/usr/bin/env python3
"""
Hello World - Simplest InkPy example
"""
from reactpy import component
from inkpy import render
from inkpy.components import Text

@component
def App():
    return Text("Hello, World!", color="green", bold=True)

if __name__ == "__main__":
    render(App())

