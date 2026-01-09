"""
Tests for Exit Summary System Components
Testing the Exit Summary tasks: T150-T154
"""
import unittest
from datetime import datetime
from src.exit_summary.exit_summary import (
    ExitSummaryTracker,
    ExitSummaryDisplay,
    SessionStatistics
)


class TestExitSummaryTracker(unittest.TestCase):
    """Test exit summary tracker functionality (T150, T151, T152, T153)"""

    def setUp(self):
        """Set up test fixtures"""
        self.tracker = ExitSummaryTracker()

    def test_increment_tasks_created(self):
        """Test incrementing tasks created counter (T151)"""
        initial_count = self.tracker.get_current_statistics().total_tasks_created
        self.tracker.increment_tasks_created()
        new_count = self.tracker.get_current_statistics().total_tasks_created

        self.assertEqual(new_count, initial_count + 1)

    def test_increment_tasks_completed(self):
        """Test incrementing tasks completed counter (T152)"""
        initial_count = self.tracker.get_current_statistics().tasks_completed
        self.tracker.increment_tasks_completed()
        new_count = self.tracker.get_current_statistics().tasks_completed

        self.assertEqual(new_count, initial_count + 1)

    def test_increment_commands_executed(self):
        """Test incrementing commands executed counter (T153)"""
        initial_count = self.tracker.get_current_statistics().commands_executed
        self.tracker.increment_commands_executed()
        new_count = self.tracker.get_current_statistics().commands_executed

        self.assertEqual(new_count, initial_count + 1)

    def test_increment_tasks_deleted(self):
        """Test incrementing tasks deleted counter"""
        initial_count = self.tracker.get_current_statistics().tasks_deleted
        self.tracker.increment_tasks_deleted()
        new_count = self.tracker.get_current_statistics().tasks_deleted

        self.assertEqual(new_count, initial_count + 1)

    def test_increment_tasks_updated(self):
        """Test incrementing tasks updated counter"""
        initial_count = self.tracker.get_current_statistics().tasks_updated
        self.tracker.increment_tasks_updated()
        new_count = self.tracker.get_current_statistics().tasks_updated

        self.assertEqual(new_count, initial_count + 1)

    def test_increment_tasks_reopened(self):
        """Test incrementing tasks reopened counter"""
        initial_count = self.tracker.get_current_statistics().tasks_reopened
        self.tracker.increment_tasks_reopened()
        new_count = self.tracker.get_current_statistics().tasks_reopened

        self.assertEqual(new_count, initial_count + 1)

    def test_get_current_statistics(self):
        """Test getting current session statistics (T150)"""
        # Manipulate some counters
        self.tracker.increment_tasks_created()
        self.tracker.increment_tasks_completed()
        self.tracker.increment_commands_executed()

        stats = self.tracker.get_current_statistics()

        self.assertEqual(stats.total_tasks_created, 1)
        self.assertEqual(stats.tasks_completed, 1)
        self.assertEqual(stats.commands_executed, 1)
        self.assertIsNotNone(stats.session_start_time)

    def test_finalize_session(self):
        """Test finalizing session and calculating statistics (T154)"""
        # Manipulate some counters
        self.tracker.increment_tasks_created()
        self.tracker.increment_tasks_completed()
        self.tracker.increment_commands_executed()

        stats = self.tracker.finalize_session()

        self.assertEqual(stats.total_tasks_created, 1)
        self.assertEqual(stats.tasks_completed, 1)
        self.assertEqual(stats.commands_executed, 1)
        self.assertIsNotNone(stats.session_end_time)
        self.assertGreaterEqual(stats.session_duration_seconds, 0)

    def test_reset_counters(self):
        """Test resetting counters for new session"""
        # Set some values
        self.tracker.increment_tasks_created()
        self.tracker.increment_tasks_completed()
        self.tracker.increment_commands_executed()

        # Reset
        self.tracker.reset_counters()

        stats = self.tracker.get_current_statistics()
        self.assertEqual(stats.total_tasks_created, 0)
        self.assertEqual(stats.tasks_completed, 0)
        self.assertEqual(stats.commands_executed, 0)

    def test_session_duration_calculation(self):
        """Test session duration calculation (T150)"""
        # Allow some time to pass
        import time
        time.sleep(0.01)  # Sleep for 10ms

        stats = self.tracker.get_current_statistics()
        self.assertGreaterEqual(stats.session_duration_seconds, 0.01)


