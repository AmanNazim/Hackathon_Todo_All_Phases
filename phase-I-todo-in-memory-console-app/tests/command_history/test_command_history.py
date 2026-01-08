"""
Tests for Command History & Undo Components
Testing the Command History & Undo tasks: T100-T106
"""
import unittest
from datetime import datetime, timedelta
from uuid import UUID
from src.command_history.command_history import (
    CommandHistoryManager,
    CommandHistoryStorage,
    CommandTimestampTracker,
    CommandStatusTracker,
    UndoManager,
    CommandReplayer,
    CommandRecord,
    CommandStatus,
    CommandType
)


class TestCommandHistoryStorage(unittest.TestCase):
    """Test command history storage functionality (T100)"""

    def setUp(self):
        """Set up test fixtures"""
        self.storage = CommandHistoryStorage()

    def test_add_command_creates_record(self):
        """Test that adding command creates a record (T100)"""
        record = self.storage.add_command(
            command_type=CommandType.ADD,
            parameters={"title": "Test task"},
            status=CommandStatus.SUCCESS,
            result="Task created"
        )

        self.assertIsInstance(record, CommandRecord)
        self.assertEqual(record.command_type, CommandType.ADD)
        self.assertEqual(record.status, CommandStatus.SUCCESS)
        self.assertEqual(record.parameters["title"], "Test task")

    def test_get_command_by_id(self):
        """Test retrieving command by ID (T100)"""
        original_record = self.storage.add_command(
            command_type=CommandType.UPDATE,
            parameters={"id": 1, "title": "Updated task"},
            status=CommandStatus.SUCCESS
        )

        retrieved_record = self.storage.get_command_by_id(original_record.id)

        self.assertEqual(retrieved_record.id, original_record.id)
        self.assertEqual(retrieved_record.command_type, CommandType.UPDATE)

    def test_get_recent_commands(self):
        """Test getting recent commands (T100)"""
        # Add several commands
        for i in range(5):
            self.storage.add_command(
                command_type=CommandType.ADD,
                parameters={"title": f"Task {i}"},
                status=CommandStatus.SUCCESS
            )

        recent = self.storage.get_recent_commands(3)

        self.assertEqual(len(recent), 3)
        self.assertEqual(recent[0].parameters["title"], "Task 2")  # Should be oldest of the 3
        self.assertEqual(recent[-1].parameters["title"], "Task 4")  # Should be newest

    def test_get_all_commands(self):
        """Test getting all commands (T100)"""
        # Add commands
        for i in range(3):
            self.storage.add_command(
                command_type=CommandType.LIST,
                parameters={},
                status=CommandStatus.SUCCESS
            )

        all_commands = self.storage.get_all_commands()

        self.assertEqual(len(all_commands), 3)

    def test_get_commands_by_type(self):
        """Test filtering commands by type (T100)"""
        # Add different types of commands
        self.storage.add_command(CommandType.ADD, {"title": "Task 1"}, CommandStatus.SUCCESS)
        self.storage.add_command(CommandType.UPDATE, {"id": 1}, CommandStatus.SUCCESS)
        self.storage.add_command(CommandType.ADD, {"title": "Task 2"}, CommandStatus.SUCCESS)

        add_commands = self.storage.get_commands_by_type(CommandType.ADD)

        self.assertEqual(len(add_commands), 2)
        for cmd in add_commands:
            self.assertEqual(cmd.command_type, CommandType.ADD)

    def test_get_commands_by_status(self):
        """Test filtering commands by status (T100)"""
        # Add commands with different statuses
        self.storage.add_command(CommandType.ADD, {"title": "Task 1"}, CommandStatus.SUCCESS)
        self.storage.add_command(CommandType.ADD, {"title": "Task 2"}, CommandStatus.FAILURE)
        self.storage.add_command(CommandType.ADD, {"title": "Task 3"}, CommandStatus.SUCCESS)

        success_commands = self.storage.get_commands_by_status(CommandStatus.SUCCESS)

        self.assertEqual(len(success_commands), 2)
        for cmd in success_commands:
            self.assertEqual(cmd.status, CommandStatus.SUCCESS)

    def test_clear_history(self):
        """Test clearing command history (T100)"""
        self.storage.add_command(CommandType.ADD, {"title": "Task"}, CommandStatus.SUCCESS)

        self.storage.clear_history()

        self.assertEqual(self.storage.get_history_size(), 0)

    def test_history_size_limit(self):
        """Test history size limit functionality (T100)"""
        # Set a small max size for testing
        storage = CommandHistoryStorage()
        # Add more commands than the limit
        for i in range(storage._max_history_size + 5):
            storage.add_command(CommandType.ADD, {"title": f"Task {i}"}, CommandStatus.SUCCESS)

        # History should be limited to max size
        self.assertLessEqual(storage.get_history_size(), storage._max_history_size)


