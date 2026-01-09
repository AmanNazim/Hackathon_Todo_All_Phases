"""
Tests for Error Handling & Recovery System Components
Testing the Error Handling & Recovery tasks: T160-T166
"""
import unittest
import time
from datetime import datetime
from src.error_handling.error_handler import (
    ErrorHandler,
    ErrorRecoveryManager,
    InvalidCommandHandler,
    AmbiguousCommandHandler,
    ConfirmationFailureHandler,
    UndoFailureHandler,
    SafeRecoveryBehavior,
    GracefulDegradation,
    DataIntegrityManager,
    ErrorType,
    ErrorSeverity,
    ErrorInfo
)


class TestDataIntegrityManager(unittest.TestCase):
    """Test data integrity manager functionality (T166)"""

    def setUp(self):
        """Set up test fixtures"""
        self.integrity_manager = DataIntegrityManager()

    def test_register_and_verify_integrity(self):
        """Test registering and verifying data integrity checks (T166)"""
        # Register a simple check function
        def mock_check():
            return True  # Simulate valid integrity

        self.integrity_manager.register_integrity_check("mock_check", mock_check)

        is_valid, failed_checks = self.integrity_manager.verify_integrity()
        self.assertTrue(is_valid)
        self.assertEqual(len(failed_checks), 0)

    def test_verify_integrity_with_failure(self):
        """Test integrity verification with failing checks (T166)"""
        def failing_check():
            return False  # Simulate failing integrity

        self.integrity_manager.register_integrity_check("failing_check", failing_check)

        is_valid, failed_checks = self.integrity_manager.verify_integrity()
        self.assertFalse(is_valid)
        self.assertIn("failing_check", failed_checks)

    def test_repair_integrity(self):
        """Test data integrity repair functionality (T166)"""
        result = self.integrity_manager.repair_integrity()
        self.assertTrue(result)


class TestInvalidCommandHandler(unittest.TestCase):
    """Test invalid command handling (T160)"""

    def setUp(self):
        """Set up test fixtures"""
        self.handler = InvalidCommandHandler()

    def test_suggest_alternatives(self):
        """Test suggesting alternatives for invalid commands (T160)"""
        suggestions = self.handler.suggest_alternatives("addd")  # Typo for "add"
        # Should suggest "add" as a similar command
        self.assertIsInstance(suggestions, list)

    def test_handle_invalid_command(self):
        """Test handling invalid command with suggestions (T160)"""
        success, message, suggestions = self.handler.handle_invalid_command("invalid_command")

        self.assertFalse(success)
        self.assertIn("invalid_command", message)
        self.assertIsInstance(suggestions, list)

    def test_performance_within_50ms(self):
        """Test that invalid command handling performs within 50ms (T160)"""
        start_time = time.time()
        success, message, suggestions = self.handler.handle_invalid_command("test_cmd")
        elapsed_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        self.assertLess(elapsed_time, 50, f"Invalid command handling took {elapsed_time}ms, exceeding 50ms limit")


class TestAmbiguousCommandHandler(unittest.TestCase):
    """Test ambiguous command disambiguation (T161)"""

    def setUp(self):
        """Set up test fixtures"""
        self.handler = AmbiguousCommandHandler()

    def test_resolve_ambiguity_with_options(self):
        """Test resolving ambiguous command with multiple options (T161)"""
        interpretations = ["add task", "edit task", "show tasks"]
        success, message, selected = self.handler.resolve_ambiguity("task", interpretations)

        self.assertFalse(success)  # Should return false to prompt user
        self.assertIn("Ambiguous command", message)
        self.assertIsNone(selected)

    def test_parse_user_choice_valid(self):
        """Test parsing valid user choice from disambiguation (T161)"""
        interpretations = ["add task", "edit task", "show tasks"]
        success, message, selected = self.handler.parse_user_choice("1", interpretations)

        self.assertTrue(success)
        self.assertIsNotNone(selected)
        self.assertEqual(selected, "add task")

    def test_parse_user_choice_invalid(self):
        """Test parsing invalid user choice (T161)"""
        interpretations = ["add task", "edit task"]
        success, message, selected = self.handler.parse_user_choice("5", interpretations)

        self.assertFalse(success)
        self.assertIn("Invalid choice", message)
        self.assertIsNone(selected)

    def test_parse_user_choice_cancel(self):
        """Test parsing cancel command (T161)"""
        interpretations = ["add task", "edit task"]
        success, message, selected = self.handler.parse_user_choice("cancel", interpretations)

        self.assertFalse(success)
        self.assertIn("cancelled", message.lower())


