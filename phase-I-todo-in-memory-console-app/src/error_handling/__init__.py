"""
Error Handling & Recovery module for CLI Todo Application
"""
from .error_handler import (
    ErrorHandler,
    ErrorRecoveryManager,
    InvalidCommandHandler,
    AmbiguousCommandHandler,
    ConfirmationFailureHandler,
    UndoFailureHandler,
    SafeRecoveryBehavior,
    GracefulDegradation,
    DataIntegrityManager
)

__all__ = [
    'ErrorHandler',
    'ErrorRecoveryManager',
    'InvalidCommandHandler',
    'AmbiguousCommandHandler',
    'ConfirmationFailureHandler',
    'UndoFailureHandler',
    'SafeRecoveryBehavior',
    'GracefulDegradation',
    'DataIntegrityManager'
]