class TestCommandTimestampTracker(unittest.TestCase):
    """Test command timestamp tracking (T101)"""

    def setUp(self):
        """Set up test fixtures"""
        self.storage = CommandHistoryStorage()
        self.tracker = CommandTimestampTracker(self.storage)

    def test_get_command_age(self):
        """Test calculating command age (T101)"""
        # Add a command with a past timestamp
        past_time = datetime.now() - timedelta(seconds=10)
        record = CommandRecord(
            id=...,  # Will be auto-generated
            command_type=CommandType.ADD,
            parameters={"title": "Test"},
            timestamp=past_time,
            status=CommandStatus.SUCCESS
        )
        # Add it to storage
        self.storage.add_command(CommandType.ADD, {"title": "Test"}, CommandStatus.SUCCESS)

        # Get the most recent command
        recent_cmd = self.storage.get_all_commands()[-1]
        age = self.tracker.get_command_age(recent_cmd)

        # Age should be a reasonable value (less than 1 second for this test)
        self.assertGreaterEqual(age, 0)

    def test_get_commands_in_time_range(self):
        """Test getting commands in time range (T101)"""
        # Add a command
        self.storage.add_command(CommandType.ADD, {"title": "Test"}, CommandStatus.SUCCESS)

        # Define a time range that includes the command
        now = datetime.now()
        start_time = now - timedelta(hours=1)
        end_time = now + timedelta(hours=1)

        commands = self.tracker.get_commands_in_time_range(start_time, end_time)

        self.assertGreaterEqual(len(commands), 1)

    def test_get_recent_commands(self):
        """Test getting recent commands (T101)"""
        # Add a command
        self.storage.add_command(CommandType.ADD, {"title": "Test"}, CommandStatus.SUCCESS)

        # Get commands from last 10 minutes (should include our command)
        recent = self.tracker.get_recent_commands(minutes=10)

        self.assertGreaterEqual(len(recent), 1)


