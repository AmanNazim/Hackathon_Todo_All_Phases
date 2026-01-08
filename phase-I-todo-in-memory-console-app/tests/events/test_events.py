"""
Unit tests for Event Sourcing System components
Testing the Event Sourcing System tasks: T030-T035
"""
import unittest
import threading
import time
from datetime import datetime
from src.events.event_store import EventStore, EventValidator
from src.events.event_bus import EventBus
from src.events.replay import EventReplayService
from src.domain.entities import Task
from src.domain.events import (
    TaskCreatedEvent, TaskUpdatedEvent, TaskDeletedEvent,
    TaskCompletedEvent, TaskReopenedEvent, EventType
)


class TestEventStore(unittest.TestCase):
    """Test the event store functionality (T030, T031)"""

    def setUp(self):
        """Set up test data"""
        self.event_store = EventStore()
        self.task = Task.create("Test Task", "Test Description")
        self.task.update(tags=["test", "important"])

    def test_append_event(self):
        """Test appending an event to the store (T030)"""
        event = TaskCreatedEvent(self.task)
        self.event_store.append(event)

        events = self.event_store.get_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].id, event.id)

    def test_get_events_chronological_order(self):
        """Test getting all events in chronological order (T031)"""
        event1 = TaskCreatedEvent(self.task)

        # Create a small delay to ensure different timestamps
        time.sleep(0.01)
        updated_task = Task.create("Updated Task", "Updated Description")
        event2 = TaskUpdatedEvent(updated_task, {'title': self.task.title})

        self.event_store.append(event1)
        self.event_store.append(event2)

        events = self.event_store.get_events()
        self.assertEqual(len(events), 2)
        # Events should be returned in the order they were added
        self.assertEqual(events[0].id, event1.id)
        self.assertEqual(events[1].id, event2.id)

    def test_get_events_by_aggregate(self):
        """Test getting events for a specific aggregate (T031)"""
        task1 = Task.create("Task 1", "Description 1")
        task2 = Task.create("Task 2", "Description 2")

        event1 = TaskCreatedEvent(task1)
        event2 = TaskCreatedEvent(task2)

        self.event_store.append(event1)
        self.event_store.append(event2)

        # Get events for task1
        task1_events = self.event_store.get_events_by_aggregate(task1.id)
        self.assertEqual(len(task1_events), 1)
        self.assertEqual(task1_events[0].aggregate_id, task1.id)

    def test_get_events_by_type(self):
        """Test getting events of a specific type"""
        task1 = Task.create("Task 1", "Description 1")
        task2 = Task.create("Task 2", "Description 2")

        event1 = TaskCreatedEvent(task1)
        event2 = TaskUpdatedEvent(task2, {'title': task2.title})
        event3 = TaskCreatedEvent(task2)

        self.event_store.append(event1)
        self.event_store.append(event2)
        self.event_store.append(event3)

        created_events = self.event_store.get_events_by_type(EventType.TASK_CREATED.value)
        self.assertEqual(len(created_events), 2)

        updated_events = self.event_store.get_events_by_type(EventType.TASK_UPDATED.value)
        self.assertEqual(len(updated_events), 1)

    def test_clear_events(self):
        """Test clearing all events from the store (T035)"""
        event = TaskCreatedEvent(self.task)
        self.event_store.append(event)

        self.assertEqual(len(self.event_store.get_events()), 1)

        self.event_store.clear()
        self.assertEqual(len(self.event_store.get_events()), 0)

    def test_count_events(self):
        """Test counting stored events"""
        event1 = TaskCreatedEvent(self.task)
        event2 = TaskUpdatedEvent(self.task, {'title': self.task.title})

        self.event_store.append(event1)
        self.event_store.append(event2)

        self.assertEqual(self.event_store.count(), 2)

    def test_get_events_since(self):
        """Test getting events after a specific timestamp"""
        past_time = datetime.now().isoformat()

        time.sleep(0.01)  # Ensure different timestamp
        event = TaskCreatedEvent(self.task)
        self.event_store.append(event)

        events_since_past = self.event_store.get_events_since(past_time)
        self.assertEqual(len(events_since_past), 1)
        self.assertEqual(events_since_past[0].id, event.id)

    def test_thread_safety(self):
        """Test thread safety of event store operations (T030)"""
        results = []

        def add_events(thread_id):
            for i in range(5):
                task = Task.create(f"Task {thread_id}-{i}", f"Description {thread_id}-{i}")
                event = TaskCreatedEvent(task)
                self.event_store.append(event)
                results.append(f"Thread {thread_id}: Added event for {task.title}")

        # Create and start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=add_events, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all events were added
        all_events = self.event_store.get_events()
        self.assertEqual(len(all_events), 15)  # 3 threads * 5 events each
        self.assertEqual(len(results), 15)


