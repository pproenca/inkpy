"""
Tests for EventEmitter class.

Following TDD: Write failing test first, then implement.
"""
from inkpy.input.event_emitter import EventEmitter


def test_event_emitter_on_and_emit():
    """Test that EventEmitter can register listeners and emit events"""
    emitter = EventEmitter()
    captured_events = []
    
    def handler(data):
        captured_events.append(data)
    
    emitter.on('input', handler)
    emitter.emit('input', 'test_data')
    
    assert len(captured_events) == 1
    assert captured_events[0] == 'test_data'


def test_event_emitter_multiple_listeners():
    """Test that multiple listeners can be registered for same event"""
    emitter = EventEmitter()
    captured_1 = []
    captured_2 = []
    
    def handler1(data):
        captured_1.append(data)
    
    def handler2(data):
        captured_2.append(data)
    
    emitter.on('input', handler1)
    emitter.on('input', handler2)
    emitter.emit('input', 'test')
    
    assert len(captured_1) == 1
    assert len(captured_2) == 1
    assert captured_1[0] == 'test'
    assert captured_2[0] == 'test'


def test_event_emitter_remove_listener():
    """Test that listeners can be removed"""
    emitter = EventEmitter()
    captured = []
    
    def handler(data):
        captured.append(data)
    
    emitter.on('input', handler)
    emitter.emit('input', 'test1')
    assert len(captured) == 1
    
    emitter.remove_listener('input', handler)
    emitter.emit('input', 'test2')
    assert len(captured) == 1  # Should not increase


def test_event_emitter_no_listeners():
    """Test that emitting with no listeners doesn't crash"""
    emitter = EventEmitter()
    # Should not raise
    emitter.emit('input', 'test')


def test_event_emitter_different_events():
    """Test that different event types are isolated"""
    emitter = EventEmitter()
    input_captured = []
    output_captured = []
    
    def input_handler(data):
        input_captured.append(data)
    
    def output_handler(data):
        output_captured.append(data)
    
    emitter.on('input', input_handler)
    emitter.on('output', output_handler)
    
    emitter.emit('input', 'input_data')
    emitter.emit('output', 'output_data')
    
    assert len(input_captured) == 1
    assert len(output_captured) == 1
    assert input_captured[0] == 'input_data'
    assert output_captured[0] == 'output_data'