class TestConfirmationFailureHandler(unittest.TestCase):
    """Test confirmation failure handling (T162)"""

    def setUp(self):
        """Set up test fixtures"""
        self.handler = ConfirmationFailureHandler()

    def test_handle_confirmation_failure(self):
        """Test handling confirmation failure (T162)"""
        success, message = self.handler.handle_confirmation_failure("delete_task", "User declined")

        self.assertFalse(success)
        self.assertIn("cancelled", message.lower())
        self.assertIn("without making any changes", message.lower())

    def test_restore_previous_state(self):
        """Test restoring previous state after confirmation failure (T162)"""
        mock_state = {"tasks": [1, 2, 3]}
        result = self.handler.restore_previous_state(mock_state)

        self.assertTrue(result)


class TestUndoFailureHandler(unittest.TestCase):
    """Test undo failure handling (T163)"""

    def setUp(self):
        """Set up test fixtures"""
        self.handler = UndoFailureHandler()

    def test_handle_undo_failure(self):
        """Test handling undo failure (T163)"""
        success, message = self.handler.handle_undo_failure("Cannot undo completed task", "complete_task")

        self.assertFalse(success)
        self.assertIn("cannot undo", message.lower())
        self.assertIn("complete_task", message)

    def test_preserve_and_restore_state(self):
        """Test preserving and restoring state during undo failure (T163)"""
        mock_state = {"previous_state": "backup"}
        self.handler.preserve_state_before_undo("test_op", mock_state)

        result = self.handler.restore_state_after_undo_failure("test_op")
        self.assertTrue(result)

        # Try to restore non-existent state
        result = self.handler.restore_state_after_undo_failure("nonexistent_op")
        self.assertFalse(result)


class TestSafeRecoveryBehavior(unittest.TestCase):
    """Test safe recovery behavior (T164)"""

    def setUp(self):
        """Set up test fixtures"""
        self.integrity_manager = DataIntegrityManager()
        self.recovery = SafeRecoveryBehavior(self.integrity_manager)

    def test_safe_recovery_from_error(self):
        """Test safe recovery from error condition (T164)"""
        error_info = ErrorInfo(
            error_type=ErrorType.SYSTEM_ERROR,
            message="Test error for recovery",
            severity=ErrorSeverity.HIGH,
            timestamp=datetime.now()
        )

        success, message = self.recovery.safe_recovery_from_error(error_info)

        self.assertTrue(success)
        self.assertIn("safe recovery", message.lower())

    def test_validate_safe_state(self):
        """Test validating safe state (T164)"""
        success, message = self.recovery.validate_safe_state()

        self.assertTrue(success)
        self.assertIn("safe state", message.lower())


class TestGracefulDegradation(unittest.TestCase):
    """Test graceful degradation functionality (T165)"""

    def setUp(self):
        """Set up test fixtures"""
        self.degradation = GracefulDegradation()

    def test_activate_degraded_mode(self):
        """Test activating degraded mode (T165)"""
        message = self.degradation.activate_degraded_mode("undo_feature", "Internal error")

        self.assertIn("undo_feature", message)
        self.assertIn("temporarily unavailable", message.lower())

    def test_feature_degraded_status(self):
        """Test checking if feature is degraded (T165)"""
        # Feature should not be degraded initially
        self.assertFalse(self.degradation.is_feature_degraded("test_feature"))

        # Activate degradation
        self.degradation.activate_degraded_mode("test_feature", "error")

        # Now it should be degraded
        self.assertTrue(self.degradation.is_feature_degraded("test_feature"))

    def test_get_available_features(self):
        """Test getting available features (T165)"""
        all_features = ["feature1", "feature2", "feature3"]

        # Initially all should be available
        available = self.degradation.get_available_features(all_features)
        self.assertEqual(len(available), 3)

        # Activate degradation for one feature
        self.degradation.activate_degraded_mode("feature2", "error")

        # Should have one less available
        available = self.degradation.get_available_features(all_features)
        self.assertEqual(len(available), 2)
        self.assertNotIn("feature2", available)

    def test_restore_feature(self):
        """Test restoring a feature from degraded mode (T165)"""
        # Activate degradation
        self.degradation.activate_degraded_mode("test_feature", "error")
        self.assertTrue(self.degradation.is_feature_degraded("test_feature"))

        # Restore the feature
        result = self.degradation.restore_feature("test_feature")
        self.assertTrue(result)
        self.assertFalse(self.degradation.is_feature_degraded("test_feature"))


