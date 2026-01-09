"""
Security Guard Middleware for CLI Todo Application
T052: Create SecurityGuard middleware for validating command safety
"""
import re
from typing import Dict, Any, Callable
from .pipeline import MiddlewareResult, MiddlewareResultStatus


class SecurityGuard:
    """
    Middleware to validate command safety and prevent malicious inputs
    Implements T052: Create SecurityGuard middleware for validating command safety
    """

    def __init__(self):
        self.name = "SecurityGuard"
        # Define dangerous patterns that should be blocked
        self.dangerous_patterns = [
            # Command injection patterns
            r';\s*[a-z]',  # Semicolon followed by command
            r'\|\s*[a-z]',  # Pipe followed by command
            r'&&\s*[a-z]',  # Double ampersand followed by command
            r'\|\|',  # Double pipe (OR operator)
            r'\$\(',  # Command substitution
            r'`[^`]*`',  # Backtick command substitution
            r'<\s*/etc/',  # Reading system files
            r'>\s*/etc/',  # Writing to system files
            # Dangerous commands that shouldn't be executed
            r'\brm\s+-',  # rm command with flags
            r'\bmv\s+',  # mv command
            r'\bcd\s+',  # cd command
            r'\bcat\s+/etc/',  # Reading system files
            # Patterns that might be used for injection
            r'\$\{.*\}',  # Variable expansion
            r'\~.*',  # Home directory expansion
            # Potential path traversal
            r'\.\./',  # Directory traversal
            r'%2[eE]%2[eE]/',  # URL encoded directory traversal
        ]

    def process(self, data: Dict[str, Any], next_middleware: Callable) -> MiddlewareResult:
        """
        Process the input data by validating command safety
        """
        # Get the normalized input from previous middleware
        normalized_input = data.get('normalized_input', '')

        # Check for security violations
        security_check = self._check_security(normalized_input)

        if not security_check['is_safe']:
            return MiddlewareResult(
                status=MiddlewareResultStatus.SECURITY_VIOLATION,
                data=data,
                error_message=security_check['error_message'],
                suggestions=security_check['suggestions']
            )

        # If input is safe, pass to the next middleware in the chain
        return next_middleware(data)

    def _check_security(self, normalized_input: str) -> Dict[str, Any]:
        """
        Check if the input contains any security violations
        """
        if not normalized_input:
            return {
                'is_safe': True,
                'error_message': None,
                'suggestions': []
            }

        # Check against dangerous patterns
        for pattern in self.dangerous_patterns:
            if re.search(pattern, normalized_input, re.IGNORECASE):
                return {
                    'is_safe': False,
                    'error_message': f"Security violation detected in command: potential command injection",
                    'suggestions': [
                        "Remove any special characters like ;, |, &, $, ` from your command",
                        "Use only alphanumeric characters and spaces in task titles/descriptions",
                        "Avoid system commands in your input"
                    ]
                }

        # Additional security checks
        # Check for excessively long inputs (potential buffer overflow)
        if len(normalized_input) > 1000:  # Arbitrary limit, adjust as needed
            return {
                'is_safe': False,
                'error_message': "Command input too long, potential security risk",
                'suggestions': [
                    "Keep command length under 1000 characters",
                    "Break down complex operations into smaller commands"
                ]
            }

        # Check for potential SQL-like injection patterns (though we don't have SQL)
        sql_injection_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|TABLE|FROM|WHERE)\b)",
            r"(--.*)",  # SQL comment
            r"(''.*)",  # String concatenation
            r'(;.*)',  # Statement terminator
        ]

        for pattern in sql_injection_patterns:
            if re.search(pattern, normalized_input, re.IGNORECASE):
                return {
                    'is_safe': False,
                    'error_message': "Potential SQL injection detected in command",
                    'suggestions': [
                        "Remove SQL keywords from your command",
                        "Avoid using special characters that might be interpreted as SQL",
                        "Use only alphanumeric characters and spaces in task titles/descriptions"
                    ]
                }

        # If all checks pass, return safe
        return {
            'is_safe': True,
            'error_message': None,
            'suggestions': []
        }