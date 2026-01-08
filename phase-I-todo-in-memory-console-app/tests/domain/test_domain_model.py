"""
Unit tests for CLI Todo Application Domain Model
Testing the Domain Model tasks: T010-T017
"""
import unittest
from datetime import datetime
from src.domain.entities import Task
from src.domain.status import TaskStatus
from src.domain.events import (
    TaskCreatedEvent, TaskUpdatedEvent, TaskDeletedEvent,
    TaskCompletedEvent, TaskReopenedEvent, EventType
)
from src.domain.validation import DomainValidator


class TestTaskEntity(unittest.TestCase):
    """Test the Task entity implementation (T010)"""

    def test_task_creation_with_required_fields(self):
        """Test Task entity with required fields (T010)"""
        task = Task.create("Test task")

        self.assertIsNotNone(task.id)
        self.assertEqual(task.title, "Test task")
        self.assertIsNone(task.description)
        self.assertIsNotNone(task.created_at)
        self.assertIsNotNone(task.updated_at)
        self.assertEqual(task.status, TaskStatus.PENDING)
        self.assertEqual(task.tags, [])

    def test_task_creation_with_optional_fields(self):
        """Test Task entity with optional fields (T010)"""
        task = Task.create(
            title="Test task",
            description="Test description",
            tags=["work", "important"]
        )

        self.assertEqual(task.title, "Test task")
        self.assertEqual(task.description, "Test description")
        self.assertEqual(task.tags, ["work", "important"])

    def test_task_validation_rules(self):
        """Test domain validation rules (T017)"""
        # Test title validation
        with self.assertRaises(ValueError):
            Task.create("")  # Empty title

        with self.assertRaises(ValueError):
            Task.create("a" * 257)  # Title too long

        # Test description validation
        with self.assertRaises(ValueError):
            Task.create("Valid title", "a" * 1025)  # Description too long

        # Test tags validation
        with self.assertRaises(ValueError):
            Task.create("Valid title", tags=["a"] * 11)  # Too many tags

    def test_task_update_method(self):
        """Test Task update functionality"""
        task = Task.create("Original title")

        # Update title
        task.update(title="Updated title")
        self.assertEqual(task.title, "Updated title")

        # Update description
        task.update(description="Updated description")
        self.assertEqual(task.description, "Updated description")

        # Update tags
        task.update(tags=["new", "tags"])
        self.assertEqual(task.tags, ["new", "tags"])

    def test_task_mark_completed(self):
        """Test marking task as completed"""
        task = Task.create("Test task")
        self.assertEqual(task.status, TaskStatus.PENDING)

        task.mark_completed()
        self.assertEqual(task.status, TaskStatus.COMPLETED)

    def test_task_mark_pending(self):
        """Test marking task as pending"""
        task = Task.create("Test task")
        task.mark_completed()  # First mark as completed
        self.assertEqual(task.status, TaskStatus.COMPLETED)

        task.mark_pending()
        self.assertEqual(task.status, TaskStatus.PENDING)


class TestTaskStatusEnum(unittest.TestCase):
    """Test the TaskStatus enum implementation (T011)"""

    def test_task_status_enum_values(self):
        """Test TaskStatus enum values (T011)"""
        self.assertEqual(TaskStatus.PENDING.value, "PENDING")
        self.assertEqual(TaskStatus.COMPLETED.value, "COMPLETED")

        # Test that only valid statuses are accepted
        valid_statuses = [TaskStatus.PENDING, TaskStatus.COMPLETED]
        self.assertIn(TaskStatus.PENDING, valid_statuses)
        self.assertIn(TaskStatus.COMPLETED, valid_statuses)


