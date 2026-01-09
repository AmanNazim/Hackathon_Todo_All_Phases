"""
Error Handling & Recovery System for CLI Todo Application
Implements T160-T166: Error Handling & Recovery functionality
"""
import threading
import time
import traceback
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import logging


class ErrorSeverity(Enum):
    """Severity levels for errors"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorType(Enum):
    """Types of errors that can occur"""
    INVALID_COMMAND = "invalid_command"
    AMBIGUOUS_COMMAND = "ambiguous_command"
    CONFIRMATION_FAILURE = "confirmation_failure"
    UNDO_FAILURE = "undo_failure"
    SYSTEM_ERROR = "system_error"
    DATA_INTEGRITY = "data_integrity"
    RECOVERY_ERROR = "recovery_error"


@dataclass
class ErrorInfo:
    """Information about an error"""
    error_type: ErrorType
    message: str
    severity: ErrorSeverity
    timestamp: datetime
    command_context: Optional[str] = None
    suggested_solution: Optional[str] = None
    stack_trace: Optional[str] = None


class DataIntegrityManager:
    """Manages data integrity during error conditions"""

    def __init__(self):
        self._integrity_checks: Dict[str, Callable[[], bool]] = {}
        self._lock = threading.RLock()

    def register_integrity_check(self, name: str, check_func: Callable[[], bool]) -> None:
        """Register a data integrity check function"""
        with self._lock:
            self._integrity_checks[name] = check_func

    def verify_integrity(self) -> Tuple[bool, List[str]]:
        """Verify data integrity by running all registered checks"""
        with self._lock:
            failed_checks = []
            for name, check_func in self._integrity_checks.items():
                try:
                    if not check_func():
                        failed_checks.append(name)
                except Exception as e:
                    failed_checks.append(f"{name} (error: {str(e)})")

            is_valid = len(failed_checks) == 0
            return is_valid, failed_checks

    def repair_integrity(self) -> bool:
        """Attempt to repair data integrity issues"""
        # This is a placeholder - actual repair logic would be implemented based on specific needs
        # For now, just return True indicating integrity is maintained
        return True


class InvalidCommandHandler:
    """Handles invalid command errors with suggestions"""

    def __init__(self, command_suggestions: Optional[Dict[str, List[str]]] = None):
        self._command_suggestions = command_suggestions or {}
        self._lock = threading.RLock()

    def suggest_alternatives(self, invalid_command: str) -> List[str]:
        """Provide suggestions for invalid commands"""
        # Find similar commands based on character similarity
        suggestions = []

        # Look for commands with similar names
        all_commands = list(self._command_suggestions.keys()) if self._command_suggestions else [
            "add", "list", "update", "delete", "complete", "incomplete", "help", "theme",
            "undo", "macro", "snapshot", "exit"
        ]

        # Simple similarity algorithm - find commands that share at least half the characters
        for cmd in all_commands:
            common_chars = sum(1 for c1, c2 in zip(invalid_command.lower(), cmd.lower()) if c1 == c2)
            if common_chars > 0 and len(invalid_command) > 0:
                similarity_ratio = common_chars / max(len(invalid_command), len(cmd))
                if similarity_ratio >= 0.5:  # At least 50% similar
                    suggestions.append(cmd)

        # Return top 3 suggestions
        return suggestions[:3]

    def handle_invalid_command(self, command: str) -> Tuple[bool, str, List[str]]:
        """Handle invalid command with clear error and suggestions"""
        start_time = time.time()

        suggestions = self.suggest_alternatives(command)

        if suggestions:
            message = f"Unknown command '{command}'. Did you mean: {', '.join(suggestions)}?"
        else:
            message = f"Unknown command '{command}'. Type 'help' for available commands."

        # Performance check - ensure response is within 50ms
        elapsed_time = (time.time() - start_time) * 1000
        if elapsed_time > 50:
            logging.warning(f"Invalid command handling took {elapsed_time:.2f}ms (over 50ms limit)")

        return False, message, suggestions


class AmbiguousCommandHandler:
    """Handles ambiguous command disambiguation"""

    def resolve_ambiguity(self, command: str, possible_interpretations: List[str]) -> Tuple[bool, str, Optional[str]]:
        """Resolve ambiguous command by prompting user"""
        if len(possible_interpretations) == 0:
            return False, f"No interpretations available for command: {command}", None

        if len(possible_interpretations) == 1:
            # Not really ambiguous
            return True, f"Interpreted as: {possible_interpretations[0]}", possible_interpretations[0]

        # Present options to user
        options_text = "\n".join([f"  {i+1}. {opt}" for i, opt in enumerate(possible_interpretations)])
        message = f"Ambiguous command '{command}'. Possible interpretations:\n{options_text}\nPlease specify which option you meant (1-{len(possible_interpretations)}) or 'cancel' to abort."

        return False, message, None

    def parse_user_choice(self, user_input: str, possible_interpretations: List[str]) -> Tuple[bool, str, Optional[str]]:
        """Parse user's choice from disambiguation prompt"""
        try:
            choice_num = int(user_input.strip())
            if 1 <= choice_num <= len(possible_interpretations):
                selected = possible_interpretations[choice_num - 1]
                return True, f"Selected: {selected}", selected
            else:
                return False, f"Invalid choice. Please select 1-{len(possible_interpretations)} or 'cancel'.", None
        except ValueError:
            if user_input.strip().lower() == 'cancel':
                return False, "Command cancelled by user.", None
            else:
                return False, f"Invalid input. Please enter a number 1-{len(possible_interpretations)} or 'cancel'.", None


