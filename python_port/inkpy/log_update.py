"""
Log Update - Terminal output management with cursor control and incremental rendering.

Ported from: src/log-update.ts
"""
from typing import TextIO, List

# ANSI escape sequences
HIDE_CURSOR = "\x1b[?25l"
SHOW_CURSOR = "\x1b[?25h"
ERASE_LINE = "\x1b[2K"
CURSOR_NEXT_LINE = "\x1b[1E"


def erase_lines(count: int) -> str:
    """
    Generate ANSI sequence to erase N lines.
    
    Equivalent to ansiEscapes.eraseLines(count) from ansi-escapes package.
    """
    if count <= 0:
        return ""
    
    # Move up N lines, erase each line, then return to start
    result = ""
    for _ in range(count):
        result += ERASE_LINE  # Erase current line
        if _ < count - 1:  # Don't move up after last line
            result += "\x1b[1A"  # Move cursor up 1 line
    
    result += "\r"  # Return to start of line
    return result


def cursor_up(count: int) -> str:
    """Move cursor up N lines"""
    if count <= 0:
        return ""
    return f"\x1b[{count}A"


class LogUpdate:
    """Manages terminal output with support for re-rendering"""
    
    def __init__(
        self,
        stream: TextIO,
        show_cursor: bool = True,
        incremental: bool = False
    ):
        self.stream = stream
        self.show_cursor = show_cursor
        self.incremental = incremental
        self._previous_line_count = 0
        self._previous_output = ""
        self._previous_lines: List[str] = []
        self._has_hidden_cursor = False
    
    def __call__(self, text: str) -> None:
        """Write output, erasing previous content"""
        if self.incremental:
            self._render_incremental(text)
        else:
            self._render_standard(text)
    
    def _render_standard(self, text: str) -> None:
        """Standard rendering mode - erase all previous lines"""
        if not self.show_cursor and not self._has_hidden_cursor:
            self.stream.write(HIDE_CURSOR)
            self._has_hidden_cursor = True
        
        output = text + "\n"
        if output == self._previous_output:
            return
        
        self._previous_output = output
        self.stream.write(erase_lines(self._previous_line_count) + output)
        self._previous_line_count = len(output.split("\n")) - 1  # Subtract 1 for trailing newline
        self.stream.flush()
    
    def _render_incremental(self, text: str) -> None:
        """Incremental rendering mode - only update changed lines"""
        if not self.show_cursor and not self._has_hidden_cursor:
            self.stream.write(HIDE_CURSOR)
            self._has_hidden_cursor = True
        
        output = text + "\n"
        if output == self._previous_output:
            return
        
        previous_count = len(self._previous_lines)
        next_lines = output.split("\n")
        next_count = len(next_lines)
        visible_count = next_count - 1  # Exclude trailing empty line
        
        if output == "\n" or len(self._previous_output) == 0:
            self.stream.write(erase_lines(previous_count) + output)
            self._previous_output = output
            self._previous_lines = next_lines
            self.stream.flush()
            return
        
        buffer = []
        
        # Handle line count changes
        if next_count < previous_count:
            # Clear extra lines
            buffer.append(erase_lines(previous_count - next_count + 1))
            buffer.append(cursor_up(visible_count))
        else:
            buffer.append(cursor_up(previous_count - 1))
        
        # Only write changed lines
        for i in range(visible_count):
            if i < len(self._previous_lines) and next_lines[i] == self._previous_lines[i]:
                # Skip unchanged lines
                buffer.append(CURSOR_NEXT_LINE)
                continue
            # Erase and write changed line
            buffer.append(ERASE_LINE + next_lines[i] + "\n")
        
        self.stream.write("".join(buffer))
        self._previous_output = output
        self._previous_lines = next_lines
        self.stream.flush()
    
    def clear(self) -> None:
        """Erase all output"""
        self.stream.write(erase_lines(self._previous_line_count))
        self._previous_output = ""
        self._previous_line_count = 0
        self._previous_lines = []
        self.stream.flush()
    
    def done(self) -> None:
        """Cleanup - reset state and show cursor"""
        self._previous_output = ""
        self._previous_line_count = 0
        self._previous_lines = []
        
        if not self.show_cursor and self._has_hidden_cursor:
            self.stream.write(SHOW_CURSOR)
            self._has_hidden_cursor = False
            self.stream.flush()
    
    def sync(self, text: str) -> None:
        """Update internal state without writing to stream"""
        output = text + "\n"
        self._previous_output = output
        self._previous_line_count = len(output.split("\n")) - 1
        self._previous_lines = output.split("\n")


def create_log_update(
    stream: TextIO,
    show_cursor: bool = True,
    incremental: bool = False
) -> LogUpdate:
    """Factory function to create LogUpdate instance"""
    return LogUpdate(stream, show_cursor, incremental)

