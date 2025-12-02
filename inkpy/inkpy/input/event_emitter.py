"""
EventEmitter class for distributing events.

Ports EventEmitter pattern from Ink's TypeScript implementation.
Used for distributing stdin input events to subscribers.
"""

from typing import Callable


class EventEmitter:
    """
    Simple event emitter for distributing events to listeners.

    Used primarily for stdin input distribution in the App component.
    """

    def __init__(self):
        """Initialize event emitter with empty listeners dictionary."""
        self._listeners: dict[str, list[Callable]] = {}

    def on(self, event: str, callback: Callable):
        """
        Register a listener for an event.

        Args:
            event: Event name (e.g., 'input')
            callback: Function to call when event is emitted
        """
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(callback)

    def emit(self, event: str, *args, **kwargs):
        """
        Emit an event, calling all registered listeners.

        Args:
            event: Event name
            *args: Positional arguments to pass to listeners
            **kwargs: Keyword arguments to pass to listeners
        """
        for callback in self._listeners.get(event, []):
            callback(*args, **kwargs)

    def remove_listener(self, event: str, callback: Callable):
        """
        Remove a specific listener from an event.

        Args:
            event: Event name
            callback: The callback function to remove
        """
        if event in self._listeners:
            self._listeners[event] = [cb for cb in self._listeners[event] if cb != callback]

    def removeListener(self, event: str, callback: Callable):
        """
        Alias for remove_listener (matches TypeScript naming).

        Args:
            event: Event name
            callback: The callback function to remove
        """
        self.remove_listener(event, callback)
