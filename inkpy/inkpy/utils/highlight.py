"""
Syntax highlighting utilities using Pygments.

Provides terminal-compatible syntax highlighting for code blocks.
"""

from typing import Optional

from pygments import highlight
from pygments.formatters import Terminal256Formatter
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.util import ClassNotFound


def get_lexer_for_language(language: str):
    """
    Get a Pygments lexer for the specified language.

    Args:
        language: Language name (e.g., 'python', 'javascript', 'rust')

    Returns:
        Pygments lexer or None if not found
    """
    try:
        return get_lexer_by_name(language)
    except ClassNotFound:
        return None


def highlight_code(
    code: str,
    language: Optional[str] = None,
    theme: str = "monokai",
) -> str:
    """
    Highlight code with syntax coloring for terminal output.

    Args:
        code: Source code to highlight
        language: Programming language (auto-detected if None)
        theme: Color theme name (default: 'monokai')

    Returns:
        Code with ANSI color codes for terminal display

    Example:
        >>> highlighted = highlight_code('print("hello")', 'python')
        >>> print(highlighted)
    """
    # Get lexer
    lexer = None
    if language:
        lexer = get_lexer_for_language(language)

    if lexer is None:
        # Try to guess the language
        try:
            lexer = guess_lexer(code)
        except ClassNotFound:
            # Return plain code if we can't identify the language
            return code

    # Create formatter for terminal
    formatter = Terminal256Formatter(style=theme)

    # Highlight and return
    try:
        result = highlight(code, lexer, formatter)
        # Strip trailing newline that Pygments adds
        return result.rstrip("\n")
    except Exception:
        # Return plain code on any error
        return code
