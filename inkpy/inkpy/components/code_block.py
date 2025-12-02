"""
CodeBlock component module.

Provides syntax-highlighted code display for terminal applications.
"""

from typing import Optional

from reactpy import component, html

from inkpy.utils.highlight import highlight_code


@component
def CodeBlock(
    code: str = "",
    language: Optional[str] = None,
    show_line_numbers: bool = False,
    theme: str = "monokai",
    border: bool = False,
):
    """
    CodeBlock component for displaying syntax-highlighted code.

    Args:
        code: Source code to display
        language: Programming language for syntax highlighting
        show_line_numbers: Whether to show line numbers
        theme: Pygments theme name (default: 'monokai')
        border: Whether to show a border around the code

    Example:
        @component
        def App():
            code = '''
            def hello():
                print("Hello, World!")
            '''
            return CodeBlock(code=code, language="python", show_line_numbers=True)
    """
    # Highlight the code
    highlighted = highlight_code(code, language, theme)

    # Split into lines for line number handling
    lines = highlighted.split("\n")

    if show_line_numbers:
        # Calculate padding for line numbers
        num_lines = len(lines)
        padding = len(str(num_lines))

        # Add line numbers
        numbered_lines = []
        for i, line in enumerate(lines, 1):
            line_num = str(i).rjust(padding)
            numbered_lines.append(f"\x1b[90m{line_num}\x1b[0m │ {line}")

        final_code = "\n".join(numbered_lines)
    else:
        final_code = highlighted

    # Build style
    style = {
        "flexDirection": "column",
    }

    if border:
        style["borderStyle"] = "round"
        style["paddingLeft"] = 1
        style["paddingRight"] = 1

    return html.div(
        {"style": style},
        html.pre({}, final_code),
    )
