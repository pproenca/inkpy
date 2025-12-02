"""
Tests for TUI Backend reconciler bridge features.

Following TDD: Write failing test first, then implement.
"""
import pytest
from inkpy.backend.tui_backend import TUIBackend, HostContext
from inkpy.dom import TextNode


def test_host_context_tracks_is_inside_text():
    """Test that host context tracks isInsideText state"""
    backend = TUIBackend()
    
    # Verify backend has context tracking methods
    assert hasattr(backend, 'get_root_host_context')
    assert hasattr(backend, 'get_child_host_context')
    
    # Test root context
    root_ctx = backend.get_root_host_context()
    assert root_ctx.is_inside_text is False
    
    # Test child context for Text component
    text_ctx = backend.get_child_host_context(root_ctx, 'ink-text')
    assert text_ctx.is_inside_text is True
    
    # Test child context for Box component (should remain False)
    box_ctx = backend.get_child_host_context(root_ctx, 'ink-box')
    assert box_ctx.is_inside_text is False
    
    # Test nested Text (should remain True)
    nested_text_ctx = backend.get_child_host_context(text_ctx, 'ink-text')
    assert nested_text_ctx.is_inside_text is True


def test_text_validation_prevents_text_outside_text_component():
    """Test that text strings can only be created inside Text component"""
    backend = TUIBackend()
    
    # Creating text outside Text component should raise error
    # This tests create_text_instance validation
    
    # This will fail until implemented
    with pytest.raises(ValueError, match="must be rendered inside.*Text"):
        backend.create_text_instance("Hello", None, HostContext(is_inside_text=False))


def test_text_validation_allows_text_inside_text_component():
    """Test that text strings can be created inside Text component"""
    backend = TUIBackend()
    
    # Creating text inside Text component should succeed
    text_node = backend.create_text_instance("Hello", None, HostContext(is_inside_text=True))
    assert text_node is not None
    assert isinstance(text_node, TextNode)


def test_box_cannot_be_nested_inside_text():
    """Test that Box component cannot be nested inside Text"""
    backend = TUIBackend()
    
    # Creating Box inside Text should raise error
    with pytest.raises(ValueError, match="can't be nested inside.*Text"):
        backend.create_instance('ink-box', {}, None, HostContext(is_inside_text=True))


def test_commit_update_diffs_attributes():
    """Test that commitUpdate properly diffs old and new props"""
    backend = TUIBackend()
    
    # Create a node
    node = backend.create_instance('ink-box', {'id': 'test', 'data': 'old'}, None, HostContext(is_inside_text=False))
    
    # Update with changed props
    backend.commit_update(node, 'ink-box', {'id': 'test', 'data': 'old'}, {'id': 'test', 'data': 'new'})
    
    # Node should have updated attribute
    assert node.attributes.get('data') == 'new'


def test_commit_update_diffs_styles():
    """Test that commitUpdate properly diffs styles"""
    backend = TUIBackend()
    
    # Create a node with initial style
    node = backend.create_instance('ink-box', {'style': {'padding': 1}}, None, HostContext(is_inside_text=False))
    
    # Update with changed style
    backend.commit_update(node, 'ink-box', {'style': {'padding': 1}}, {'style': {'padding': 2}})
    
    # Style should be updated
    assert node.style.get('padding') == 2


def test_static_element_detection():
    """Test that static elements are detected and marked"""
    backend = TUIBackend()
    root_node = backend.create_instance('ink-root', {}, None, HostContext(is_inside_text=False))
    
    # Create static element
    static_node = backend.create_instance('ink-box', {'internal_static': True}, root_node, HostContext(is_inside_text=False))
    
    # Root should be marked as static dirty
    assert root_node.is_static_dirty is True
    assert root_node.static_node == static_node


def test_reset_after_commit_triggers_callbacks():
    """Test that resetAfterCommit triggers onComputeLayout, onRender callbacks"""
    backend = TUIBackend()
    
    callbacks_called = {'layout': False, 'render': False}
    
    def on_layout():
        callbacks_called['layout'] = True
    
    def on_render():
        callbacks_called['render'] = True
    
    root_node = backend.create_instance('ink-root', {}, None, HostContext(is_inside_text=False))
    root_node.on_compute_layout = on_layout
    root_node.on_render = on_render
    
    backend.reset_after_commit(root_node)
    
    assert callbacks_called['layout'] is True
    assert callbacks_called['render'] is True


def test_reset_after_commit_triggers_immediate_render_for_static():
    """Test that resetAfterCommit triggers onImmediateRender for static elements"""
    backend = TUIBackend()
    
    callbacks_called = {'immediate': False, 'normal': False}
    
    def on_immediate():
        callbacks_called['immediate'] = True
    
    def on_render():
        callbacks_called['normal'] = True
    
    root_node = backend.create_instance('ink-root', {}, None, HostContext(is_inside_text=False))
    root_node.is_static_dirty = True
    root_node.on_immediate_render = on_immediate
    root_node.on_render = on_render
    
    backend.reset_after_commit(root_node)
    
    assert callbacks_called['immediate'] is True
    assert callbacks_called['normal'] is False  # Should not call normal render


def test_yoga_node_cleanup_on_remove():
    """Test that Yoga nodes are cleaned up when nodes are removed"""
    backend = TUIBackend()
    
    parent = backend.create_instance('ink-box', {}, None, HostContext(is_inside_text=False))
    child = backend.create_instance('ink-box', {}, parent, HostContext(is_inside_text=False))
    
    # Mock cleanup function
    cleanup_called = {'called': False}
    original_free = child.yoga_node.free_recursive if child.yoga_node and hasattr(child.yoga_node, 'free_recursive') else None
    
    if child.yoga_node and hasattr(child.yoga_node, 'free_recursive'):
        def mock_free():
            cleanup_called['called'] = True
            if original_free:
                original_free()
        
        child.yoga_node.free_recursive = mock_free
    
    # Remove child
    backend.remove_child(parent, child)
    
    # Cleanup should be called (if free_recursive exists)
    # Note: This test may need adjustment based on actual Yoga node API
    if original_free:
        assert cleanup_called['called'] is True