class TestErrorHandler(unittest.TestCase):
    """Test main error handler functionality (T160-T166)"""

    def setUp(self):
        """Set up test fixtures"""
        self.error_handler = ErrorHandler()

    def test_log_error(self):
        """Test error logging functionality"""
        error_info = ErrorInfo(
            error_type=ErrorType.INVALID_COMMAND,
            message="Test error message",
            severity=ErrorSeverity.MEDIUM,
            timestamp=datetime.now()
        )

        self.error_handler.log_error(error_info)

        stats = self.error_handler.get_error_statistics()
        self.assertEqual(stats["total_errors"], 1)
        self.assertIn("invalid_command", stats["by_type"])

    def test_handle_invalid_command(self):
        """Test handling invalid command (T160)"""
        success, message, suggestions = self.error_handler.handle_invalid_command("bad_cmd")

        self.assertFalse(success)
        self.assertIn("bad_cmd", message)
        self.assertIsInstance(suggestions, list)

    def test_handle_ambiguous_command(self):
        """Test handling ambiguous command (T161)"""
        interpretations = ["option1", "option2"]
        success, message, selected = self.error_handler.handle_ambiguous_command("ambiguous", interpretations)

        self.assertFalse(success)
        self.assertIn("Ambiguous command", message)

    def test_handle_confirmation_failure(self):
        """Test handling confirmation failure (T162)"""
        success, message = self.error_handler.handle_confirmation_failure("delete_op", "User denied")

        self.assertFalse(success)
        self.assertIn("cancelled", message.lower())

    def test_handle_undo_failure(self):
        """Test handling undo failure (T163)"""
        success, message = self.error_handler.handle_undo_failure("Cannot undo", "complete_task")

        self.assertFalse(success)
        self.assertIn("cannot undo", message.lower())

    def test_handle_system_error(self):
        """Test handling system error (T164)"""
        try:
            raise ValueError("Test system error")
        except ValueError as e:
            success, message = self.error_handler.handle_system_error(e, "test_context")

        self.assertFalse(success)
        self.assertIn("error occurred", message.lower())

    def test_activate_graceful_degradation(self):
        """Test activating graceful degradation (T165)"""
        message = self.error_handler.activate_graceful_degradation("test_feature", "Connection failed")

        self.assertIn("test_feature", message)
        self.assertIn("temporarily unavailable", message.lower())

    def test_maintain_data_integrity(self):
        """Test maintaining data integrity (T166)"""
        success, message = self.error_handler.maintain_data_integrity()

        self.assertTrue(success)
        self.assertIn("integrity", message.lower())

    def test_get_error_statistics(self):
        """Test getting error statistics (T160-T166)"""
        stats = self.error_handler.get_error_statistics()

        self.assertIn("total_errors", stats)
        self.assertIn("by_type", stats)
        self.assertIn("by_severity", stats)


class TestErrorRecoveryManager(unittest.TestCase):
    """Test error recovery manager integration (T160-T166)"""

    def setUp(self):
        """Set up test fixtures"""
        self.manager = ErrorRecoveryManager()

    def test_execute_with_error_handling_success(self):
        """Test executing operation with error handling (success case)"""
        def successful_operation(x, y):
            return x + y

        success, message, result = self.manager.execute_with_error_handling(successful_operation, 2, 3)

        self.assertTrue(success)
        self.assertEqual(result, 5)

    def test_execute_with_error_handling_failure(self):
        """Test executing operation with error handling (failure case)"""
        def failing_operation():
            raise ValueError("Test error")

        success, message, result = self.manager.execute_with_error_handling(failing_operation)

        self.assertFalse(success)
        self.assertIn("error occurred", message.lower())

    def test_register_integrity_check(self):
        """Test registering integrity check (T166)"""
        def mock_check():
            return True

        self.manager.register_integrity_check("test_check", mock_check)

        # Verify it was registered by attempting validation
        success, message = self.manager.validate_safe_state()
        self.assertTrue(success)

    def test_validate_safe_state(self):
        """Test validating safe state (T164)"""
        success, message = self.manager.validate_safe_state()

        self.assertTrue(success)
        self.assertIn("safe", message.lower())

    def test_feature_availability(self):
        """Test checking feature availability (T165)"""
        # Initially should be available
        self.assertTrue(self.manager.is_feature_available("test_feature"))

        # Activate degradation
        self.manager.handler.activate_graceful_degradation("test_feature", "error")

        # Should now be unavailable
        self.assertFalse(self.manager.is_feature_available("test_feature"))

    def test_get_error_summary(self):
        """Test getting error summary (T160-T166)"""
        summary = self.manager.get_error_summary()

        self.assertIn("total_errors", summary)
        self.assertIn("by_type", summary)
        self.assertIn("by_severity", summary)


