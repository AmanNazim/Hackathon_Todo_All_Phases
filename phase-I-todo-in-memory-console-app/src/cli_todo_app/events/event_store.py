"""
Event store for CLI Todo Application
Phase I: In-Memory Python CLI Todo Application
"""
from typing import List, Dict, Any
from datetime import datetime
import threading
from ..domain.events import TaskEvent


class EventStore:
    """
    Event store for in-memory event storage (T030)
    Implements event store methods: append, get_events, get_events_by_aggregate (T031)
    """

    def __init__(self):
        self._events: List[TaskEvent] = []
        self._lock = threading.RLock()  # Thread safety

    def append(self, event: TaskEvent) -> None:
        """
        Append an event to the store
        Thread-safe operation with lock
        """
        with self._lock:
            self._events.append(event)

    def get_events(self) -> List[TaskEvent]:
        """
        Get all events in chronological order
        Thread-safe operation with lock
        """
        with self._lock:
            # Return a copy to prevent external modification
            return self._events.copy()

    def get_events_by_aggregate(self, aggregate_id: str) -> List[TaskEvent]:
        """
        Get events for a specific aggregate (task)
        Thread-safe operation with lock
        """
        with self._lock:
            return [event for event in self._events if event.aggregate_id == aggregate_id]

    def get_events_by_type(self, event_type: str) -> List[TaskEvent]:
        """
        Get events of a specific type
        Thread-safe operation with lock
        """
        with self._lock:
            return [event for event in self._events if event.type.value == event_type]

    def clear(self) -> None:
        """
        Clear all events from the store (session cleanup) (T035)
        Thread-safe operation with lock
        """
        with self._lock:
            self._events.clear()

    def cleanup_old_events(self, retention_hours: int = 24) -> int:
        """
        Clean up events older than the specified retention period
        Returns the number of events removed
        Thread-safe operation with lock
        """
        from datetime import datetime, timedelta
        import re

        # Calculate the cutoff time
        cutoff_time = datetime.now() - timedelta(hours=retention_hours)

        with self._lock:
            # Count events before cleanup
            original_count = len(self._events)

            # Filter out old events (keep only recent ones)
            # Parse ISO format timestamps to compare with cutoff
            recent_events = []
            for event in self._events:
                try:
                    # Parse the timestamp from ISO format
                    event_time = datetime.fromisoformat(event.timestamp.replace('Z', '+00:00'))
                    if event_time >= cutoff_time:
                        recent_events.append(event)
                except ValueError:
                    # If timestamp is malformed, keep the event to avoid data loss
                    recent_events.append(event)

            # Replace the events list with only recent events
            self._events = recent_events

            # Return the number of events removed
            removed_count = original_count - len(self._events)
            return removed_count

    def cleanup_for_session_end(self) -> None:
        """
        Perform cleanup operations at the end of a session
        This could include clearing all events or performing other cleanup tasks
        Thread-safe operation with lock
        """
        with self._lock:
            # For session-scoped cleanup, clear all events
            self._events.clear()

    def get_memory_usage_stats(self) -> Dict[str, Any]:
        """
        Get memory usage statistics for the event store
        Helps monitor memory consumption during sessions
        Thread-safe operation with lock
        """
        import sys
        with self._lock:
            stats = {
                'event_count': len(self._events),
                'estimated_memory_bytes': sum(sys.getsizeof(str(event)) for event in self._events),
                'memory_usage_category': self._classify_memory_usage(len(self._events))
            }
            return stats

    def _classify_memory_usage(self, event_count: int) -> str:
        """
        Classify memory usage based on event count
        """
        if event_count < 100:
            return 'low'
        elif event_count < 1000:
            return 'moderate'
        elif event_count < 10000:
            return 'high'
        else:
            return 'critical'

    def count(self) -> int:
        """
        Get the count of stored events
        Thread-safe operation with lock
        """
        with self._lock:
            return len(self._events)

    def get_events_since(self, timestamp: str) -> List[TaskEvent]:
        """
        Get events that occurred after a specific timestamp
        Thread-safe operation with lock
        """
        with self._lock:
            return [event for event in self._events if event.timestamp >= timestamp]


