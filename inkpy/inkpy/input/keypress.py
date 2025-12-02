"""
Keypress parser module.

Ports parse-keypress functionality from Ink.
Parses ANSI escape sequences and converts them to structured key information.
"""
import re
from typing import Union, Optional
from dataclasses import dataclass

# Key name mappings
KEY_NAMES = {
    # xterm/gnome ESC O letter
    'OP': 'f1',
    'OQ': 'f2',
    'OR': 'f3',
    'OS': 'f4',
    # xterm/rxvt ESC [ number ~
    '[11~': 'f1',
    '[12~': 'f2',
    '[13~': 'f3',
    '[14~': 'f4',
    # from Cygwin and used in libuv
    '[[A': 'f1',
    '[[B': 'f2',
    '[[C': 'f3',
    '[[D': 'f4',
    '[[E': 'f5',
    # common
    '[15~': 'f5',
    '[17~': 'f6',
    '[18~': 'f7',
    '[19~': 'f8',
    '[20~': 'f9',
    '[21~': 'f10',
    '[23~': 'f11',
    '[24~': 'f12',
    # xterm ESC [ letter
    '[A': 'up',
    '[B': 'down',
    '[C': 'right',
    '[D': 'left',
    '[E': 'clear',
    '[F': 'end',
    '[H': 'home',
    # xterm/gnome ESC O letter
    'OA': 'up',
    'OB': 'down',
    'OC': 'right',
    'OD': 'left',
    'OE': 'clear',
    'OF': 'end',
    'OH': 'home',
    # xterm/rxvt ESC [ number ~
    '[1~': 'home',
    '[2~': 'insert',
    '[3~': 'delete',
    '[4~': 'end',
    '[5~': 'pageup',
    '[6~': 'pagedown',
    # putty
    '[[5~': 'pageup',
    '[[6~': 'pagedown',
    # rxvt
    '[7~': 'home',
    '[8~': 'end',
    # rxvt keys with modifiers
    '[a': 'up',
    '[b': 'down',
    '[c': 'right',
    '[d': 'left',
    '[e': 'clear',
    '[2$': 'insert',
    '[3$': 'delete',
    '[5$': 'pageup',
    '[6$': 'pagedown',
    '[7$': 'home',
    '[8$': 'end',
    'Oa': 'up',
    'Ob': 'down',
    'Oc': 'right',
    'Od': 'left',
    'Oe': 'clear',
    '[2^': 'insert',
    '[3^': 'delete',
    '[5^': 'pageup',
    '[6^': 'pagedown',
    '[7^': 'home',
    '[8^': 'end',
    # misc.
    '[Z': 'tab',
}

NON_ALPHANUMERIC_KEYS = list(KEY_NAMES.values()) + ['backspace']

SHIFT_KEYS = ['[a', '[b', '[c', '[d', '[e', '[2$', '[3$', '[5$', '[6$', '[7$', '[8$', '[Z']
CTRL_KEYS = ['Oa', 'Ob', 'Oc', 'Od', 'Oe', '[2^', '[3^', '[5^', '[6^', '[7^', '[8^']

META_KEY_CODE_RE = re.compile(r'^(?:\x1b)([a-zA-Z0-9])$')
FN_KEY_RE = re.compile(r'^(?:\x1b+)(O|N|\[|\[\[)(?:(\d+)(?:;(\d+))?([~^$])|(?:1;)?(\d+)?([a-zA-Z]))')