class TestExitSummaryDisplay(unittest.TestCase):
    """Test exit summary display functionality (T154)"""

    def setUp(self):
        """Set up test fixtures"""
        self.tracker = ExitSummaryTracker()
        self.display = ExitSummaryDisplay(self.tracker)

    def test_display_exit_summary(self):
        """Test displaying exit summary at application termination (T154)"""
        # Manipulate some counters
        self.display.register_task_creation()
        self.display.register_task_completion()
        self.display.register_command_execution()

        summary_text = self.display.display_exit_summary()

        # Check that the summary contains expected elements
        self.assertIn("SESSION SUMMARY", summary_text)
        self.assertIn("Tasks Created:", summary_text)
        self.assertIn("Tasks Completed:", summary_text)
        self.assertIn("Commands Executed:", summary_text)
        self.assertIn("Thank you for using CLI Todo App!", summary_text)

    def test_display_intermediate_summary(self):
        """Test displaying intermediate summary"""
        # Manipulate some counters
        self.display.register_task_creation()
        self.display.register_task_completion()

        summary_text = self.display.display_intermediate_summary()

        self.assertIn("SESSION SUMMARY", summary_text)
        self.assertIn("Tasks Created:                      1", summary_text)
        self.assertIn("Tasks Completed:                    1", summary_text)

    def test_register_command_execution(self):
        """Test registering command execution (T153)"""
        initial_count = self.tracker.get_current_statistics().commands_executed
        self.display.register_command_execution()
        new_count = self.tracker.get_current_statistics().commands_executed

        self.assertEqual(new_count, initial_count + 1)

    def test_register_task_creation(self):
        """Test registering task creation (T151)"""
        initial_count = self.tracker.get_current_statistics().total_tasks_created
        self.display.register_task_creation()
        new_count = self.tracker.get_current_statistics().total_tasks_created

        self.assertEqual(new_count, initial_count + 1)

    def test_register_task_completion(self):
        """Test registering task completion (T152)"""
        initial_count = self.tracker.get_current_statistics().tasks_completed
        self.display.register_task_completion()
        new_count = self.tracker.get_current_statistics().tasks_completed

        self.assertEqual(new_count, initial_count + 1)

    def test_register_task_deletion(self):
        """Test registering task deletion"""
        initial_count = self.tracker.get_current_statistics().tasks_deleted
        self.display.register_task_deletion()
        new_count = self.tracker.get_current_statistics().tasks_deleted

        self.assertEqual(new_count, initial_count + 1)

    def test_register_task_update(self):
        """Test registering task update"""
        initial_count = self.tracker.get_current_statistics().tasks_updated
        self.display.register_task_update()
        new_count = self.tracker.get_current_statistics().tasks_updated

        self.assertEqual(new_count, initial_count + 1)

    def test_register_task_reopen(self):
        """Test registering task reopen"""
        initial_count = self.tracker.get_current_statistics().tasks_reopened
        self.display.register_task_reopen()
        new_count = self.tracker.get_current_statistics().tasks_reopened

        self.assertEqual(new_count, initial_count + 1)


class TestSessionStatistics(unittest.TestCase):
    """Test session statistics functionality (T150)"""

    def test_get_session_duration_formatted(self):
        """Test formatted session duration (T150)"""
        stats = SessionStatistics()
        stats.session_duration_seconds = 3661  # 1 hour, 1 minute, 1 second

        formatted = stats.get_session_duration_formatted()
        self.assertIn("1h", formatted)
        self.assertIn("1m", formatted)
        self.assertIn("1s", formatted)

    def test_get_session_duration_formatted_minutes(self):
        """Test formatted session duration for minutes (T150)"""
        stats = SessionStatistics()
        stats.session_duration_seconds = 125  # 2 minutes, 5 seconds

        formatted = stats.get_session_duration_formatted()
        self.assertIn("2m", formatted)
        self.assertIn("5s", formatted)

    def test_get_session_duration_formatted_seconds(self):
        """Test formatted session duration for seconds (T150)"""
        stats = SessionStatistics()
        stats.session_duration_seconds = 45  # 45 seconds

        formatted = stats.get_session_duration_formatted()
        self.assertEqual(formatted, "45s")

    def test_get_session_duration_formatted_zero(self):
        """Test formatted session duration for zero (T150)"""
        stats = SessionStatistics()
        stats.session_duration_seconds = 0

        formatted = stats.get_session_duration_formatted()
        self.assertEqual(formatted, "0s")