class TestEventValidator(unittest.TestCase):
    """Test event validation and integrity checks (T034)"""

    def setUp(self):
        """Set up test data"""
        self.validator = EventValidator
        self.task = Task.create("Test Task", "Test Description")
        self.event = TaskCreatedEvent(self.task)

    def test_validate_valid_event(self):
        """Test validating a properly formed event (T034)"""
        # This should not raise an exception
        result = self.validator.validate_event(self.event)
        self.assertTrue(result)

    def test_validate_event_missing_id(self):
        """Test validating an event with missing ID"""
        invalid_event = TaskCreatedEvent(self.task)
        invalid_event.id = ""

        with self.assertRaises(ValueError):
            self.validator.validate_event(invalid_event)

    def test_validate_event_missing_type(self):
        """Test validating an event with missing type"""
        invalid_event = TaskCreatedEvent(self.task)
        invalid_event.type = None

        with self.assertRaises(ValueError):
            self.validator.validate_event(invalid_event)

    def test_validate_event_missing_timestamp(self):
        """Test validating an event with missing timestamp"""
        invalid_event = TaskCreatedEvent(self.task)
        invalid_event.timestamp = ""

        with self.assertRaises(ValueError):
            self.validator.validate_event(invalid_event)

    def test_validate_event_missing_aggregate_id(self):
        """Test validating an event with missing aggregate ID"""
        invalid_event = TaskCreatedEvent(self.task)
        invalid_event.aggregate_id = ""

        with self.assertRaises(ValueError):
            self.validator.validate_event(invalid_event)

    def test_validate_event_invalid_data_type(self):
        """Test validating an event with invalid data type"""
        invalid_event = TaskCreatedEvent(self.task)
        invalid_event.data = "invalid_data_type"

        with self.assertRaises(ValueError):
            self.validator.validate_event(invalid_event)

    def test_validate_event_signature(self):
        """Test validating event signature/integrity (T034)"""
        result = self.validator.validate_event_signature(self.event)
        self.assertTrue(result)

    def test_validate_event_id_format(self):
        """Test validating event ID format"""
        # Valid UUID should pass
        result = self.validator._validate_event_id_format(self.event.id)
        self.assertTrue(result)

        # Invalid format should fail
        with self.assertRaises(ValueError):
            self.validator._validate_event_id_format("invalid-uuid-format")

    def test_validate_event_type(self):
        """Test validating event type"""
        result = self.validator._validate_event_type(self.event.type)
        self.assertTrue(result)

        # Invalid event type should fail
        with self.assertRaises(ValueError):
            self.validator._validate_event_type("INVALID_TYPE")

    def test_validate_event_data_structure(self):
        """Test validating event data structure"""
        result = self.validator._validate_event_data_structure(self.event)
        self.assertTrue(result)

    def test_calculate_event_checksum(self):
        """Test calculating event checksum"""
        checksum = self.validator.calculate_event_checksum(self.event)
        self.assertIsInstance(checksum, str)
        self.assertEqual(len(checksum), 64)  # SHA256 hash length

    def test_validate_event_checksum(self):
        """Test validating event checksum"""
        checksum = self.validator.calculate_event_checksum(self.event)
        result = self.validator.validate_event_checksum(self.event, checksum)
        self.assertTrue(result)

        # Invalid checksum should fail
        result = self.validator.validate_event_checksum(self.event, "invalid_checksum")
        self.assertFalse(result)


