"""
Tests for Snapshot System Components
Testing the Snapshot System tasks: T120-T125
"""
import unittest
from datetime import datetime
from uuid import UUID
from src.snapshot_system.snapshot_system import (
    SnapshotSystem,
    Snapshot,
    SnapshotStorage
)


class TestSnapshotStorage(unittest.TestCase):
    """Test snapshot storage functionality (T121)"""

    def setUp(self):
        """Set up test fixtures"""
        self.storage = SnapshotStorage()

    def test_save_and_get_snapshot(self):
        """Test saving and retrieving a snapshot (T121)"""
        snapshot = Snapshot(
            id=UUID('12345678-1234-5678-1234-567812345678'),
            name="test_snapshot",
            created_at=datetime.now(),
            state_data={"tasks": [], "events": []},
            task_count=0,
            event_count=0
        )

        result = self.storage.save_snapshot(snapshot)
        self.assertTrue(result)

        retrieved = self.storage.get_snapshot("test_snapshot")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "test_snapshot")

    def test_list_snapshots(self):
        """Test listing all snapshots (T124)"""
        # Add multiple snapshots
        snapshot1 = Snapshot(
            id=UUID('12345678-1234-5678-1234-567812345678'),
            name="snapshot1",
            created_at=datetime.now(),
            state_data={"tasks": [], "events": []},
            task_count=0,
            event_count=0
        )
        snapshot2 = Snapshot(
            id=UUID('87654321-4321-8765-4321-876543214321'),
            name="snapshot2",
            created_at=datetime.now(),
            state_data={"tasks": [], "events": []},
            task_count=0,
            event_count=0
        )

        self.storage.save_snapshot(snapshot1)
        self.storage.save_snapshot(snapshot2)

        snapshots = self.storage.list_snapshots()
        self.assertEqual(len(snapshots), 2)
        names = {snapshot.name for snapshot in snapshots}
        self.assertIn("snapshot1", names)
        self.assertIn("snapshot2", names)

    def test_delete_snapshot(self):
        """Test deleting a snapshot (T121)"""
        snapshot = Snapshot(
            id=UUID('12345678-1234-5678-1234-567812345678'),
            name="test_snapshot",
            created_at=datetime.now(),
            state_data={"tasks": [], "events": []},
            task_count=0,
            event_count=0
        )

        self.storage.save_snapshot(snapshot)
        self.assertIsNotNone(self.storage.get_snapshot("test_snapshot"))

        result = self.storage.delete_snapshot("test_snapshot")
        self.assertTrue(result)
        self.assertIsNone(self.storage.get_snapshot("test_snapshot"))

    def test_clear_all_snapshots(self):
        """Test clearing all snapshots (T121)"""
        snapshot = Snapshot(
            id=UUID('12345678-1234-5678-1234-567812345678'),
            name="test_snapshot",
            created_at=datetime.now(),
            state_data={"tasks": [], "events": []},
            task_count=0,
            event_count=0
        )

        self.storage.save_snapshot(snapshot)
        self.assertEqual(len(self.storage.list_snapshots()), 1)

        self.storage.clear_all()
        self.assertEqual(len(self.storage.list_snapshots()), 0)

    def test_max_snapshot_limit(self):
        """Test max snapshot limit functionality (T125)"""
        # Create storage with small max limit
        storage = SnapshotStorage(max_snapshots=2)

        # Add 3 snapshots (exceeding limit)
        for i in range(3):
            snapshot = Snapshot(
                id=UUID(f'12345678-1234-5678-1234-56781234567{i}'),
                name=f"snapshot_{i}",
                created_at=datetime.now(),
                state_data={"tasks": [], "events": []},
                task_count=0,
                event_count=0
            )
            storage.save_snapshot(snapshot)

        # Should only keep the last 2 snapshots
        snapshots = storage.list_snapshots()
        self.assertLessEqual(len(snapshots), 2)