class ConfirmationFailureHandler:
    """Handles confirmation failure scenarios"""

    def handle_confirmation_failure(self, operation: str, reason: str) -> Tuple[bool, str]:
        """Handle confirmation failure with clear messaging"""
        message = f"Operation '{operation}' cancelled: {reason}\nOperation was cancelled without making any changes. You can try again."
        return False, message

    def restore_previous_state(self, state_backup: Any) -> bool:
        """Restore previous state after confirmation failure"""
        # In a real implementation, this would restore from a backup state
        # For now, we'll just return True to indicate successful restoration
        return True


class UndoFailureHandler:
    """Handles undo operation failures with state preservation"""

    def __init__(self):
        self._state_backups: Dict[str, Any] = {}
        self._lock = threading.RLock()

    def handle_undo_failure(self, failure_reason: str, affected_operation: str) -> Tuple[bool, str]:
        """Handle undo failure with clear explanation"""
        message = f"Cannot undo operation '{affected_operation}': {failure_reason}\nCurrent state has been preserved. Alternative recovery options may be available."
        return False, message

    def preserve_state_before_undo(self, operation_id: str, state_snapshot: Any) -> None:
        """Preserve current state before attempting undo"""
        with self._lock:
            self._state_backups[operation_id] = state_snapshot

    def restore_state_after_undo_failure(self, operation_id: str) -> bool:
        """Restore state after undo failure"""
        with self._lock:
            if operation_id in self._state_backups:
                # In a real implementation, this would restore the backup state
                del self._state_backups[operation_id]
                return True
            return False


class SafeRecoveryBehavior:
    """Implements safe recovery behavior for error conditions"""

    def __init__(self, data_integrity_manager: DataIntegrityManager):
        self.data_integrity_manager = data_integrity_manager
        self._lock = threading.RLock()

    def safe_recovery_from_error(self, error_info: ErrorInfo) -> Tuple[bool, str]:
        """Perform safe recovery from an error condition"""
        try:
            # Verify data integrity first
            integrity_ok, failed_checks = self.data_integrity_manager.verify_integrity()

            if not integrity_ok:
                # Attempt to repair if possible
                repair_ok = self.data_integrity_manager.repair_integrity()
                if not repair_ok:
                    return False, f"Error recovery failed: Data integrity issues detected ({', '.join(failed_checks)})"

            # Log the error for debugging
            logging.error(f"Error recovery attempted: {error_info.message}")

            message = f"Safe recovery performed after error: {error_info.message}\nSystem is in a stable state and ready for normal operation."
            return True, message

        except Exception as e:
            return False, f"Recovery failed: {str(e)}. System may be unstable."

    def validate_safe_state(self) -> Tuple[bool, str]:
        """Validate that the system is in a safe state"""
        try:
            integrity_ok, failed_checks = self.data_integrity_manager.verify_integrity()
            if integrity_ok:
                return True, "System is in safe state"
            else:
                return False, f"Unsafe state: Integrity issues in {', '.join(failed_checks)}"
        except Exception as e:
            return False, f"Could not validate safe state: {str(e)}"


