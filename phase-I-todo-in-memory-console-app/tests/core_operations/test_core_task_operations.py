"""
Tests for Core Task Operations Components
Testing the Core Task Operations tasks: T180-T186
"""
import unittest
from datetime import datetime
import time
from typing import List
from unittest.mock import Mock, MagicMock

from src.core_operations.core_task_operations import CoreTaskOperations, TaskConfirmation
from src.domain.entities import Task, TaskStatus
from src.repository.memory_repository import InMemoryTaskRepository
from src.events import EventStore, EventValidator, EventPublisher, EventBus


class TestCoreTaskOperations(unittest.TestCase):
    """Test core task operations functionality (T180-T186)"""

    def setUp(self):
        """Set up test fixtures"""
        # Create mock components
        self.event_bus = EventBus()
        self.event_store = EventStore()
        self.event_publisher = EventPublisher(self.event_bus)
        self.event_validator = EventValidator()

        # Create repository
        self.repository = InMemoryTaskRepository()

        # Create core operations instance
        self.core_ops = CoreTaskOperations(
            repository=self.repository,
            event_store=self.event_store,
            event_publisher=self.event_publisher,
            event_validator=self.event_validator
        )

    def test_add_task_with_title_validation(self):
        """Test Add Task functionality with title validation (T180)"""
        # Test adding a task with valid title
        confirmation = self.core_ops.add_task("Buy groceries")
        self.assertTrue(confirmation.success)
        self.assertIn("Task added successfully", confirmation.message)
        self.assertIsNotNone(confirmation.task_id)

        # Test adding a task with description
        confirmation = self.core_ops.add_task("Call mom", "Remember to call mom tonight")
        self.assertTrue(confirmation.success)
        self.assertIsNotNone(confirmation.task_id)

        # Test adding a task with empty title (should fail)
        confirmation = self.core_ops.add_task("")
        self.assertFalse(confirmation.success)
        self.assertIn("cannot be empty", confirmation.message)

        # Test adding a task with too long title (should fail)
        long_title = "A" * 257  # More than 256 characters
        confirmation = self.core_ops.add_task(long_title)
        self.assertFalse(confirmation.success)
        self.assertIn("exceeds maximum length", confirmation.message)

        # Performance test: ensure operation completes within 100ms
        start_time = time.time()
        confirmation = self.core_ops.add_task("Performance test task")
        duration = (time.time() - start_time) * 1000
        self.assertLess(duration, 100, f"Add task operation took {duration}ms, exceeding 100ms limit")

    def test_list_tasks_with_status_indicators(self):
        """Test View/List Tasks functionality with status indicators (T181)"""
        # Add some tasks
        task1_id = self.core_ops.add_task("Task 1").task_id
        task2_id = self.core_ops.add_task("Task 2", "Description for task 2").task_id

        # Complete one task
        self.core_ops.complete_task(task1_id)

        # Test listing all tasks
        confirmation = self.core_ops.list_tasks()
        self.assertTrue(confirmation.success)
        self.assertGreaterEqual(len(confirmation.task_data), 2)

        # Test listing completed tasks only
        confirmation = self.core_ops.list_tasks("completed")
        self.assertTrue(confirmation.success)
        completed_tasks = [t for t in confirmation.task_data if t['status'] == 'COMPLETED']
        self.assertEqual(len(completed_tasks), 1)

        # Test listing pending tasks only
        confirmation = self.core_ops.list_tasks("pending")
        self.assertTrue(confirmation.success)
        pending_tasks = [t for t in confirmation.task_data if t['status'] == 'PENDING']
        self.assertEqual(len(pending_tasks), 1)

        # Performance test: ensure operation completes within 200ms for up to 1000 tasks
        start_time = time.time()
        confirmation = self.core_ops.list_tasks()
        duration = (time.time() - start_time) * 1000
        self.assertLess(duration, 200, f"List tasks operation took {duration}ms, exceeding 200ms limit")

    def test_update_task_preserving_unchanged_fields(self):
        """Test Update Task functionality preserving unchanged fields (T182)"""
        # Add a task first
        original_confirmation = self.core_ops.add_task("Original title", "Original description")
        self.assertTrue(original_confirmation.success)
        task_id = original_confirmation.task_id

        # Update only the title, keeping description unchanged
        update_confirmation = self.core_ops.update_task(task_id, title="Updated title")
        self.assertTrue(update_confirmation.success)

        # Verify the task was updated correctly
        updated_task_data = update_confirmation.task_data
        self.assertEqual(updated_task_data['title'], "Updated title")
        self.assertEqual(updated_task_data['description'], "Original description")  # Should remain unchanged

        # Update only the description, keeping title unchanged
        update_confirmation = self.core_ops.update_task(task_id, description="Updated description")
        self.assertTrue(update_confirmation.success)

        updated_task_data = update_confirmation.task_data
        self.assertEqual(updated_task_data['title'], "Updated title")  # Should remain unchanged
        self.assertEqual(updated_task_data['description'], "Updated description")

        # Performance test: ensure operation completes within 100ms
        start_time = time.time()
        update_confirmation = self.core_ops.update_task(task_id, title="Performance test")
        duration = (time.time() - start_time) * 1000
        self.assertLess(duration, 100, f"Update task operation took {duration}ms, exceeding 100ms limit")

    def test_delete_task_with_id_validation(self):
        """Test Delete Task functionality with ID validation (T183)"""
        # Add a task first
        add_confirmation = self.core_ops.add_task("Task to delete")
        self.assertTrue(add_confirmation.success)
        task_id = add_confirmation.task_id

        # Verify task exists before deletion
        list_confirmation = self.core_ops.list_tasks()
        original_task_count = len(list_confirmation.task_data)

        # Delete the task
        delete_confirmation = self.core_ops.delete_task(task_id)
        self.assertTrue(delete_confirmation.success)
        self.assertIn("deleted successfully", delete_confirmation.message)

        # Verify task no longer exists
        list_confirmation = self.core_ops.list_tasks()
        new_task_count = len(list_confirmation.task_data)
        self.assertEqual(new_task_count, original_task_count - 1)

        # Try to delete a non-existent task (should fail)
        fake_task_id = "non-existent-id"
        delete_confirmation = self.core_ops.delete_task(fake_task_id)
        self.assertFalse(delete_confirmation.success)
        self.assertIn("not found", delete_confirmation.message)

        # Performance test: ensure operation completes within 100ms
        another_task_id = self.core_ops.add_task("Another task").task_id
        start_time = time.time()
        delete_confirmation = self.core_ops.delete_task(another_task_id)
        duration = (time.time() - start_time) * 1000
        self.assertLess(duration, 100, f"Delete task operation took {duration}ms, exceeding 100ms limit")

    def test_mark_task_complete_incomplete_functionality(self):
        """Test Mark Task Complete/Incomplete functionality (T184)"""
        # Add a task
        add_confirmation = self.core_ops.add_task("Test task")
        self.assertTrue(add_confirmation.success)
        task_id = add_confirmation.task_id

        # Verify task is initially pending
        list_confirmation = self.core_ops.list_tasks()
        task = next((t for t in list_confirmation.task_data if t['id'] == task_id), None)
        self.assertEqual(task['status'], 'PENDING')

        # Complete the task
        complete_confirmation = self.core_ops.complete_task(task_id)
        self.assertTrue(complete_confirmation.success)
        self.assertIn("marked as complete", complete_confirmation.message)

        # Verify task is now completed
        list_confirmation = self.core_ops.list_tasks()
        task = next((t for t in list_confirmation.task_data if t['id'] == task_id), None)
        self.assertEqual(task['status'], 'COMPLETED')

        # Mark task as incomplete
        incomplete_confirmation = self.core_ops.incomplete_task(task_id)
        self.assertTrue(incomplete_confirmation.success)
        self.assertIn("marked as incomplete", incomplete_confirmation.message)

        # Verify task is now pending again
        list_confirmation = self.core_ops.list_tasks()
        task = next((t for t in list_confirmation.task_data if t['id'] == task_id), None)
        self.assertEqual(task['status'], 'PENDING')

        # Performance test: ensure operations complete within 100ms
        start_time = time.time()
        self.core_ops.complete_task(task_id)
        complete_duration = (time.time() - start_time) * 1000

        start_time = time.time()
        self.core_ops.incomplete_task(task_id)
        incomplete_duration = (time.time() - start_time) * 1000

        self.assertLess(complete_duration, 100, f"Complete task operation took {complete_duration}ms, exceeding 100ms limit")
        self.assertLess(incomplete_duration, 100, f"Incomplete task operation took {incomplete_duration}ms, exceeding 100ms limit")

    def test_task_confirmation_for_successful_operations(self):
        """Test task confirmation for successful operations (T185)"""
        # Add a task and get confirmation
        confirmation = self.core_ops.add_task("Test task for confirmation")
        self.assertTrue(confirmation.success)

        # Confirm the operation
        confirmation_message = self.core_ops.confirm_operation("add", confirmation)
        self.assertIn("Task added successfully", confirmation_message)
        self.assertNotIn("Error:", confirmation_message)

        # Test error confirmation
        error_confirmation = TaskConfirmation(success=False, message="Something went wrong")
        error_message = self.core_ops.confirm_operation("add", error_confirmation)
        self.assertIn("Error:", error_message)
        self.assertIn("Something went wrong", error_message)

    def test_tags_attachment_to_tasks_functionality(self):
        """Test tags attachment to tasks functionality (T186)"""
        # Add a task
        add_confirmation = self.core_ops.add_task("Task with tags")
        self.assertTrue(add_confirmation.success)
        task_id = add_confirmation.task_id

        # Add tags to the task
        tags = ["work", "urgent", "important"]
        tag_confirmation = self.core_ops.add_tags_to_task(task_id, tags)
        self.assertTrue(tag_confirmation.success)
        self.assertIn("Tags added to task", tag_confirmation.message)

        # Verify tags were added
        updated_task_data = tag_confirmation.task_data
        self.assertIsNotNone(updated_task_data['tags'])
        for tag in tags:
            self.assertIn(tag, updated_task_data['tags'])

        # Add more tags to existing ones
        more_tags = ["priority", "follow-up"]
        additional_confirmation = self.core_ops.add_tags_to_task(task_id, more_tags)
        self.assertTrue(additional_confirmation.success)

        # Verify all tags are present
        updated_task_data = additional_confirmation.task_data
        all_expected_tags = tags + more_tags
        for tag in all_expected_tags:
            self.assertIn(tag, updated_task_data['tags'])

        # Test with invalid tag format (should fail)
        invalid_tags = ["invalid tag with spaces"]
        invalid_confirmation = self.core_ops.add_tags_to_task(task_id, invalid_tags)
        self.assertFalse(invalid_confirmation.success)
        self.assertIn("Invalid tag format", invalid_confirmation.message)

        # Performance test: ensure operation completes within 100ms
        fresh_task_id = self.core_ops.add_task("Fresh task").task_id
        start_time = time.time()
        tag_confirmation = self.core_ops.add_tags_to_task(fresh_task_id, ["performance", "test"])
        duration = (time.time() - start_time) * 1000
        self.assertLess(duration, 100, f"Add tags operation took {duration}ms, exceeding 100ms limit")


