"""
Test Mode System for CLI Todo Application
Implements T140-T145: Test Mode functionality
"""
import json
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
import threading
import hashlib


@dataclass
class TestModeResponse:
    """Standardized response structure for test mode"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    command: Optional[str] = None
    timestamp: Optional[str] = None


class JSONFormatter:
    """Formats responses as standardized JSON for test mode"""

    def __init__(self):
        self._deterministic_order = True

    def format_response(self, response: TestModeResponse) -> str:
        """Format a response as JSON with deterministic ordering"""
        # Set timestamp if not already set
        if response.timestamp is None:
            response.timestamp = datetime.now().isoformat() + "Z"

        response_dict = asdict(response)

        if self._deterministic_order:
            # Sort keys to ensure deterministic output
            response_dict = self._sort_dict_recursively(response_dict)

        return json.dumps(response_dict, separators=(',', ':'), sort_keys=False)

    def format_error(self, error_msg: str, command: Optional[str] = None) -> str:
        """Format an error response as JSON"""
        response = TestModeResponse(
            success=False,
            message=error_msg,
            command=command
        )
        return self.format_response(response)

    def format_success(self, message: str, data: Optional[Dict[str, Any]] = None,
                      command: Optional[str] = None) -> str:
        """Format a success response as JSON"""
        response = TestModeResponse(
            success=True,
            message=message,
            data=data,
            command=command
        )
        return self.format_response(response)

    def _sort_dict_recursively(self, obj: Any) -> Any:
        """Recursively sort dictionary keys to ensure deterministic output"""
        if isinstance(obj, dict):
            sorted_dict = {}
            for key in sorted(obj.keys()):
                sorted_dict[key] = self._sort_dict_recursively(obj[key])
            return sorted_dict
        elif isinstance(obj, list):
            return [self._sort_dict_recursively(item) for item in obj]
        else:
            return obj


class TestModeRenderer:
    """Renderer for test mode output"""

    def __init__(self):
        self.formatter = JSONFormatter()
        self.enabled = False
        self._lock = threading.Lock()

    def enable_test_mode(self) -> str:
        """Enable test mode and return confirmation"""
        with self._lock:
            self.enabled = True
            return self.formatter.format_success("Test mode enabled", {"mode": "test"})

    def disable_test_mode(self) -> str:
        """Disable test mode and return confirmation"""
        with self._lock:
            self.enabled = False
            return self.formatter.format_success("Test mode disabled", {"mode": "normal"})

    def is_enabled(self) -> bool:
        """Check if test mode is enabled"""
        with self._lock:
            return self.enabled

    def render_output(self, data: Union[str, Dict[str, Any]], success: bool = True,
                     message: str = "", command: Optional[str] = None) -> str:
        """Render output in test mode format"""
        if not self.enabled:
            # Return plain text for non-test mode
            if isinstance(data, dict):
                return json.dumps(data)
            return str(data)

        # In test mode, return structured JSON
        if isinstance(data, str):
            # If data is string and no specific message, use data as message
            if not message:
                message = data
            return self.formatter.format_success(message, command=command)
        else:
            # Data is a dict/object, use as data field
            return self.formatter.format_success(message or "Operation completed",
                                               data=data, command=command)

    def render_error(self, error_msg: str, command: Optional[str] = None) -> str:
        """Render error in test mode format"""
        if not self.enabled:
            return f"ERROR: {error_msg}"

        return self.formatter.format_error(error_msg, command)

    def render_list(self, items: List[Dict[str, Any]], command: Optional[str] = None) -> str:
        """Render a list of items in test mode format"""
        if not self.enabled:
            return json.dumps(items)

        return self.formatter.format_success("List retrieved",
                                           data={"items": items, "count": len(items)},
                                           command=command)

    def render_task(self, task: Dict[str, Any], command: Optional[str] = None) -> str:
        """Render a single task in test mode format"""
        if not self.enabled:
            return json.dumps(task)

        return self.formatter.format_success("Task retrieved",
                                           data={"task": task},
                                           command=command)


class TestModeManager:
    """Main manager for test mode functionality"""

    def __init__(self):
        self.renderer = TestModeRenderer()
        self.formatter = JSONFormatter()
        self._lock = threading.Lock()
        self._command_history = []

    def process_flag(self, flag: str) -> str:
        """Process test mode flag"""
        if flag == "--test-mode":
            return self.renderer.enable_test_mode()
        elif flag == "--normal-mode":
            return self.renderer.disable_test_mode()
        else:
            return self.formatter.format_error(f"Unknown flag: {flag}")

    def is_test_mode_enabled(self) -> bool:
        """Check if test mode is enabled"""
        return self.renderer.is_enabled()

    def enable_test_mode(self) -> str:
        """Enable test mode"""
        return self.renderer.enable_test_mode()

    def disable_test_mode(self) -> str:
        """Disable test mode"""
        return self.renderer.disable_test_mode()

    def execute_command_in_test_mode(self, command_str: str,
                                   execute_callback) -> str:
        """Execute a command with test mode output"""
        if not self.is_test_mode_enabled():
            # If not in test mode, just execute and return
            try:
                result = execute_callback()
                return str(result)
            except Exception as e:
                return str(e)

        try:
            # Execute the command
            result = execute_callback()

            # Add to command history for deterministic output checking
            with self._lock:
                self._command_history.append({
                    "command": command_str,
                    "timestamp": datetime.utcnow().isoformat(),
                    "result_type": type(result).__name__
                })

            # Format the result appropriately
            if isinstance(result, dict):
                return self.renderer.render_output(result, success=True,
                                                 message="Command executed successfully",
                                                 command=command_str)
            elif isinstance(result, list):
                return self.renderer.render_list(result, command=command_str)
            elif isinstance(result, str):
                return self.renderer.render_output(result, success=True,
                                                 message=result,
                                                 command=command_str)
            else:
                return self.renderer.render_output({"result": result}, success=True,
                                                 message="Command executed",
                                                 command=command_str)
        except Exception as e:
            return self.renderer.render_error(str(e), command=command_str)

    def get_command_history(self) -> List[Dict[str, Any]]:
        """Get command history for test verification"""
        with self._lock:
            return self._command_history.copy()

    def clear_command_history(self) -> None:
        """Clear command history"""
        with self._lock:
            self._command_history.clear()

    def get_deterministic_hash(self, data: Any) -> str:
        """Generate a deterministic hash for data comparison"""
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def validate_json_schema(self, json_str: str) -> bool:
        """Validate that JSON conforms to expected schema"""
        try:
            parsed = json.loads(json_str)
            # Check for required fields in test mode response
            required_fields = ['success', 'message', 'timestamp']
            for field in required_fields:
                if field not in parsed:
                    return False
            return True
        except json.JSONDecodeError:
            return False

    def format_for_automation(self, data: Dict[str, Any]) -> str:
        """Format data specifically for test automation tools"""
        if not self.is_test_mode_enabled():
            return json.dumps(data)

        # Add automation-specific metadata
        automation_data = {
            "success": True,
            "message": "Automation data formatted",
            "data": data,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "format_version": "1.0",
            "automation_compatible": True
        }

        return self.formatter.format_response(TestModeResponse(**{
            k: v for k, v in automation_data.items()
            if k in ['success', 'message', 'data', 'timestamp']
        }))