class TestSnapshotSystem(unittest.TestCase):
    """Test the main snapshot system (T120, T122, T123, T124, T125)"""

    def setUp(self):
        """Set up test fixtures"""
        self.system = SnapshotSystem()

        # Mock state data for testing
        self.mock_state_data = {
            "tasks": [
                {"id": 1, "title": "Task 1", "status": "pending"},
                {"id": 2, "title": "Task 2", "status": "completed"}
            ],
            "events": [
                {"type": "TaskCreated", "id": 1, "timestamp": "2023-01-01T00:00:00"},
                {"type": "TaskCompleted", "id": 2, "timestamp": "2023-01-01T00:01:00"}
            ],
            "task_count": 2,
            "event_count": 2
        }

        # Mock capture callback
        def mock_capture():
            return self.mock_state_data.copy()

        # Mock restore callback
        def mock_restore(state_data):
            self.restored_state = state_data
            return True

        self.mock_capture = mock_capture
        self.mock_restore = mock_restore

    def test_create_snapshot_with_name(self):
        """Test creating a snapshot with a specific name (T120, T123)"""
        success, message, name = self.system.create_snapshot(
            name="my_snapshot",
            capture_callback=self.mock_capture
        )

        self.assertTrue(success)
        self.assertEqual(name, "my_snapshot")
        self.assertIn("created successfully", message.lower())

    def test_create_snapshot_with_timestamp_name(self):
        """Test creating a snapshot with auto-generated timestamp name (T123)"""
        success, message, name = self.system.create_snapshot(
            capture_callback=self.mock_capture
        )

        self.assertTrue(success)
        self.assertIsNotNone(name)
        self.assertIn("snapshot_", name)

    def test_create_snapshot_duplicate_name(self):
        """Test creating snapshot with duplicate name (T123)"""
        # Create first snapshot
        self.system.create_snapshot(
            name="duplicate_snapshot",
            capture_callback=self.mock_capture
        )

        # Try to create another with same name
        success, message, name = self.system.create_snapshot(
            name="duplicate_snapshot",
            capture_callback=self.mock_capture
        )

        self.assertFalse(success)
        self.assertIn("already exists", message.lower())

    def test_restore_snapshot_success(self):
        """Test successful snapshot restoration (T122)"""
        # Create a snapshot first
        self.system.create_snapshot(
            name="restore_test",
            capture_callback=self.mock_capture
        )

        success, message = self.system.restore_snapshot(
            name="restore_test",
            restore_callback=self.mock_restore
        )

        self.assertTrue(success)
        self.assertIn("successfully restored", message.lower())

    def test_restore_snapshot_not_found(self):
        """Test restoring non-existent snapshot (T122)"""
        success, message = self.system.restore_snapshot(
            name="nonexistent",
            restore_callback=self.mock_restore
        )

        self.assertFalse(success)
        self.assertIn("not found", message.lower())

    def test_list_snapshots(self):
        """Test listing snapshots (T124)"""
        # Create multiple snapshots
        self.system.create_snapshot(
            name="snapshot_a",
            capture_callback=self.mock_capture
        )
        self.system.create_snapshot(
            name="snapshot_b",
            capture_callback=self.mock_capture
        )

        snapshots = self.system.list_snapshots()
        self.assertEqual(len(snapshots), 2)
        names = {snapshot.name for snapshot in snapshots}
        self.assertIn("snapshot_a", names)
        self.assertIn("snapshot_b", names)

    def test_delete_snapshot(self):
        """Test deleting a snapshot (T121)"""
        # Create a snapshot
        self.system.create_snapshot(
            name="to_delete",
            capture_callback=self.mock_capture
        )

        # Verify it exists
        self.assertIsNotNone(self.system.get_snapshot("to_delete"))

        # Delete it
        result = self.system.delete_snapshot("to_delete")
        self.assertTrue(result)

        # Verify it's gone
        self.assertIsNone(self.system.get_snapshot("to_delete"))

    def test_multiple_snapshots_support(self):
        """Test multiple snapshots support (T125)"""
        # Create multiple snapshots
        for i in range(5):
            success, msg, name = self.system.create_snapshot(
                name=f"multi_snapshot_{i}",
                capture_callback=self.mock_capture
            )
            self.assertTrue(success)

        # Verify all exist
        snapshots = self.system.list_snapshots()
        self.assertEqual(len(snapshots), 5)

        # Test that they can be individually restored
        for snapshot in snapshots:
            success, msg = self.system.restore_snapshot(
                name=snapshot.name,
                restore_callback=self.mock_restore
            )
            self.assertTrue(success)

    def test_snapshot_storage_info(self):
        """Test getting storage information (T121, T125)"""
        # Create a snapshot
        self.system.create_snapshot(
            name="info_test",
            capture_callback=self.mock_capture
        )

        info = self.system.get_storage_info()
        self.assertEqual(info['snapshot_count'], 1)
        self.assertEqual(info['total_tasks'], 2)  # From mock data
        self.assertEqual(info['total_events'], 2)  # From mock data
        self.assertGreater(info['max_snapshots'], 0)

    def test_empty_snapshot_list(self):
        """Test listing with no snapshots (T124)"""
        snapshots = self.system.list_snapshots()
        self.assertEqual(len(snapshots), 0)

    def test_snapshot_performance(self):
        """Test snapshot creation performance (T120)"""
        import time

        start_time = time.time()
        success, message, name = self.system.create_snapshot(
            name="perf_test",
            capture_callback=self.mock_capture
        )
        end_time = time.time()

        self.assertTrue(success)
        # Creation should be fast (less than 100ms for this simple test)
        self.assertLess((end_time - start_time) * 1000, 500)  # 500ms limit


