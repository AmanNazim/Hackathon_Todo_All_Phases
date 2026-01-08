"""
Logging and Error Handling Infrastructure for CLI Todo Application
Phase I: In-Memory Python CLI Todo Application
"""

import logging
import sys
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
import traceback
import json


class LogLevel(Enum):
    """Log level enumeration"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AppLogger:
    """Application logger with structured logging capabilities"""

    def __init__(self, name: str = "cli-todo-app", level: LogLevel = LogLevel.INFO):
        self.name = name
        self.level = level.value
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.level)

        # Only add handler if not already configured
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def _log(self, level: LogLevel, message: str, extra: Optional[Dict[str, Any]] = None):
        """Internal logging method"""
        log_msg = message
        if extra:
            log_msg += f" | Extra: {extra}"

        if level == LogLevel.DEBUG:
            self.logger.debug(log_msg)
        elif level == LogLevel.INFO:
            self.logger.info(log_msg)
        elif level == LogLevel.WARNING:
            self.logger.warning(log_msg)
        elif level == LogLevel.ERROR:
            self.logger.error(log_msg)
        elif level == LogLevel.CRITICAL:
            self.logger.critical(log_msg)

    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log debug message"""
        if LogLevel.DEBUG.value >= self.level:
            self._log(LogLevel.DEBUG, message, extra)

    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log info message"""
        if LogLevel.INFO.value >= self.level:
            self._log(LogLevel.INFO, message, extra)

    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log warning message"""
        if LogLevel.WARNING.value >= self.level:
            self._log(LogLevel.WARNING, message, extra)

    def error(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log error message"""
        if LogLevel.ERROR.value >= self.level:
            self._log(LogLevel.ERROR, message, extra)

    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log critical message"""
        if LogLevel.CRITICAL.value >= self.level:
            self._log(LogLevel.CRITICAL, message, extra)


class AppException(Exception):
    """Base application exception class"""

    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "APP_ERROR"
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()
        self.traceback_str = traceback.format_exc()

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging"""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
            "timestamp": self.timestamp
        }

    def __str__(self):
        return f"[{self.error_code}] {self.message}"


class ValidationError(AppException):
    """Exception raised for validation errors"""
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        details = {"field": field, "value": value} if field else {}
        super().__init__(message, "VALIDATION_ERROR", details)


class TaskNotFoundError(AppException):
    """Exception raised when a task is not found"""
    def __init__(self, task_id: str):
        super().__init__(f"Task with ID {task_id} not found", "TASK_NOT_FOUND", {"task_id": task_id})


class SecurityError(AppException):
    """Exception raised for security-related issues"""
    def __init__(self, message: str):
        super().__init__(message, "SECURITY_ERROR")


class BusinessLogicError(AppException):
    """Exception raised for business logic violations"""
    def __init__(self, message: str):
        super().__init__(message, "BUSINESS_LOGIC_ERROR")


class ErrorHandler:
    """Centralized error handling system"""

    def __init__(self, logger: AppLogger):
        self.logger = logger

    def handle_exception(self, exc: Exception, context: Optional[str] = None) -> Dict[str, Any]:
        """Handle an exception and return structured error information"""
        if isinstance(exc, AppException):
            # It's already an application exception
            error_info = exc.to_dict()
        else:
            # Wrap standard exceptions in AppException
            app_exc = AppException(
                str(exc),
                error_code="INTERNAL_ERROR",
                details={"original_exception_type": type(exc).__name__, "context": context}
            )
            error_info = app_exc.to_dict()

        # Log the error
        self.logger.error(
            f"Exception occurred: {error_info['message']}",
            extra={
                "error_code": error_info["error_code"],
                "context": context,
                "error_type": error_info["error_type"]
            }
        )

        # In test mode, we might want to output more detailed error info
        if hasattr(self, '_test_mode') and self._test_mode:
            error_info["traceback"] = traceback.format_exc()

        return error_info

    def validate_input(self, value: Any, field_name: str, constraints: Dict[str, Any]) -> bool:
        """Validate input according to constraints"""
        try:
            # Length validation
            if "max_length" in constraints and hasattr(value, '__len__'):
                if len(value) > constraints["max_length"]:
                    raise ValidationError(
                        f"{field_name} exceeds maximum length of {constraints['max_length']} characters",
                        field_name, value
                    )

            if "min_length" in constraints and hasattr(value, '__len__'):
                if len(value) < constraints["min_length"]:
                    raise ValidationError(
                        f"{field_name} is below minimum length of {constraints['min_length']} characters",
                        field_name, value
                    )

            # Value range validation
            if "max_value" in constraints and isinstance(value, (int, float)):
                if value > constraints["max_value"]:
                    raise ValidationError(
                        f"{field_name} exceeds maximum value of {constraints['max_value']}",
                        field_name, value
                    )

            if "min_value" in constraints and isinstance(value, (int, float)):
                if value < constraints["min_value"]:
                    raise ValidationError(
                        f"{field_name} is below minimum value of {constraints['min_value']}",
                        field_name, value
                    )

            # Required field validation
            if constraints.get("required", False):
                if value is None or (hasattr(value, '__len__') and len(value) == 0):
                    raise ValidationError(f"{field_name} is required", field_name, value)

            # Custom validation function
            if "validator" in constraints and callable(constraints["validator"]):
                if not constraints["validator"](value):
                    raise ValidationError(f"{field_name} does not meet validation criteria", field_name, value)

            return True

        except ValidationError:
            # Re-raise validation errors as-is
            raise
        except Exception as e:
            # Handle any other validation-related errors
            raise ValidationError(f"Validation failed for {field_name}: {str(e)}", field_name, value)

    def safe_execute(self, func, *args, **kwargs) -> Optional[Any]:
        """Safely execute a function and handle any exceptions"""
        try:
            return func(*args, **kwargs)
        except AppException:
            # Re-raise application exceptions
            raise
        except Exception as e:
            # Wrap unexpected exceptions
            raise AppException(f"Unexpected error during execution: {str(e)}", "EXECUTION_ERROR")


# Global logger instance
app_logger = AppLogger()


def get_logger() -> AppLogger:
    """Get the global logger instance"""
    return app_logger


def handle_error(exc: Exception, context: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function to handle errors globally"""
    error_handler = ErrorHandler(app_logger)
    return error_handler.handle_exception(exc, context)


def validate_input(value: Any, field_name: str, constraints: Dict[str, Any]) -> bool:
    """Convenience function to validate input globally"""
    error_handler = ErrorHandler(app_logger)
    return error_handler.validate_input(value, field_name, constraints)