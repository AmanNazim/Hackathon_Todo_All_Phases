"""
Tests for CLI State Machine Components
Testing the CLI State Machine tasks: T060-T065
"""
import unittest
from src.state_machine.cli_state_machine import CLIState, CLIStateMachine, StateHandler


class TestCLIStateEnum(unittest.TestCase):
    """Test the CLI state enumeration (T060)"""

    def test_state_enum_values(self):
        """Test that all state values are defined correctly (T060)"""
        self.assertEqual(CLIState.MAIN_MENU.value, "MAIN_MENU")
        self.assertEqual(CLIState.ADDING_TASK.value, "ADDING_TASK")
        self.assertEqual(CLIState.UPDATING_TASK.value, "UPDATING_TASK")
        self.assertEqual(CLIState.DELETING_TASK.value, "DELETING_TASK")
        self.assertEqual(CLIState.CONFIRMATION_DIALOG.value, "CONFIRMATION_DIALOG")
        self.assertEqual(CLIState.EXITING.value, "EXITING")

    def test_state_enum_hashability(self):
        """Test that states are hashable for use in dictionaries (T060)"""
        state_dict = {CLIState.MAIN_MENU: "main", CLIState.ADDING_TASK: "adding"}
        self.assertIn(CLIState.MAIN_MENU, state_dict)
        self.assertEqual(state_dict[CLIState.MAIN_MENU], "main")


class TestCLIStateMachine(unittest.TestCase):
    """Test the CLI state machine (T061, T062, T064, T065)"""

    def setUp(self):
        """Set up test fixtures"""
        self.state_machine = CLIStateMachine()

    def test_initial_state_is_main_menu(self):
        """Test that the state machine starts in MAIN_MENU state (T061)"""
        self.assertEqual(self.state_machine.current_state, CLIState.MAIN_MENU)

    def test_state_transitions_are_valid(self):
        """Test that valid state transitions work (T062)"""
        # Test transition from MAIN_MENU to ADDING_TASK
        result = self.state_machine.transition_to(CLIState.ADDING_TASK)
        self.assertTrue(result)
        self.assertEqual(self.state_machine.current_state, CLIState.ADDING_TASK)

        # Test transition from ADDING_TASK back to MAIN_MENU
        result = self.state_machine.transition_to(CLIState.MAIN_MENU)
        self.assertTrue(result)
        self.assertEqual(self.state_machine.current_state, CLIState.MAIN_MENU)

    def test_invalid_state_transitions_are_rejected(self):
        """Test that invalid state transitions are properly rejected (T064)"""
        # Attempt to transition from ADDING_TASK to UPDATING_TASK (should be invalid)
        self.state_machine.transition_to(CLIState.ADDING_TASK)  # First go to ADDING_TASK
        result = self.state_machine.transition_to(CLIState.UPDATING_TASK)  # Invalid transition
        self.assertFalse(result)
        self.assertEqual(self.state_machine.current_state, CLIState.ADDING_TASK)  # Should remain in ADDING_TASK

    def test_previous_state_tracking(self):
        """Test that previous state is tracked correctly (T062)"""
        initial_state = self.state_machine.current_state
        self.assertIsNone(self.state_machine.previous_state)

        # Transition to another state
        self.state_machine.transition_to(CLIState.ADDING_TASK)
        self.assertEqual(self.state_machine.previous_state, initial_state)

    def test_state_data_persistence(self):
        """Test that state data persists across operations (T065)"""
        # Set some data
        self.state_machine.set_state_data("test_key", "test_value")

        # Verify data can be retrieved
        retrieved_value = self.state_machine.get_state_data("test_key")
        self.assertEqual(retrieved_value, "test_value")

        # Verify all data can be retrieved
        all_data = self.state_machine.get_state_data()
        self.assertIn("test_key", all_data)
        self.assertEqual(all_data["test_key"], "test_value")

    def test_state_data_update_multiple(self):
        """Test updating multiple state data items (T065)"""
        data_dict = {"key1": "value1", "key2": "value2", "key3": "value3"}
        self.state_machine.update_state_data(data_dict)

        # Verify all data was set
        self.assertEqual(self.state_machine.get_state_data("key1"), "value1")
        self.assertEqual(self.state_machine.get_state_data("key2"), "value2")
        self.assertEqual(self.state_machine.get_state_data("key3"), "value3")

    def test_clear_specific_state_data(self):
        """Test clearing specific state data keys (T065)"""
        # Set multiple data items
        self.state_machine.set_state_data("keep_this", "important")
        self.state_machine.set_state_data("remove_this", "temporary")
        self.state_machine.set_state_data("also_remove", "temp2")

        # Clear specific keys
        self.state_machine.clear_state_data(["remove_this", "also_remove"])

        # Verify only the specified keys were removed
        self.assertEqual(self.state_machine.get_state_data("keep_this"), "important")
        self.assertIsNone(self.state_machine.get_state_data("remove_this"))
        self.assertIsNone(self.state_machine.get_state_data("also_remove"))

    def test_state_snapshot_and_restore(self):
        """Test state snapshot and restore functionality (T065)"""
        # Set up some state
        self.state_machine.transition_to(CLIState.ADDING_TASK)
        self.state_machine.set_state_data("task_title", "Test Task")
        self.state_machine.set_state_data("task_desc", "Test Description")

        # Take a snapshot
        snapshot = self.state_machine.persist_state_snapshot()

        # Change state to something different
        self.state_machine.transition_to(CLIState.EXITING)
        self.state_machine.set_state_data("task_title", "Different Task")

        # Restore from snapshot
        result = self.state_machine.restore_from_snapshot(snapshot)
        self.assertTrue(result)

        # Verify state was restored
        self.assertEqual(self.state_machine.current_state, CLIState.ADDING_TASK)
        self.assertEqual(self.state_machine.get_state_data("task_title"), "Test Task")
        self.assertEqual(self.state_machine.get_state_data("task_desc"), "Test Description")

    def test_state_validation_for_operations(self):
        """Test state validation for specific operations (T064)"""
        # Test in MAIN_MENU state
        self.state_machine.transition_to(CLIState.MAIN_MENU)

        # Should be able to add task from MAIN_MENU
        valid, msg = self.state_machine.validate_state_for_operation("add_task")
        self.assertTrue(valid)

        # Should be able to list tasks from MAIN_MENU
        valid, msg = self.state_machine.validate_state_for_operation("list_tasks")
        self.assertTrue(valid)

        # Go to ADDING_TASK state
        self.state_machine.transition_to(CLIState.ADDING_TASK)

        # Should still be able to list tasks from ADDING_TASK
        valid, msg = self.state_machine.validate_state_for_operation("list_tasks")
        self.assertTrue(valid)

        # Should not be able to complete task from ADDING_TASK
        valid, msg = self.state_machine.validate_state_for_operation("complete_task")
        self.assertFalse(valid)

    def test_transition_history_logging(self):
        """Test that transitions are properly logged (T062)"""
        initial_count = len(self.state_machine.get_transition_history())

        # Perform a valid transition
        self.state_machine.transition_to(CLIState.ADDING_TASK)

        # Check that history was updated
        history = self.state_machine.get_transition_history()
        self.assertEqual(len(history), initial_count + 1)
        self.assertTrue(history[-1]['valid'])
        self.assertEqual(history[-1]['from'], CLIState.MAIN_MENU)
        self.assertEqual(history[-1]['to'], CLIState.ADDING_TASK)

        # Perform an invalid transition
        result = self.state_machine.transition_to(CLIState.EXITING)  # Invalid from ADDING_TASK
        self.assertFalse(result)

        # Check that invalid transition was also logged
        history = self.state_machine.get_transition_history()
        # The invalid transition should add another entry, so total should be initial + 2
        # (1 for the successful transition, 1 for the failed transition attempt)
        self.assertEqual(len(history), initial_count + 2)
        # The last entry should be the failed transition
        self.assertFalse(history[-1]['valid'])
        self.assertEqual(history[-1]['from'], CLIState.ADDING_TASK)
        self.assertEqual(history[-1]['to'], CLIState.EXITING)