class TestCoreTaskOperationsIntegration(unittest.TestCase):
    """Test core task operations integration scenarios (T180-T186)"""

    def setUp(self):
        """Set up test fixtures"""
        self.event_bus = EventBus()
        self.event_store = EventStore()
        self.event_publisher = EventPublisher(self.event_bus)
        self.event_validator = EventValidator()
        self.repository = InMemoryTaskRepository()
        self.core_ops = CoreTaskOperations(
            repository=self.repository,
            event_store=self.event_store,
            event_publisher=self.event_publisher,
            event_validator=self.event_validator
        )

    def test_full_task_lifecycle(self):
        """Test complete task lifecycle: add, update, complete, incomplete, delete (T180-T186)"""
        # Add a task
        add_confirmation = self.core_ops.add_task("Complete lifecycle test", "Test description", ["test", "lifecycle"])
        self.assertTrue(add_confirmation.success)
        task_id = add_confirmation.task_id

        # Update the task
        update_confirmation = self.core_ops.update_task(task_id, title="Updated lifecycle test", description="Updated description")
        self.assertTrue(update_confirmation.success)

        # Add more tags
        tag_confirmation = self.core_ops.add_tags_to_task(task_id, ["updated", "verification"])
        self.assertTrue(tag_confirmation.success)

        # List tasks to verify the task exists and has correct data
        list_confirmation = self.core_ops.list_tasks()
        self.assertTrue(list_confirmation.success)
        task = next((t for t in list_confirmation.task_data if t['id'] == task_id), None)
        self.assertIsNotNone(task)
        self.assertEqual(task['title'], "Updated lifecycle test")
        self.assertEqual(task['description'], "Updated description")
        self.assertIn("test", task['tags'])
        self.assertIn("lifecycle", task['tags'])
        self.assertIn("updated", task['tags'])
        self.assertIn("verification", task['tags'])

        # Complete the task
        complete_confirmation = self.core_ops.complete_task(task_id)
        self.assertTrue(complete_confirmation.success)

        # Verify completion
        list_confirmation = self.core_ops.list_tasks()
        task = next((t for t in list_confirmation.task_data if t['id'] == task_id), None)
        self.assertEqual(task['status'], 'COMPLETED')

        # Mark as incomplete
        incomplete_confirmation = self.core_ops.incomplete_task(task_id)
        self.assertTrue(incomplete_confirmation.success)

        # Verify it's back to pending
        list_confirmation = self.core_ops.list_tasks()
        task = next((t for t in list_confirmation.task_data if t['id'] == task_id), None)
        self.assertEqual(task['status'], 'PENDING')

        # Delete the task
        delete_confirmation = self.core_ops.delete_task(task_id)
        self.assertTrue(delete_confirmation.success)

        # Verify task no longer exists
        list_confirmation = self.core_ops.list_tasks()
        task = next((t for t in list_confirmation.task_data if t['id'] == task_id), None)
        self.assertIsNone(task)

    def test_multiple_tasks_concurrent_operations(self):
        """Test multiple tasks with concurrent operations"""
        # Add multiple tasks
        tasks_data = [
            ("Task 1", "Description 1", ["tag1"]),
            ("Task 2", "Description 2", ["tag2"]),
            ("Task 3", "Description 3", ["tag3"]),
        ]

        task_ids = []
        for title, desc, tags in tasks_data:
            confirmation = self.core_ops.add_task(title, desc, tags)
            self.assertTrue(confirmation.success)
            task_ids.append(confirmation.task_id)

        # Update different tasks
        for i, task_id in enumerate(task_ids):
            update_confirmation = self.core_ops.update_task(task_id, title=f"Updated Task {i+1}")
            self.assertTrue(update_confirmation.success)

        # Complete alternate tasks
        for i, task_id in enumerate(task_ids):
            if i % 2 == 0:  # Complete even-indexed tasks
                complete_confirmation = self.core_ops.complete_task(task_id)
                self.assertTrue(complete_confirmation.success)

        # Verify status distribution
        list_confirmation = self.core_ops.list_tasks()
        completed_count = sum(1 for t in list_confirmation.task_data if t['status'] == 'COMPLETED')
        pending_count = sum(1 for t in list_confirmation.task_data if t['status'] == 'PENDING')

        self.assertEqual(completed_count, 2)  # Tasks 0 and 2 (0-indexed)
        self.assertEqual(pending_count, 1)   # Task 1 (0-indexed)

    def test_performance_with_multiple_tasks(self):
        """Test performance with multiple tasks"""
        # Add 100 tasks to test performance
        task_ids = []
        start_time = time.time()

        for i in range(100):
            confirmation = self.core_ops.add_task(f"Performance Task {i}", f"Description {i}")
            self.assertTrue(confirmation.success)
            task_ids.append(confirmation.task_id)

        add_duration = (time.time() - start_time) * 1000
        # Average time per task should be reasonable
        avg_add_time = add_duration / 100
        self.assertLess(avg_add_time, 10, f"Average add task time {avg_add_time}ms exceeds 10ms per task")

        # Test listing performance
        start_time = time.time()
        list_confirmation = self.core_ops.list_tasks()
        list_duration = (time.time() - start_time) * 1000
        self.assertLess(list_duration, 200, f"List 100 tasks took {list_duration}ms, exceeding 200ms limit")

        # Test updating performance
        start_time = time.time()
        for task_id in task_ids[:10]:  # Update first 10 tasks
            self.core_ops.update_task(task_id, title="Updated")
        update_duration = (time.time() - start_time) * 1000
        avg_update_time = update_duration / 10
        self.assertLess(avg_update_time, 100, f"Average update task time {avg_update_time}ms exceeds 100ms per task")

    def test_error_handling_scenarios(self):
        """Test various error handling scenarios"""
        # Try to update a non-existent task
        confirmation = self.core_ops.update_task("non-existent-id", title="Should fail")
        self.assertFalse(confirmation.success)
        self.assertIn("not found", confirmation.message)

        # Try to delete a non-existent task
        confirmation = self.core_ops.delete_task("non-existent-id")
        self.assertFalse(confirmation.success)
        self.assertIn("not found", confirmation.message)

        # Try to complete a non-existent task
        confirmation = self.core_ops.complete_task("non-existent-id")
        self.assertFalse(confirmation.success)
        self.assertIn("not found", confirmation.message)

        # Try to mark incomplete a non-existent task
        confirmation = self.core_ops.incomplete_task("non-existent-id")
        self.assertFalse(confirmation.success)
        self.assertIn("not found", confirmation.message)

        # Try to add tags to a non-existent task
        confirmation = self.core_ops.add_tags_to_task("non-existent-id", ["tag"])
        self.assertFalse(confirmation.success)
        self.assertIn("not found", confirmation.message)

        # Try to add invalid title
        confirmation = self.core_ops.add_task("")  # Empty title
        self.assertFalse(confirmation.success)
        self.assertIn("cannot be empty", confirmation.message)


if __name__ == '__main__':
    unittest.main()