class TestExitSummaryIntegration(unittest.TestCase):
    """Test exit summary integration scenarios (T150-T154)"""

    def setUp(self):
        """Set up test fixtures"""
        self.tracker = ExitSummaryTracker()
        self.display = ExitSummaryDisplay(self.tracker)

    def test_full_session_tracking_workflow(self):
        """Test complete session tracking workflow (T150-T154)"""
        # Simulate a full session with various activities
        for i in range(5):
            self.display.register_task_creation()

        for i in range(3):
            self.display.register_task_completion()

        for i in range(7):
            self.display.register_command_execution()

        for i in range(2):
            self.display.register_task_deletion()

        for i in range(4):
            self.display.register_task_update()

        # Get current statistics
        stats = self.tracker.get_current_statistics()
        self.assertEqual(stats.total_tasks_created, 5)
        self.assertEqual(stats.tasks_completed, 3)
        self.assertEqual(stats.commands_executed, 7)
        self.assertEqual(stats.tasks_deleted, 2)
        self.assertEqual(stats.tasks_updated, 4)

        # Finalize and display summary
        final_stats = self.tracker.finalize_session()
        summary_text = self.display.display_exit_summary()

        # Verify the summary contains the correct values
        self.assertIn("Tasks Created:                      5", summary_text)
        self.assertIn("Tasks Completed:                    3", summary_text)
        self.assertIn("Commands Executed:                  7", summary_text)
        self.assertIn("Tasks Deleted:                      2", summary_text)
        self.assertIn("Tasks Updated:                      4", summary_text)

    def test_accuracy_of_statistic_calculation(self):
        """Test accuracy of statistic calculation (T150)"""
        # Register exact numbers and verify accuracy
        expected_tasks_created = 10
        expected_tasks_completed = 7
        expected_commands_executed = 15

        for _ in range(expected_tasks_created):
            self.display.register_task_creation()

        for _ in range(expected_tasks_completed):
            self.display.register_task_completion()

        for _ in range(expected_commands_executed):
            self.display.register_command_execution()

        stats = self.tracker.get_current_statistics()
        self.assertEqual(stats.total_tasks_created, expected_tasks_created)
        self.assertEqual(stats.tasks_completed, expected_tasks_completed)
        self.assertEqual(stats.commands_executed, expected_commands_executed)

    def test_counter_reset_functionality(self):
        """Test counter reset functionality (T151)"""
        # Add some activity
        self.display.register_task_creation()
        self.display.register_task_completion()
        self.display.register_command_execution()

        # Verify counters are not zero
        stats_before = self.tracker.get_current_statistics()
        self.assertGreater(stats_before.total_tasks_created, 0)
        self.assertGreater(stats_before.tasks_completed, 0)
        self.assertGreater(stats_before.commands_executed, 0)

        # Reset counters
        self.tracker.reset_counters()

        # Verify counters are zero
        stats_after = self.tracker.get_current_statistics()
        self.assertEqual(stats_after.total_tasks_created, 0)
        self.assertEqual(stats_after.tasks_completed, 0)
        self.assertEqual(stats_after.commands_executed, 0)

    def test_multiple_sessions_simulation(self):
        """Test simulation of multiple sessions (T151)"""
        # First session
        self.display.register_task_creation()
        self.display.register_task_completion()
        self.display.register_command_execution()

        first_session_stats = self.tracker.finalize_session()
        self.assertEqual(first_session_stats.total_tasks_created, 1)
        self.assertEqual(first_session_stats.tasks_completed, 1)
        self.assertEqual(first_session_stats.commands_executed, 1)

        # Start new session
        self.tracker.reset_counters()

        # Second session
        for _ in range(3):
            self.display.register_task_creation()
        for _ in range(2):
            self.display.register_task_completion()

        second_session_stats = self.tracker.finalize_session()
        self.assertEqual(second_session_stats.total_tasks_created, 3)
        self.assertEqual(second_session_stats.tasks_completed, 2)
        self.assertEqual(second_session_stats.commands_executed, 0)  # Not incremented in second session


if __name__ == '__main__':
    unittest.main()