class TestErrorHandlingIntegration(unittest.TestCase):
    """Test error handling integration scenarios (T160-T166)"""

    def setUp(self):
        """Set up test fixtures"""
        self.manager = ErrorRecoveryManager()

    def test_full_error_handling_workflow(self):
        """Test complete error handling workflow (T160-T166)"""
        # 1. Test invalid command handling
        success, message, suggestions = self.manager.handler.handle_invalid_command("unknown_cmd")
        self.assertFalse(success)

        # 2. Test ambiguous command handling
        success, message, selected = self.manager.handler.handle_ambiguous_command("task", ["add", "edit"])
        self.assertFalse(success)

        # 3. Test confirmation failure handling
        success, message = self.manager.handler.handle_confirmation_failure("delete", "denied")
        self.assertFalse(success)

        # 4. Test undo failure handling
        success, message = self.manager.handler.handle_undo_failure("cannot", "op")
        self.assertFalse(success)

        # 5. Test system error handling
        try:
            raise RuntimeError("System error")
        except RuntimeError as e:
            success, message = self.manager.handler.handle_system_error(e, "context")
            self.assertFalse(success)

        # 6. Test graceful degradation
        degradation_msg = self.manager.handler.activate_graceful_degradation("feature", "error")
        self.assertIn("unavailable", degradation_msg.lower())

        # 7. Test data integrity maintenance
        integrity_success, integrity_msg = self.manager.handler.maintain_data_integrity()
        self.assertTrue(integrity_success)

        # 8. Check that errors were logged
        summary = self.manager.get_error_summary()
        self.assertGreater(summary["total_errors"], 0)

    def test_error_recovery_validation(self):
        """Test error recovery validation (T164)"""
        # Simulate an error condition
        try:
            raise ValueError("Recovery test")
        except ValueError as e:
            success, message = self.manager.handler.handle_system_error(e, "recovery_test")

        # Validate safe state after recovery
        safe_success, safe_message = self.manager.validate_safe_state()
        self.assertTrue(safe_success)

    def test_performance_under_error_conditions(self):
        """Test performance under error conditions (T160)"""
        # Test that error handling doesn't exceed performance limits
        start_time = time.time()
        for i in range(10):  # Test multiple error operations
            self.manager.handler.handle_invalid_command(f"bad_cmd_{i}")
        elapsed_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        # Total time for 10 operations should be reasonable
        self.assertLess(elapsed_time, 500)  # 500ms for 10 operations (50ms average)

    def test_data_integrity_during_errors(self):
        """Test data integrity maintained during errors (T166)"""
        # Register a mock integrity check
        def mock_integrity_check():
            return True

        self.manager.register_integrity_check("mock_check", mock_integrity_check)

        # Simulate various errors
        self.manager.handler.handle_invalid_command("bad_cmd")
        self.manager.handler.handle_confirmation_failure("op", "reason")

        # Check that integrity is still maintained
        integrity_success, integrity_msg = self.manager.handler.maintain_data_integrity()
        self.assertTrue(integrity_success)

    def test_graceful_degradation_effectiveness(self):
        """Test that graceful degradation works effectively (T165)"""
        # Activate degradation for a feature
        degradation_msg = self.manager.handler.activate_graceful_degradation("undo", "service_down")
        self.assertIn("temporarily unavailable", degradation_msg.lower())

        # Verify the feature is marked as degraded
        self.assertFalse(self.manager.is_feature_available("undo"))

        # Simulate using other non-degraded features (they should work)
        def working_operation():
            return "success"

        success, message, result = self.manager.execute_with_error_handling(working_operation)
        self.assertTrue(success)
        self.assertEqual(result, "success")


if __name__ == '__main__':
    unittest.main()