class EventValidator:
    """
    Event validation and integrity checks (T034)
    """

    @staticmethod
    def validate_event(event: TaskEvent) -> bool:
        """
        Validate an event for integrity and required fields
        """
        if not event.id:
            raise ValueError("Event must have an ID")
        if not event.type:
            raise ValueError("Event must have a type")
        if not event.timestamp:
            raise ValueError("Event must have a timestamp")
        if not event.aggregate_id:
            raise ValueError("Event must have an aggregate ID")
        if not isinstance(event.data, dict):
            raise ValueError("Event data must be a dictionary")

        # Additional checks
        EventValidator._validate_event_id_format(event.id)
        EventValidator._validate_event_type(event.type)
        EventValidator._validate_timestamp_format(event.timestamp)

        return True

    @staticmethod
    def validate_event_signature(event: TaskEvent) -> bool:
        """
        Validate the signature/integrity of an event
        """
        try:
            # Basic validation checks
            EventValidator.validate_event(event)

            # Additional integrity checks
            return EventValidator._check_event_integrity(event)
        except Exception:
            return False

    @staticmethod
    def _validate_event_id_format(event_id: str) -> bool:
        """
        Validate the format of an event ID (should be UUID)
        """
        import uuid
        try:
            uuid.UUID(event_id)
            return True
        except ValueError:
            raise ValueError(f"Invalid event ID format: {event_id}")

    @staticmethod
    def _validate_event_type(event_type) -> bool:
        """
        Validate that the event type is one of the allowed types
        """
        from ..domain.events import EventType
        if event_type not in EventType.__members__.values():
            raise ValueError(f"Invalid event type: {event_type}")
        return True

    @staticmethod
    def _validate_timestamp_format(timestamp: str) -> bool:
        """
        Validate that the timestamp is in ISO format
        """
        from datetime import datetime
        try:
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return True
        except ValueError:
            raise ValueError(f"Invalid timestamp format: {timestamp}")

    @staticmethod
    def _check_event_integrity(event: TaskEvent) -> bool:
        """
        Perform additional integrity checks on the event
        """
        # Check that aggregate_id matches the expected pattern (UUID)
        import uuid
        try:
            uuid.UUID(event.aggregate_id)
        except ValueError:
            raise ValueError(f"Invalid aggregate ID format: {event.aggregate_id}")

        # Validate that the event type matches the expected data structure
        EventValidator._validate_event_data_structure(event)

        # Additional integrity checks could be implemented here
        # For example: checksum validation, digital signature verification, etc.
        return True

    @staticmethod
    def _validate_event_data_structure(event: TaskEvent) -> bool:
        """
        Validate that the event data structure is appropriate for the event type
        """
        from ..domain.events import EventType

        if event.type == EventType.TASK_CREATED:
            required_fields = ['title', 'description', 'created_at', 'status', 'tags']
        elif event.type == EventType.TASK_UPDATED:
            required_fields = ['new_values', 'old_values']
        elif event.type == EventType.TASK_DELETED:
            required_fields = ['title', 'description', 'created_at', 'updated_at', 'status', 'tags']
        elif event.type == EventType.TASK_COMPLETED:
            required_fields = ['previous_status', 'updated_at']
        elif event.type == EventType.TASK_REOPENED:
            required_fields = ['previous_status', 'updated_at']
        else:
            # For unknown event types, just check that data is a dictionary
            return True

        for field in required_fields:
            if field not in event.data:
                raise ValueError(f"Missing required field '{field}' in {event.type.value} event data")

        return True

    @staticmethod
    def validate_event_consistency(event: TaskEvent, existing_events: List[TaskEvent]) -> bool:
        """
        Validate that the event is consistent with existing events
        For example, check that a TASK_COMPLETED event is not applied to an already completed task
        """
        from ..domain.events import EventType

        if event.type in [EventType.TASK_COMPLETED, EventType.TASK_REOPENED]:
            # Find the most recent state of this task
            task_events = [e for e in existing_events if e.aggregate_id == event.aggregate_id]

            if not task_events:
                # If there are no previous events, this is likely invalid
                # (except for TASK_CREATED which should be first)
                if event.type != EventType.TASK_CREATED:
                    raise ValueError(f"No previous events for task {event.aggregate_id}, cannot apply {event.type.value}")
                return True

            # Sort events by timestamp to find the current state
            task_events.sort(key=lambda x: x.timestamp)
            current_state = None

            for task_event in task_events:
                if task_event.type == EventType.TASK_CREATED:
                    current_state = 'PENDING'
                elif task_event.type == EventType.TASK_COMPLETED:
                    current_state = 'COMPLETED'
                elif task_event.type == EventType.TASK_REOPENED:
                    current_state = 'PENDING'
                elif task_event.type == EventType.TASK_DELETED:
                    current_state = 'DELETED'

            # Check consistency
            if event.type == EventType.TASK_COMPLETED and current_state == 'COMPLETED':
                raise ValueError(f"Cannot complete task {event.aggregate_id}, it is already completed")
            elif event.type == EventType.TASK_REOPENED and current_state == 'PENDING':
                raise ValueError(f"Cannot reopen task {event.aggregate_id}, it is already pending")
            elif event.type == EventType.TASK_DELETED and current_state == 'DELETED':
                raise ValueError(f"Cannot delete task {event.aggregate_id}, it is already deleted")

        return True

    @staticmethod
    def calculate_event_checksum(event: TaskEvent) -> str:
        """
        Calculate a checksum for the event to verify integrity
        """
        import hashlib
        import json

        # Create a string representation of the event
        event_str = f"{event.id}|{event.type.value}|{event.timestamp}|{event.aggregate_id}|{json.dumps(event.data, sort_keys=True)}"

        # Calculate SHA256 hash
        return hashlib.sha256(event_str.encode()).hexdigest()

    @staticmethod
    def validate_event_checksum(event: TaskEvent, expected_checksum: str) -> bool:
        """
        Validate the event checksum against an expected value
        """
        calculated_checksum = EventValidator.calculate_event_checksum(event)
        return calculated_checksum == expected_checksum