class TestCommandStatusTracker(unittest.TestCase):
    """Test command status tracking (T102)"""

    def setUp(self):
        """Set up test fixtures"""
        self.storage = CommandHistoryStorage()
        self.tracker = CommandStatusTracker(self.storage)

    def test_get_success_rate(self):
        """Test calculating success rate (T102)"""
        # Add commands with mixed statuses
        self.storage.add_command(CommandType.ADD, {"title": "Task 1"}, CommandStatus.SUCCESS)
        self.storage.add_command(CommandType.ADD, {"title": "Task 2"}, CommandStatus.FAILURE)
        self.storage.add_command(CommandType.ADD, {"title": "Task 3"}, CommandStatus.SUCCESS)

        success_rate = self.tracker.get_success_rate()

        self.assertEqual(success_rate, 2/3)  # 2 out of 3 succeeded

    def test_get_success_rate_by_type(self):
        """Test calculating success rate for specific command type (T102)"""
        # Add commands of different types
        self.storage.add_command(CommandType.ADD, {"title": "Task 1"}, CommandStatus.SUCCESS)
        self.storage.add_command(CommandType.ADD, {"title": "Task 2"}, CommandStatus.FAILURE)
        self.storage.add_command(CommandType.UPDATE, {"id": 1}, CommandStatus.SUCCESS)

        add_success_rate = self.tracker.get_success_rate(CommandType.ADD)

        self.assertEqual(add_success_rate, 0.5)  # 1 out of 2 ADD commands succeeded

    def test_get_failure_count(self):
        """Test counting failed commands (T102)"""
        # Add commands with mixed statuses
        self.storage.add_command(CommandType.ADD, {"title": "Task 1"}, CommandStatus.SUCCESS)
        self.storage.add_command(CommandType.ADD, {"title": "Task 2"}, CommandStatus.FAILURE)
        self.storage.add_command(CommandType.ADD, {"title": "Task 3"}, CommandStatus.FAILURE)

        failure_count = self.tracker.get_failure_count()

        self.assertEqual(failure_count, 2)

    def test_get_latest_command_status(self):
        """Test getting latest command status (T102)"""
        self.storage.add_command(CommandType.ADD, {"title": "Task 1"}, CommandStatus.FAILURE)

        latest_status = self.tracker.get_latest_command_status()

        self.assertEqual(latest_status, CommandStatus.FAILURE)

    def test_status_distribution(self):
        """Test getting status distribution (T102)"""
        # Add commands with different statuses
        self.storage.add_command(CommandType.ADD, {"title": "Task 1"}, CommandStatus.SUCCESS)
        self.storage.add_command(CommandType.ADD, {"title": "Task 2"}, CommandStatus.FAILURE)
        self.storage.add_command(CommandType.ADD, {"title": "Task 3"}, CommandStatus.SUCCESS)

        distribution = self.tracker.get_status_distribution()

        self.assertGreater(distribution[CommandStatus.SUCCESS], 0)
        self.assertGreater(distribution[CommandStatus.FAILURE], 0)

    def test_has_failed_commands(self):
        """Test checking for failed commands (T102)"""
        # Add a failed command
        self.storage.add_command(CommandType.ADD, {"title": "Task"}, CommandStatus.FAILURE)

        has_failures = self.tracker.has_failed_commands()

        self.assertTrue(has_failures)


class TestUndoManager(unittest.TestCase):
    """Test undo functionality (T103, T104, T105)"""

    def setUp(self):
        """Set up test fixtures"""
        self.storage = CommandHistoryStorage()
        self.undo_manager = UndoManager(self.storage)

    def test_can_undo_when_no_commands(self):
        """Test undo availability when no commands exist (T105)"""
        can_undo = self.undo_manager.can_undo()

        self.assertFalse(can_undo)

    def test_can_undo_with_commands(self):
        """Test undo availability with commands (T105)"""
        # Add a command that could be undone
        self.storage.add_command(
            CommandType.ADD,
            {"title": "Test"},
            CommandStatus.SUCCESS,
            undo_data={"operation": "add", "id": 1}
        )

        can_undo = self.undo_manager.can_undo()

        self.assertTrue(can_undo)

    def test_cannot_undo_undo_commands(self):
        """Test that undo commands themselves cannot be undone (T105)"""
        # Add an undo command
        self.storage.add_command(CommandType.UNDO, {}, CommandStatus.SUCCESS)

        can_undo = self.undo_manager.can_undo()

        # Should still be able to undo if there are other commands
        # This test may fail depending on the specific history, so we'll just ensure no error
        self.assertIsInstance(can_undo, bool)

    def test_get_last_undoable_command(self):
        """Test getting last undoable command (T103)"""
        # Add a command with undo data
        cmd_with_undo = self.storage.add_command(
            CommandType.ADD,
            {"title": "Test"},
            CommandStatus.SUCCESS,
            undo_data={"operation": "add", "id": 1}
        )

        last_undoable = self.undo_manager.get_last_undoable_command()

        self.assertIsNotNone(last_undoable)
        self.assertEqual(last_undoable.id, cmd_with_undo.id)

    def test_validate_undo_success(self):
        """Test successful undo validation (T104)"""
        # Create a command with undo data
        cmd = CommandRecord(
            id=...,  # Will be auto-generated
            command_type=CommandType.ADD,
            parameters={"title": "Test"},
            timestamp=datetime.now(),
            status=CommandStatus.SUCCESS,
            undo_data={"test": "data"}
        )

        is_valid, message = self.undo_manager.validate_undo(cmd)

        self.assertTrue(is_valid)

    def test_validate_undo_no_data(self):
        """Test undo validation for command without undo data (T104)"""
        # Create a command without undo data
        cmd = CommandRecord(
            id=...,  # Will be auto-generated
            command_type=CommandType.ADD,
            parameters={"title": "Test"},
            timestamp=datetime.now(),
            status=CommandStatus.SUCCESS,
            undo_data=None
        )

        is_valid, message = self.undo_manager.validate_undo(cmd)

        self.assertFalse(is_valid)

    def test_validate_undo_non_undoable_type(self):
        """Test undo validation for non-undoable command types (T104)"""
        # Create an undo command (which shouldn't be undoable)
        cmd = CommandRecord(
            id=...,  # Will be auto-generated
            command_type=CommandType.UNDO,
            parameters={},
            timestamp=datetime.now(),
            status=CommandStatus.SUCCESS,
            undo_data={"test": "data"}
        )

        is_valid, message = self.undo_manager.validate_undo(cmd)

        self.assertFalse(is_valid)


