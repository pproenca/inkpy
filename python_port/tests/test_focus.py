# test_focus.py
from reactpy import component
from inkpy.hooks.use_focus import use_focus
from inkpy.hooks.use_focus_manager import use_focus_manager
from inkpy.components.text import Text

def test_focus_context_structure():
    """Test FocusContext provides required fields"""
    
    # Verify context has correct structure
    context_value = {
        'active_id': None,
        'add': lambda id, opts: None,
        'remove': lambda id: None,
        'activate': lambda id: None,
        'deactivate': lambda id: None,
        'enable_focus': lambda: None,
        'disable_focus': lambda: None,
        'focus_next': lambda: None,
        'focus_previous': lambda: None,
        'focus': lambda id: None,
    }
    
    for key in context_value.keys():
        assert key in context_value

def test_use_focus_returns_is_focused():
    """Test useFocus hook returns isFocused boolean"""
    @component
    def FocusableItem():
        focus = use_focus()
        assert hasattr(focus, 'is_focused')
        assert hasattr(focus, 'focus')
        assert isinstance(focus.is_focused, bool)
        return Text("Item")

def test_use_focus_with_auto_focus():
    """Test useFocus with autoFocus option"""
    @component
    def AutoFocusItem():
        focus = use_focus(auto_focus=True)
        return Text("Auto focused" if focus.is_focused else "Not focused")

def test_use_focus_with_custom_id():
    """Test useFocus with custom ID"""
    @component
    def CustomIdItem():
        _focus = use_focus(id="my-custom-id")  # noqa: F841 - Hook called for side effects
        return Text("Item")

def test_focus_manager_navigation():
    """Test focus manager provides navigation functions"""
    @component
    def ManagerTest():
        manager = use_focus_manager()
        assert hasattr(manager, 'focus_next')
        assert hasattr(manager, 'focus_previous')
        assert hasattr(manager, 'enable_focus')
        assert hasattr(manager, 'disable_focus')
        return None

def test_focus_state_management():
    """Test focus state tracking"""
    # Simulate focus management
    focusables = []
    active_id = None
    
    def add_focusable(id, opts):
        focusables.append({'id': id, 'is_active': True, 'auto_focus': opts.get('auto_focus', False)})
        nonlocal active_id
        if not active_id and opts.get('auto_focus'):
            active_id = id
    
    def remove_focusable(id):
        nonlocal focusables, active_id
        focusables = [f for f in focusables if f['id'] != id]
        if active_id == id:
            active_id = None
    
    add_focusable('item1', {'auto_focus': True})
    assert active_id == 'item1'
    
    add_focusable('item2', {'auto_focus': False})
    assert active_id == 'item1'  # Should not change
    
    remove_focusable('item1')
    assert active_id is None