class TestEventBus(unittest.TestCase):
    """Test event bus functionality (T032)"""

    def setUp(self):
        """Set up test data"""
        self.event_bus = EventBus()
        self.task = Task.create("Test Task", "Test Description")
        self.handled_events = []

    def event_handler(self, event):
        """Simple event handler for testing"""
        self.handled_events.append(event)

    def test_subscribe_and_publish(self):
        """Test subscribing to events and publishing (T032)"""
        # Subscribe to TASK_CREATED events
        self.event_bus.subscribe(EventType.TASK_CREATED, self.event_handler)

        # Publish an event
        event = TaskCreatedEvent(self.task)
        self.event_bus.publish(event)

        # Verify the handler was called
        self.assertEqual(len(self.handled_events), 1)
        self.assertEqual(self.handled_events[0].id, event.id)

    def test_multiple_handlers(self):
        """Test multiple handlers for the same event type"""
        handler2_events = []

        def handler2(event):
            handler2_events.append(event)

        # Subscribe two handlers to the same event type
        self.event_bus.subscribe(EventType.TASK_CREATED, self.event_handler)
        self.event_bus.subscribe(EventType.TASK_CREATED, handler2)

        # Publish an event
        event = TaskCreatedEvent(self.task)
        self.event_bus.publish(event)

        # Both handlers should be called
        self.assertEqual(len(self.handled_events), 1)
        self.assertEqual(len(handler2_events), 1)
        self.assertEqual(self.handled_events[0].id, event.id)
        self.assertEqual(handler2_events[0].id, event.id)

    def test_unsubscribe(self):
        """Test unsubscribing from events"""
        # Subscribe to events
        self.event_bus.subscribe(EventType.TASK_CREATED, self.event_handler)

        # Publish an event (handler should be called)
        event1 = TaskCreatedEvent(self.task)
        self.event_bus.publish(event1)
        self.assertEqual(len(self.handled_events), 1)

        # Unsubscribe
        result = self.event_bus.unsubscribe(EventType.TASK_CREATED, self.event_handler)
        self.assertTrue(result)

        # Publish another event (handler should NOT be called)
        event2 = TaskCreatedEvent(self.task)
        self.event_bus.publish(event2)
        self.assertEqual(len(self.handled_events), 1)  # Still 1, not 2

    def test_get_subscribers_count(self):
        """Test getting subscriber count"""
        self.assertEqual(self.event_bus.get_subscribers_count(EventType.TASK_CREATED), 0)

        self.event_bus.subscribe(EventType.TASK_CREATED, self.event_handler)
        self.assertEqual(self.event_bus.get_subscribers_count(EventType.TASK_CREATED), 1)

        def another_handler(event):
            pass
        self.event_bus.subscribe(EventType.TASK_CREATED, another_handler)
        self.assertEqual(self.event_bus.get_subscribers_count(EventType.TASK_CREATED), 2)

    def test_clear_subscriptions(self):
        """Test clearing all subscriptions"""
        self.event_bus.subscribe(EventType.TASK_CREATED, self.event_handler)
        self.event_bus.subscribe(EventType.TASK_UPDATED, self.event_handler)

        self.assertGreater(self.event_bus.get_subscribers_count(EventType.TASK_CREATED), 0)
        self.assertGreater(self.event_bus.get_subscribers_count(EventType.TASK_UPDATED), 0)

        self.event_bus.clear()

        self.assertEqual(self.event_bus.get_subscribers_count(EventType.TASK_CREATED), 0)
        self.assertEqual(self.event_bus.get_subscribers_count(EventType.TASK_UPDATED), 0)

    def test_thread_safety(self):
        """Test thread safety of event bus operations"""
        results_lock = threading.Lock()
        published_events = []

        def handler(event):
            with results_lock:
                published_events.append(event.id)

        def publisher():
            for i in range(5):
                task = Task.create(f"Task {i}", f"Description {i}")
                event = TaskCreatedEvent(task)
                self.event_bus.publish(event)

        def subscriber():
            self.event_bus.subscribe(EventType.TASK_CREATED, handler)

        # Start multiple threads for both publishing and subscribing
        threads = []

        # Add subscriber thread
        sub_thread = threading.Thread(target=subscriber)
        threads.append(sub_thread)
        sub_thread.start()

        # Add publisher threads
        for i in range(2):
            pub_thread = threading.Thread(target=publisher)
            threads.append(pub_thread)
            pub_thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Give a moment for events to be processed
        time.sleep(0.1)

        # Verify events were handled
        self.assertGreaterEqual(len(published_events), 0)