@dataclass
class Key:
    """Parsed key information."""
    name: str = ''
    ctrl: bool = False
    meta: bool = False
    shift: bool = False
    option: bool = False
    sequence: str = ''
    raw: Optional[str] = None
    code: Optional[str] = None
    
    # Convenience properties matching Ink's Key type
    @property
    def upArrow(self) -> bool:
        return self.name == 'up'
    
    @property
    def downArrow(self) -> bool:
        return self.name == 'down'
    
    @property
    def leftArrow(self) -> bool:
        return self.name == 'left'
    
    @property
    def rightArrow(self) -> bool:
        return self.name == 'right'
    
    @property
    def pageUp(self) -> bool:
        return self.name == 'pageup'
    
    @property
    def pageDown(self) -> bool:
        return self.name == 'pagedown'
    
    @property
    def return_(self) -> bool:
        # Both 'return' (\r) and 'enter' (\n) should be True
        return self.name in ('return', 'enter')
    
    @property
    def escape(self) -> bool:
        return self.name == 'escape'
    
    @property
    def tab(self) -> bool:
        return self.name == 'tab'
    
    @property
    def backspace(self) -> bool:
        return self.name == 'backspace'
    
    @property
    def delete(self) -> bool:
        return self.name == 'delete'
    
    # === Snake_case aliases (Pythonic API) ===
    
    @property
    def up_arrow(self) -> bool:
        """Snake_case alias for upArrow"""
        return self.upArrow
    
    @property
    def down_arrow(self) -> bool:
        """Snake_case alias for downArrow"""
        return self.downArrow
    
    @property
    def left_arrow(self) -> bool:
        """Snake_case alias for leftArrow"""
        return self.leftArrow
    
    @property
    def right_arrow(self) -> bool:
        """Snake_case alias for rightArrow"""
        return self.rightArrow
    
    @property
    def page_up(self) -> bool:
        """Snake_case alias for pageUp"""
        return self.pageUp
    
    @property
    def page_down(self) -> bool:
        """Snake_case alias for pageDown"""
        return self.pageDown
    
    @property
    def return_key(self) -> bool:
        """Alias for return_ (more readable)"""
        return self.return_


def parse_keypress(s: Union[bytes, str] = '') -> Key:
    """
    Parse a keypress sequence into structured key information.
    
    Args:
        s: Keypress sequence (bytes or string)
    
    Returns:
        Key object with parsed information
    """
    # Convert bytes to string
    if isinstance(s, bytes):
        if len(s) > 0 and s[0] > 127 and len(s) == 1:
            s = '\x1b' + chr(s[0] - 128)
        else:
            s = s.decode('utf-8', errors='replace')
    elif not isinstance(s, str):
        s = str(s)
    elif not s:
        s = ''
    
    key = Key(sequence=s, raw=s)
    
    if s == '\r':
        key.raw = None
        key.name = 'return'
    elif s == '\n':
        key.name = 'enter'
    elif s == '\t':
        key.name = 'tab'
    elif s == '\b' or s == '\x1b\b':
        key.name = 'backspace'
        key.meta = s[0] == '\x1b' if s else False
    elif s == '\x7f' or s == '\x1b\x7f':
        key.name = 'delete'
        key.meta = s[0] == '\x1b' if s else False
    elif s == '\x1b' or s == '\x1b\x1b':
        key.name = 'escape'
        key.meta = len(s) == 2
    elif s == ' ' or s == '\x1b ':
        key.name = 'space'
        key.meta = len(s) == 2
    elif len(s) == 1 and s <= '\x1a':
        # ctrl+letter
        key.name = chr(ord(s) + ord('a') - 1)
        key.ctrl = True
    elif len(s) == 1 and '0' <= s <= '9':
        key.name = 'number'
    elif len(s) == 1 and 'a' <= s <= 'z':
        key.name = s
    elif len(s) == 1 and 'A' <= s <= 'Z':
        key.name = s.lower()
        key.shift = True
    else:
        # Try meta key pattern
        meta_match = META_KEY_CODE_RE.match(s)
        if meta_match:
            key.meta = True
            key.shift = bool(re.match(r'^[A-Z]$', meta_match.group(1)))
        else:
            # Try function key pattern
            fn_match = FN_KEY_RE.match(s)
            if fn_match:
                segs = list(s)
                if len(segs) >= 2 and segs[0] == '\u001b' and segs[1] == '\u001b':
                    key.option = True
                
                # Reassemble key code
                code_parts = [fn_match.group(1), fn_match.group(2), fn_match.group(4), fn_match.group(6)]
                code = ''.join(p for p in code_parts if p)
                
                # Parse modifier
                modifier = int(fn_match.group(3) or fn_match.group(5) or '1') - 1
                key.ctrl = bool(modifier & 4)
                key.meta = bool(modifier & 10)
                key.shift = bool(modifier & 1)
                key.code = code
                
                # Get key name
                key.name = KEY_NAMES.get(code, '')
                
                # Override shift/ctrl based on code patterns
                if code in SHIFT_KEYS:
                    key.shift = True
                if code in CTRL_KEYS:
                    key.ctrl = True
    
    return key

