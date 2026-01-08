"""
Event bus for CLI Todo Application
Phase I: In-Memory Python CLI Todo Application
"""
from typing import Dict, List, Callable, Any, Type
from threading import RLock
from src.domain.events import TaskEvent, EventType


class EventBus:
    """
    Event bus for publishing events within the system (T032)
    Implements publish-subscribe pattern with thread safety
    """

    def __init__(self):
        self._handlers: Dict[EventType, List[Callable[[TaskEvent], None]]] = {}
        self._lock = RLock()  # Thread safety

    def subscribe(self, event_type: EventType, handler: Callable[[TaskEvent], None]) -> None:
        """
        Subscribe a handler to a specific event type
        Thread-safe operation with lock
        """
        with self._lock:
            if event_type not in self._handlers:
                self._handlers[event_type] = []

            if handler not in self._handlers[event_type]:
                self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type: EventType, handler: Callable[[TaskEvent], None]) -> bool:
        """
        Unsubscribe a handler from a specific event type
        Thread-safe operation with lock
        """
        with self._lock:
            if event_type in self._handlers and handler in self._handlers[event_type]:
                self._handlers[event_type].remove(handler)

                # Clean up empty lists
                if not self._handlers[event_type]:
                    del self._handlers[event_type]
                return True
            return False

    def publish(self, event: TaskEvent) -> None:
        """
        Publish an event to all subscribed handlers
        Thread-safe operation with lock
        """
        with self._lock:
            if event.type in self._handlers:
                # Create a copy of handlers to avoid issues if handlers modify the list
                handlers = self._handlers[event.type].copy()

                # Notify all handlers of this event type
                for handler in handlers:
                    try:
                        handler(event)
                    except Exception as e:
                        # Log the error but continue with other handlers
                        print(f"Error in event handler: {e}")

    def get_subscribers_count(self, event_type: EventType) -> int:
        """
        Get the number of subscribers for a specific event type
        Thread-safe operation with lock
        """
        with self._lock:
            return len(self._handlers.get(event_type, []))

    def clear(self) -> None:
        """
        Clear all subscriptions (session cleanup)
        Thread-safe operation with lock
        """
        with self._lock:
            self._handlers.clear()


class EventPublisher:
    """
    Helper class for publishing events with automatic event bus integration
    """

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus

    def publish_event(self, event: TaskEvent) -> None:
        """Publish an event through the event bus"""
        self.event_bus.publish(event)


class EventSubscriber:
    """
    Helper class for subscribing to events with automatic event bus integration
    """

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus

    def subscribe_to_event(self, event_type: EventType, handler: Callable[[TaskEvent], None]) -> None:
        """Subscribe to a specific event type"""
        self.event_bus.subscribe(event_type, handler)

    def unsubscribe_from_event(self, event_type: EventType, handler: Callable[[TaskEvent], None]) -> bool:
        """Unsubscribe from a specific event type"""
        return self.event_bus.unsubscribe(event_type, handler)