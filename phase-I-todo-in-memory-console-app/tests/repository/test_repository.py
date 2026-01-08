"""
Unit tests for In-Memory Repository implementation
Testing the In-Memory Repository tasks: T020-T024
"""
import unittest
import threading
import time
from src.repository.memory_repository import InMemoryTaskRepository
from src.repository.interface import TaskRepository
from src.domain.entities import Task
from src.domain.status import TaskStatus


class TestTaskRepositoryInterface(unittest.TestCase):
    """Test the repository interface compliance (T020)"""

    def test_interface_conformance(self):
        """Test that InMemoryTaskRepository conforms to TaskRepository interface"""
        repo = InMemoryTaskRepository()

        # Check that all required methods exist
        self.assertTrue(hasattr(repo, 'add'))
        self.assertTrue(hasattr(repo, 'get'))
        self.assertTrue(hasattr(repo, 'update'))
        self.assertTrue(hasattr(repo, 'delete'))
        self.assertTrue(hasattr(repo, 'list_all'))
        self.assertTrue(hasattr(repo, 'list_by_status'))
        self.assertTrue(hasattr(repo, 'exists'))


class TestInMemoryTaskRepository(unittest.TestCase):
    """Test the concrete repository implementation (T021, T022)"""

    def setUp(self):
        """Set up test data"""
        self.repo = InMemoryTaskRepository()
        self.task1 = Task.create("Test Task 1", "Description 1")
        self.task2 = Task.create("Test Task 2", "Description 2")
        self.task2.mark_completed()  # Mark as completed

    def test_add_task(self):
        """Test adding a task (T022)"""
        self.repo.add(self.task1)

        retrieved_task = self.repo.get(self.task1.id)
        self.assertEqual(retrieved_task.id, self.task1.id)
        self.assertEqual(retrieved_task.title, self.task1.title)
        self.assertEqual(retrieved_task.description, self.task1.description)

    def test_get_existing_task(self):
        """Test retrieving an existing task (T022)"""
        self.repo.add(self.task1)

        retrieved_task = self.repo.get(self.task1.id)
        self.assertIsNotNone(retrieved_task)
        self.assertEqual(retrieved_task.id, self.task1.id)

    def test_get_nonexistent_task(self):
        """Test retrieving a non-existent task (T022)"""
        retrieved_task = self.repo.get("nonexistent-id")
        self.assertIsNone(retrieved_task)

    def test_update_existing_task(self):
        """Test updating an existing task (T022)"""
        self.repo.add(self.task1)

        # Modify the task
        self.task1.update(title="Updated Title", description="Updated Description")

        # Update in repository
        result = self.repo.update(self.task1)
        self.assertTrue(result)

        # Verify update
        updated_task = self.repo.get(self.task1.id)
        self.assertEqual(updated_task.title, "Updated Title")
        self.assertEqual(updated_task.description, "Updated Description")

    def test_update_nonexistent_task(self):
        """Test updating a non-existent task (T022)"""
        result = self.repo.update(self.task1)
        self.assertFalse(result)

    def test_delete_existing_task(self):
        """Test deleting an existing task (T022)"""
        self.repo.add(self.task1)

        result = self.repo.delete(self.task1.id)
        self.assertTrue(result)

        # Verify deletion
        retrieved_task = self.repo.get(self.task1.id)
        self.assertIsNone(retrieved_task)

    def test_delete_nonexistent_task(self):
        """Test deleting a non-existent task (T022)"""
        result = self.repo.delete("nonexistent-id")
        self.assertFalse(result)

    def test_list_all_tasks(self):
        """Test listing all tasks (T022)"""
        self.repo.add(self.task1)
        self.repo.add(self.task2)

        all_tasks = self.repo.list_all()
        self.assertEqual(len(all_tasks), 2)
        task_ids = {task.id for task in all_tasks}
        self.assertIn(self.task1.id, task_ids)
        self.assertIn(self.task2.id, task_ids)

    def test_list_by_status_pending(self):
        """Test filtering tasks by status - pending (T023)"""
        self.repo.add(self.task1)  # This is pending by default
        self.repo.add(self.task2)  # This is completed

        pending_tasks = self.repo.list_by_status(TaskStatus.PENDING)
        self.assertEqual(len(pending_tasks), 1)
        self.assertEqual(pending_tasks[0].id, self.task1.id)

    def test_list_by_status_completed(self):
        """Test filtering tasks by status - completed (T023)"""
        self.repo.add(self.task1)  # This is pending by default
        self.repo.add(self.task2)  # This is completed

        completed_tasks = self.repo.list_by_status(TaskStatus.COMPLETED)
        self.assertEqual(len(completed_tasks), 1)
        self.assertEqual(completed_tasks[0].id, self.task2.id)

    def test_exists_positive(self):
        """Test checking existence of existing task (T022)"""
        self.repo.add(self.task1)
        self.assertTrue(self.repo.exists(self.task1.id))

    def test_exists_negative(self):
        """Test checking existence of non-existent task (T022)"""
        self.assertFalse(self.repo.exists("nonexistent-id"))

    def test_duplicate_prevention(self):
        """Test repository validation for duplicate prevention (T024)"""
        self.repo.add(self.task1)

        # Try to add the same task again - should raise an error
        with self.assertRaises(ValueError):
            self.repo.add(self.task1)

    def test_count_and_clear(self):
        """Test count and clear functionality"""
        self.repo.add(self.task1)
        self.repo.add(self.task2)

        self.assertEqual(self.repo.count(), 2)

        self.repo.clear()
        self.assertEqual(self.repo.count(), 0)
        self.assertEqual(len(self.repo.list_all()), 0)


class TestThreadSafety(unittest.TestCase):
    """Test thread safety of repository operations (T021)"""

    def test_concurrent_access(self):
        """Test concurrent access to repository (T021)"""
        repo = InMemoryTaskRepository()
        results = []

        def worker(thread_id):
            # Add different tasks from different threads
            task = Task.create(f"Task from thread {thread_id}")
            repo.add(task)
            results.append(repo.get(task.id).title)

        # Create and start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all tasks were added successfully
        self.assertEqual(len(results), 5)
        all_tasks = repo.list_all()
        self.assertEqual(len(all_tasks), 5)

    def test_concurrent_read_write(self):
        """Test concurrent read and write operations (T021)"""
        repo = InMemoryTaskRepository()
        task = Task.create("Concurrent test task")
        repo.add(task)

        read_results = []
        write_results = []

        def reader():
            for _ in range(10):
                retrieved = repo.get(task.id)
                if retrieved:
                    read_results.append(retrieved.title)
                time.sleep(0.001)  # Small delay to allow interleaving

        def updater():
            for i in range(10):
                task.update(title=f"Updated title {i}")
                success = repo.update(task)
                write_results.append(success)
                time.sleep(0.001)  # Small delay to allow interleaving

        # Start reader and writer threads
        reader_thread = threading.Thread(target=reader)
        writer_thread = threading.Thread(target=updater)

        reader_thread.start()
        writer_thread.start()

        reader_thread.join()
        writer_thread.join()

        # Both operations should complete without errors
        self.assertGreater(len(read_results), 0)
        self.assertGreater(len(write_results), 0)
        self.assertTrue(all(write_results))


if __name__ == '__main__':
    unittest.main()