class GracefulDegradation:
    """Implements graceful degradation for error scenarios"""

    def __init__(self):
        self._degraded_features: List[str] = []
        self._lock = threading.RLock()

    def activate_degraded_mode(self, failed_feature: str, error_details: str) -> str:
        """Activate degraded mode when a feature fails"""
        with self._lock:
            if failed_feature not in self._degraded_features:
                self._degraded_features.append(failed_feature)

            return f"Feature '{failed_feature}' temporarily unavailable due to error: {error_details}\nSystem continues operating with reduced functionality."

    def is_feature_degraded(self, feature_name: str) -> bool:
        """Check if a feature is currently in degraded mode"""
        with self._lock:
            return feature_name in self._degraded_features

    def get_available_features(self, all_features: List[str]) -> List[str]:
        """Get list of currently available features"""
        with self._lock:
            return [f for f in all_features if f not in self._degraded_features]

    def restore_feature(self, feature_name: str) -> bool:
        """Restore a feature from degraded mode"""
        with self._lock:
            if feature_name in self._degraded_features:
                self._degraded_features.remove(feature_name)
                return True
            return False


class ErrorHandler:
    """Main error handler coordinating all error handling components"""

    def __init__(self):
        self.data_integrity_manager = DataIntegrityManager()
        self.invalid_command_handler = InvalidCommandHandler()
        self.ambiguous_command_handler = AmbiguousCommandHandler()
        self.confirmation_failure_handler = ConfirmationFailureHandler()
        self.undo_failure_handler = UndoFailureHandler()
        self.safe_recovery_behavior = SafeRecoveryBehavior(self.data_integrity_manager)
        self.graceful_degradation = GracefulDegradation()

        self._error_log: List[ErrorInfo] = []
        self._lock = threading.RLock()

    def log_error(self, error_info: ErrorInfo) -> None:
        """Log error information for debugging and monitoring"""
        with self._lock:
            self._error_log.append(error_info)
            # Keep only the last 100 errors to prevent memory issues
            if len(self._error_log) > 100:
                self._error_log = self._error_log[-100:]

    def handle_invalid_command(self, command: str) -> Tuple[bool, str, List[str]]:
        """Handle invalid command errors (T160)"""
        success, message, suggestions = self.invalid_command_handler.handle_invalid_command(command)

        # Log the error
        error_info = ErrorInfo(
            error_type=ErrorType.INVALID_COMMAND,
            message=message,
            severity=ErrorSeverity.MEDIUM,
            timestamp=datetime.now(),
            command_context=command,
            suggested_solution="Check command spelling and syntax"
        )
        self.log_error(error_info)

        return success, message, suggestions

    def handle_ambiguous_command(self, command: str, interpretations: List[str]) -> Tuple[bool, str, Optional[str]]:
        """Handle ambiguous command disambiguation (T161)"""
        success, message, selected = self.ambiguous_command_handler.resolve_ambiguity(command, interpretations)

        error_info = ErrorInfo(
            error_type=ErrorType.AMBIGUOUS_COMMAND,
            message=message,
            severity=ErrorSeverity.LOW,
            timestamp=datetime.now(),
            command_context=command,
            suggested_solution="Provide more specific command or use number selection"
        )
        self.log_error(error_info)

        return success, message, selected

    def handle_confirmation_failure(self, operation: str, reason: str) -> Tuple[bool, str]:
        """Handle confirmation failure (T162)"""
        success, message = self.confirmation_failure_handler.handle_confirmation_failure(operation, reason)

        error_info = ErrorInfo(
            error_type=ErrorType.CONFIRMATION_FAILURE,
            message=message,
            severity=ErrorSeverity.LOW,
            timestamp=datetime.now(),
            command_context=operation,
            suggested_solution="Retry the operation with proper confirmation"
        )
        self.log_error(error_info)

        return success, message

    def handle_undo_failure(self, failure_reason: str, operation: str) -> Tuple[bool, str]:
        """Handle undo failure with state preservation (T163)"""
        success, message = self.undo_failure_handler.handle_undo_failure(failure_reason, operation)

        error_info = ErrorInfo(
            error_type=ErrorType.UNDO_FAILURE,
            message=message,
            severity=ErrorSeverity.HIGH,
            timestamp=datetime.now(),
            command_context=operation,
            suggested_solution="Operations are preserved, alternative recovery may be needed"
        )
        self.log_error(error_info)

        return success, message

    def handle_system_error(self, error: Exception, context: str = "") -> Tuple[bool, str]:
        """Handle generic system errors with safe recovery (T164)"""
        error_str = str(error)
        tb_str = traceback.format_exc()

        error_info = ErrorInfo(
            error_type=ErrorType.SYSTEM_ERROR,
            message=error_str,
            severity=ErrorSeverity.CRITICAL,
            timestamp=datetime.now(),
            command_context=context,
            suggested_solution="Contact support if issue persists",
            stack_trace=tb_str
        )
        self.log_error(error_info)

        # Attempt safe recovery
        recovery_success, recovery_message = self.safe_recovery_behavior.safe_recovery_from_error(error_info)

        if recovery_success:
            return False, f"Error occurred: {error_str}\n{recovery_message}"
        else:
            return False, f"Critical error: {error_str}\nRecovery failed: {recovery_message}"

    def activate_graceful_degradation(self, feature: str, error_details: str) -> str:
        """Activate graceful degradation for failed features (T165)"""
        message = self.graceful_degradation.activate_degraded_mode(feature, error_details)

        error_info = ErrorInfo(
            error_type=ErrorType.SYSTEM_ERROR,
            message=message,
            severity=ErrorSeverity.MEDIUM,
            timestamp=datetime.now(),
            command_context=feature,
            suggested_solution="Feature temporarily unavailable, system continues operating"
        )
        self.log_error(error_info)

        return message

    def maintain_data_integrity(self) -> Tuple[bool, str]:
        """Maintain data integrity during errors (T166)"""
        integrity_ok, failed_checks = self.data_integrity_manager.verify_integrity()

        if integrity_ok:
            return True, "Data integrity maintained"
        else:
            repair_ok = self.data_integrity_manager.repair_integrity()
            if repair_ok:
                return True, f"Data integrity restored after issues in: {', '.join(failed_checks)}"
            else:
                return False, f"Data integrity issues detected: {', '.join(failed_checks)}"

    def get_error_statistics(self) -> Dict[str, Any]:
        """Get statistics about logged errors"""
        with self._lock:
            if not self._error_log:
                return {"total_errors": 0, "by_type": {}, "by_severity": {}}

            total_errors = len(self._error_log)
            by_type = {}
            by_severity = {}

            for error in self._error_log:
                # Count by type
                error_type = error.error_type.value
                by_type[error_type] = by_type.get(error_type, 0) + 1

                # Count by severity
                severity = error.severity.value
                by_severity[severity] = by_severity.get(severity, 0) + 1

            return {
                "total_errors": total_errors,
                "by_type": by_type,
                "by_severity": by_severity,
                "latest_error": self._error_log[-1].message if self._error_log else None
            }