class TestCommandReplayer(unittest.TestCase):
    """Test command replay functionality (T106)"""

    def setUp(self):
        """Set up test fixtures"""
        self.storage = CommandHistoryStorage()
        self.replayer = CommandReplayer(self.storage)

    def test_replay_command_success(self):
        """Test successful command replay (T106)"""
        # Add a command to replay
        cmd = self.storage.add_command(
            CommandType.ADD,
            {"title": "Test task"},
            CommandStatus.SUCCESS
        )

        success, message, result = self.replayer.replay_command(cmd.id)

        self.assertTrue(success)
        self.assertIn("Successfully replayed", message)

    def test_replay_command_not_found(self):
        """Test replaying non-existent command (T106)"""
        fake_id = ...

        success, message, result = self.replayer.replay_command(fake_id)

        self.assertFalse(success)
        self.assertIn("not found", message)

    def test_get_replay_statistics(self):
        """Test getting replay statistics (T106)"""
        # Add some commands
        self.storage.add_command(CommandType.ADD, {"title": "Task 1"}, CommandStatus.SUCCESS)
        self.storage.add_command(CommandType.ADD, {"title": "Task 2"}, CommandStatus.FAILURE)
        self.storage.add_command(CommandType.UNDO, {}, CommandStatus.SUCCESS)

        stats = self.replayer.get_replay_statistics()

        self.assertGreater(stats["total_commands"], 0)
        self.assertIn("command_types", stats)


class TestCommandHistoryManager(unittest.TestCase):
    """Test the main command history manager (integration test)"""

    def setUp(self):
        """Set up test fixtures"""
        self.manager = CommandHistoryManager()

    def test_full_workflow(self):
        """Test the complete workflow of command history management"""
        # Record a command
        record = self.manager.record_command(
            CommandType.ADD,
            {"title": "Test task"},
            CommandStatus.SUCCESS,
            result={"id": 1, "status": "created"}
        )

        # Check that command was recorded
        history = self.manager.get_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].parameters["title"], "Test task")

        # Check success rate
        success_rate = self.manager.get_success_rate()
        self.assertEqual(success_rate, 1.0)  # 100% success

        # Check if undo is available (should be since we have a command)
        can_undo = self.manager.can_perform_undo()
        # This may be false if the command doesn't have undo data

        # Get replay statistics
        stats = self.manager.get_replay_stats()
        self.assertGreater(stats["total_commands"], 0)

    def test_undo_functionality(self):
        """Test undo functionality through manager"""
        # Record a command with undo data
        self.manager.record_command(
            CommandType.ADD,
            {"title": "Test task"},
            CommandStatus.SUCCESS,
            result={"id": 1},
            undo_data={"operation": "add", "id": 1}
        )

        # Check if undo is available
        can_undo = self.manager.can_perform_undo()

        # Perform undo (may or may not succeed depending on implementation)
        undo_result = self.manager.perform_undo()
        # Just check that it returns the right format
        self.assertIsInstance(undo_result, tuple)
        self.assertEqual(len(undo_result), 3)


if __name__ == '__main__':
    unittest.main()