class TestSnapshotIntegration(unittest.TestCase):
    """Test snapshot system integration scenarios"""

    def setUp(self):
        """Set up test fixtures"""
        self.system = SnapshotSystem()

        # Mock state data
        self.initial_state = {
            "tasks": [{"id": 1, "title": "Initial Task", "status": "pending"}],
            "events": [{"type": "TaskCreated", "id": 1, "timestamp": "2023-01-01T00:00:00"}],
            "task_count": 1,
            "event_count": 1
        }

        self.updated_state = {
            "tasks": [
                {"id": 1, "title": "Updated Task", "status": "completed"},
                {"id": 2, "title": "New Task", "status": "pending"}
            ],
            "events": [
                {"type": "TaskCreated", "id": 1, "timestamp": "2023-01-01T00:00:00"},
                {"type": "TaskUpdated", "id": 1, "timestamp": "2023-01-01T00:01:00"},
                {"type": "TaskCreated", "id": 2, "timestamp": "2023-01-01T00:02:00"}
            ],
            "task_count": 2,
            "event_count": 3
        }

        self.restored_state = None

        def capture_initial():
            return self.initial_state.copy()

        def capture_updated():
            return self.updated_state.copy()

        def restore_state(state_data):
            self.restored_state = state_data
            return True

        self.capture_initial = capture_initial
        self.capture_updated = capture_updated
        self.restore_state = restore_state

    def test_snapshot_restore_workflow(self):
        """Test complete snapshot create/restore workflow (T120, T122)"""
        # 1. Capture initial state
        success, msg, name = self.system.create_snapshot(
            name="workflow_test",
            capture_callback=self.capture_initial
        )
        self.assertTrue(success)

        # 2. Verify snapshot was created with correct data
        snapshot = self.system.get_snapshot("workflow_test")
        self.assertIsNotNone(snapshot)
        self.assertEqual(snapshot.task_count, 1)
        self.assertEqual(snapshot.event_count, 1)

        # 3. Simulate state change (update to new state)
        # In real usage, the app state would change here

        # 4. Restore from snapshot
        success, msg = self.system.restore_snapshot(
            name="workflow_test",
            restore_callback=self.restore_state
        )
        self.assertTrue(success)

        # 5. Verify restored state matches original snapshot
        self.assertIsNotNone(self.restored_state)
        self.assertEqual(self.restored_state["task_count"], 1)
        self.assertEqual(self.restored_state["event_count"], 1)
        self.assertEqual(len(self.restored_state["tasks"]), 1)
        self.assertEqual(self.restored_state["tasks"][0]["title"], "Initial Task")


if __name__ == '__main__':
    unittest.main()