class TestStateHandler(unittest.TestCase):
    """Test the state handlers (T063)"""

    def setUp(self):
        """Set up test fixtures"""
        self.state_machine = CLIStateMachine()
        self.state_handler = StateHandler(self.state_machine)

    def test_main_menu_handler(self):
        """Test the main menu state handler (T063)"""
        self.state_machine.transition_to(CLIState.MAIN_MENU)
        result = self.state_handler.handle_current_state()

        self.assertEqual(result['state'], CLIState.MAIN_MENU.value)
        self.assertEqual(result['action'], 'show_main_menu')
        self.assertIn('menu_options', result)
        self.assertGreater(len(result['menu_options']), 0)

    def test_adding_task_handler(self):
        """Test the adding task state handler (T063)"""
        self.state_machine.transition_to(CLIState.ADDING_TASK)
        result = self.state_handler.handle_current_state()

        self.assertEqual(result['state'], CLIState.ADDING_TASK.value)
        self.assertEqual(result['action'], 'collect_task_details')
        self.assertIn('prompt', result)
        self.assertIn('expected_input', result)

    def test_updating_task_handler(self):
        """Test the updating task state handler (T063)"""
        self.state_machine.transition_to(CLIState.UPDATING_TASK)
        result = self.state_handler.handle_current_state()

        self.assertEqual(result['state'], CLIState.UPDATING_TASK.value)
        self.assertEqual(result['action'], 'collect_update_details')
        self.assertIn('prompt', result)
        self.assertIn('expected_input', result)

    def test_deleting_task_handler(self):
        """Test the deleting task state handler (T063)"""
        self.state_machine.transition_to(CLIState.DELETING_TASK)
        result = self.state_handler.handle_current_state()

        self.assertEqual(result['state'], CLIState.DELETING_TASK.value)
        self.assertEqual(result['action'], 'confirm_deletion')
        self.assertIn('prompt', result)
        self.assertIn('expected_input', result)

    def test_confirmation_dialog_handler(self):
        """Test the confirmation dialog state handler (T063)"""
        self.state_machine.transition_to(CLIState.CONFIRMATION_DIALOG)
        result = self.state_handler.handle_current_state()

        self.assertEqual(result['state'], CLIState.CONFIRMATION_DIALOG.value)
        self.assertEqual(result['action'], 'await_confirmation')
        self.assertIn('prompt', result)
        self.assertIn('expected_input', result)

    def test_exiting_handler(self):
        """Test the exiting state handler (T063)"""
        self.state_machine.transition_to(CLIState.EXITING)
        result = self.state_handler.handle_current_state()

        self.assertEqual(result['state'], CLIState.EXITING.value)
        self.assertEqual(result['action'], 'perform_cleanup_and_exit')
        self.assertIn('cleanup_actions', result)

    def test_unknown_state_handler(self):
        """Test the unknown state handler (T063)"""
        # We can't easily create an unknown state, but we can test the error handling
        # by manually calling the handler with an invalid state
        result = self.state_handler.handle_unknown_state(CLIState.MAIN_MENU)

        self.assertEqual(result['state'], CLIState.MAIN_MENU.value)
        self.assertEqual(result['action'], 'unknown_state_error')
        self.assertIn('recovery_action', result)


if __name__ == '__main__':
    unittest.main()