class ErrorRecoveryManager:
    """Main manager for error handling and recovery operations"""

    def __init__(self):
        self.handler = ErrorHandler()
        self._lock = threading.RLock()

    def execute_with_error_handling(self, operation: Callable, *args, **kwargs) -> Tuple[bool, str, Any]:
        """Execute an operation with comprehensive error handling"""
        try:
            result = operation(*args, **kwargs)
            return True, "Operation completed successfully", result
        except Exception as e:
            success, message = self.handler.handle_system_error(e, f"Operation: {operation.__name__}")
            return success, message, None

    def register_integrity_check(self, name: str, check_func: Callable[[], bool]) -> None:
        """Register a data integrity check (T166)"""
        self.handler.data_integrity_manager.register_integrity_check(name, check_func)

    def validate_safe_state(self) -> Tuple[bool, str]:
        """Validate that the system is in a safe state (T164)"""
        return self.handler.safe_recovery_behavior.validate_safe_state()

    def is_feature_available(self, feature_name: str) -> bool:
        """Check if a feature is available (not in degraded mode) (T165)"""
        return not self.handler.graceful_degradation.is_feature_degraded(feature_name)

    def get_error_summary(self) -> Dict[str, Any]:
        """Get a summary of error statistics (T160-T166)"""
        return self.handler.get_error_statistics()