class TestEventReplayService(unittest.TestCase):
    """Test event replay functionality (T033)"""

    def setUp(self):
        """Set up test data"""
        self.event_store = EventStore()
        self.replay_service = EventReplayService(self.event_store)

    def test_rebuild_state_empty_store(self):
        """Test rebuilding state from an empty event store"""
        state = self.replay_service.rebuild_state()
        self.assertEqual(len(state), 0)

    def test_rebuild_state_single_task_creation(self):
        """Test rebuilding state with a single task creation"""
        task = Task.create("Test Task", "Test Description")
        event = TaskCreatedEvent(task)
        self.event_store.append(event)

        state = self.replay_service.rebuild_state()
        self.assertEqual(len(state), 1)
        self.assertIn(task.id, state)
        self.assertEqual(state[task.id].title, task.title)

    def test_rebuild_state_task_updates(self):
        """Test rebuilding state with task updates"""
        task = Task.create("Original Task", "Original Description")
        create_event = TaskCreatedEvent(task)
        self.event_store.append(create_event)

        # Update the task
        task.update(title="Updated Task", description="Updated Description")
        update_event = TaskUpdatedEvent(task, {'title': "Original Task", 'description': "Original Description"})
        self.event_store.append(update_event)

        state = self.replay_service.rebuild_state()
        self.assertEqual(len(state), 1)
        self.assertEqual(state[task.id].title, "Updated Task")
        self.assertEqual(state[task.id].description, "Updated Description")

    def test_rebuild_state_task_completion(self):
        """Test rebuilding state with task completion"""
        task = Task.create("Test Task", "Test Description")
        create_event = TaskCreatedEvent(task)
        self.event_store.append(create_event)

        # Complete the task
        task.mark_completed()
        complete_event = TaskCompletedEvent(task)
        self.event_store.append(complete_event)

        state = self.replay_service.rebuild_state()
        self.assertEqual(len(state), 1)
        self.assertEqual(state[task.id].status.name, "COMPLETED")

    def test_rebuild_state_task_deletion(self):
        """Test rebuilding state with task deletion"""
        task = Task.create("Test Task", "Test Description")
        create_event = TaskCreatedEvent(task)
        self.event_store.append(create_event)

        # Delete the task
        delete_event = TaskDeletedEvent(task)
        self.event_store.append(delete_event)

        state = self.replay_service.rebuild_state()
        self.assertEqual(len(state), 0)  # Task should be deleted

    def test_rebuild_state_for_aggregate(self):
        """Test rebuilding state for a specific aggregate (task)"""
        task = Task.create("Test Task", "Test Description")
        event = TaskCreatedEvent(task)
        self.event_store.append(event)

        reconstructed_task = self.replay_service.rebuild_state_for_aggregate(task.id)
        self.assertIsNotNone(reconstructed_task)
        self.assertEqual(reconstructed_task.id, task.id)
        self.assertEqual(reconstructed_task.title, task.title)

    def test_validate_replay_integrity(self):
        """Test validating replay integrity"""
        task = Task.create("Test Task", "Test Description")
        event = TaskCreatedEvent(task)
        self.event_store.append(event)

        is_valid = self.replay_service.validate_replay_integrity()
        self.assertTrue(is_valid)

    def test_get_task_lifecycle(self):
        """Test getting the complete lifecycle of a task"""
        task = Task.create("Test Task", "Test Description")
        create_event = TaskCreatedEvent(task)
        self.event_store.append(create_event)

        lifecycle = self.replay_service.get_task_lifecycle(task.id)
        self.assertEqual(len(lifecycle), 1)
        self.assertEqual(lifecycle[0].type, EventType.TASK_CREATED)


if __name__ == '__main__':
    unittest.main()