class TestTaskEvents(unittest.TestCase):
    """Test the Task event implementations (T012-T016)"""

    def setUp(self):
        """Set up test data"""
        self.task = Task.create(
            title="Test task",
            description="Test description",
            tags=["work", "important"]
        )

    def test_task_created_event(self):
        """Test TaskCreated event (T012)"""
        event = TaskCreatedEvent(self.task)

        self.assertEqual(event.type, EventType.TASK_CREATED)
        self.assertEqual(event.aggregate_id, self.task.id)
        self.assertEqual(event.data['title'], "Test task")
        self.assertEqual(event.data['description'], "Test description")
        self.assertEqual(event.data['tags'], ["work", "important"])
        self.assertEqual(event.data['status'], "PENDING")

    def test_task_updated_event(self):
        """Test TaskUpdated event (T013)"""
        old_values = {
            'title': self.task.title,
            'description': self.task.description,
            'status': self.task.status.value,
            'tags': self.task.tags.copy()
        }

        # Update the task
        self.task.update(title="Updated title", description="Updated description")

        event = TaskUpdatedEvent(self.task, old_values)

        self.assertEqual(event.type, EventType.TASK_UPDATED)
        self.assertEqual(event.aggregate_id, self.task.id)
        self.assertEqual(event.data['new_values']['title'], "Updated title")
        self.assertEqual(event.data['old_values']['title'], "Test task")

    def test_task_deleted_event(self):
        """Test TaskDeleted event (T014)"""
        event = TaskDeletedEvent(self.task)

        self.assertEqual(event.type, EventType.TASK_DELETED)
        self.assertEqual(event.aggregate_id, self.task.id)
        self.assertEqual(event.data['title'], "Test task")

    def test_task_completed_event(self):
        """Test TaskCompleted event (T015)"""
        previous_status = self.task.status.value  # PENDING
        self.task.mark_completed()
        event = TaskCompletedEvent(self.task, previous_status=previous_status)

        self.assertEqual(event.type, EventType.TASK_COMPLETED)
        self.assertEqual(event.aggregate_id, self.task.id)
        self.assertEqual(event.data['previous_status'], "PENDING")

    def test_task_reopened_event(self):
        """Test TaskReopened event (T016)"""
        self.task.mark_completed()  # First mark as completed
        previous_status = self.task.status.value  # COMPLETED
        self.task.mark_pending()    # Then mark as pending again
        event = TaskReopenedEvent(self.task, previous_status=previous_status)

        self.assertEqual(event.type, EventType.TASK_REOPENED)
        self.assertEqual(event.aggregate_id, self.task.id)
        self.assertEqual(event.data['previous_status'], "COMPLETED")


class TestDomainValidator(unittest.TestCase):
    """Test the domain validation rules (T017)"""

    def test_validate_task_title(self):
        """Test task title validation"""
        # Valid titles
        self.assertTrue(DomainValidator.validate_task_title("Valid title"))
        self.assertTrue(DomainValidator.validate_task_title("a" * 256))  # Max length

        # Invalid titles
        with self.assertRaises(ValueError):
            DomainValidator.validate_task_title("")  # Empty

        with self.assertRaises(ValueError):
            DomainValidator.validate_task_title("a" * 257)  # Too long

    def test_validate_task_description(self):
        """Test task description validation"""
        # Valid descriptions
        self.assertTrue(DomainValidator.validate_task_description(None))
        self.assertTrue(DomainValidator.validate_task_description(""))
        self.assertTrue(DomainValidator.validate_task_description("a" * 1024))  # Max length

        # Invalid descriptions
        with self.assertRaises(ValueError):
            DomainValidator.validate_task_description("a" * 1025)  # Too long

    def test_validate_task_tags(self):
        """Test task tags validation"""
        # Valid tags
        self.assertTrue(DomainValidator.validate_task_tags(None))
        self.assertTrue(DomainValidator.validate_task_tags([]))
        self.assertTrue(DomainValidator.validate_task_tags(["valid-tag", "another_tag", "Valid123"]))
        self.assertTrue(DomainValidator.validate_task_tags(["a"] * 10))  # Max count

        # Invalid tags
        with self.assertRaises(ValueError):
            DomainValidator.validate_task_tags(["a"] * 11)  # Too many tags

        with self.assertRaises(ValueError):
            DomainValidator.validate_task_tags(["invalid tag"])  # Space not allowed

        with self.assertRaises(ValueError):
            DomainValidator.validate_task_tags(["invalid@tag"])  # Special char not allowed

    def test_validate_task_comprehensive(self):
        """Test comprehensive task validation"""
        task = Task.create("Valid title", "Valid description", ["tag1", "tag2"])
        self.assertTrue(DomainValidator.validate_task(task))

        # Test with invalid task
        invalid_task = Task.create("Valid title")
        invalid_task.title = ""  # Make it invalid
        with self.assertRaises(ValueError):
            DomainValidator.validate_task(invalid_task)


if __name__ == '__main__':
    unittest.main()