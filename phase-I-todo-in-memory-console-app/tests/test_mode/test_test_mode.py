"""
Tests for Test Mode System Components
Testing the Test Mode tasks: T140-T145
"""
import unittest
import json
from src.test_mode.test_mode import (
    TestModeManager,
    JSONFormatter,
    TestModeRenderer,
    TestModeResponse
)


class TestJSONFormatter(unittest.TestCase):
    """Test JSON formatter functionality (T141, T142, T143)"""

    def setUp(self):
        """Set up test fixtures"""
        self.formatter = JSONFormatter()

    def test_format_response_basic(self):
        """Test basic response formatting (T141)"""
        response = TestModeResponse(
            success=True,
            message="Test message",
            data={"key": "value"}
        )

        result = self.formatter.format_response(response)
        parsed = json.loads(result)

        self.assertTrue(parsed['success'])
        self.assertEqual(parsed['message'], 'Test message')
        self.assertEqual(parsed['data']['key'], 'value')

    def test_format_error(self):
        """Test error formatting (T143)"""
        result = self.formatter.format_error("Test error occurred")
        parsed = json.loads(result)

        self.assertFalse(parsed['success'])
        self.assertIn('error', parsed['message'].lower())

    def test_format_success(self):
        """Test success formatting (T141)"""
        result = self.formatter.format_success("Success message", {"test": "data"})
        parsed = json.loads(result)

        self.assertTrue(parsed['success'])
        self.assertEqual(parsed['message'], 'Success message')
        self.assertEqual(parsed['data']['test'], 'data')

    def test_deterministic_output(self):
        """Test deterministic output ordering (T144)"""
        data = {"z_key": "last", "a_key": "first", "m_key": "middle"}

        # Temporarily disable timestamp setting to test deterministic behavior
        # We'll check the structure and content separately
        response1 = TestModeResponse(success=True, message="Test", data=data, timestamp="FIXED_TIMESTAMP")
        response2 = TestModeResponse(success=True, message="Test", data=data, timestamp="FIXED_TIMESTAMP")

        result1 = self.formatter.format_response(response1)
        result2 = self.formatter.format_response(response2)

        # Same inputs should produce identical outputs
        self.assertEqual(result1, result2)

    def test_json_schema_validation(self):
        """Test JSON schema validation (T141)"""
        response = TestModeResponse(
            success=True,
            message="Valid response",
            data={}
        )

        json_str = self.formatter.format_response(response)
        parsed = json.loads(json_str)

        # Validate required fields exist
        self.assertIn('success', parsed)
        self.assertIn('message', parsed)
        self.assertIn('timestamp', parsed)


class TestTestModeRenderer(unittest.TestCase):
    """Test test mode renderer functionality (T140, T141, T142, T143)"""

    def setUp(self):
        """Set up test fixtures"""
        self.renderer = TestModeRenderer()

    def test_enable_disable_test_mode(self):
        """Test enabling/disabling test mode (T140)"""
        # Initially disabled
        self.assertFalse(self.renderer.is_enabled())

        # Enable test mode
        enable_result = self.renderer.enable_test_mode()
        parsed_enable = json.loads(enable_result)
        self.assertTrue(parsed_enable['success'])
        self.assertTrue(self.renderer.is_enabled())

        # Disable test mode
        disable_result = self.renderer.disable_test_mode()
        parsed_disable = json.loads(disable_result)
        self.assertTrue(parsed_disable['success'])
        self.assertFalse(self.renderer.is_enabled())

    def test_render_output_in_test_mode(self):
        """Test rendering output in test mode (T141)"""
        self.renderer.enable_test_mode()

        result = self.renderer.render_output({"test": "data"}, message="Test output")
        parsed = json.loads(result)

        self.assertTrue(parsed['success'])
        self.assertEqual(parsed['message'], 'Test output')
        self.assertEqual(parsed['data']['test'], 'data')

    def test_render_error_in_test_mode(self):
        """Test rendering errors in test mode (T143)"""
        self.renderer.enable_test_mode()

        result = self.renderer.render_error("Test error message")
        parsed = json.loads(result)

        self.assertFalse(parsed['success'])
        self.assertIn('error', parsed['message'])

    def test_render_list_in_test_mode(self):
        """Test rendering lists in test mode (T141)"""
        self.renderer.enable_test_mode()

        items = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]
        result = self.renderer.render_list(items)
        parsed = json.loads(result)

        self.assertTrue(parsed['success'])
        self.assertEqual(parsed['data']['count'], 2)
        self.assertEqual(len(parsed['data']['items']), 2)

    def test_render_output_normal_mode(self):
        """Test rendering in normal mode (not test mode)"""
        # Test mode is disabled by default
        result = self.renderer.render_output({"test": "data"})
        # Should return JSON string in normal mode too, but without wrapper
        self.assertIsInstance(result, str)


class TestTestModeManager(unittest.TestCase):
    """Test the main test mode manager (T140, T144, T145)"""

    def setUp(self):
        """Set up test fixtures"""
        self.manager = TestModeManager()

    def test_process_test_mode_flag(self):
        """Test processing --test-mode flag (T140)"""
        result = self.manager.process_flag("--test-mode")
        parsed = json.loads(result)

        self.assertTrue(parsed['success'])
        self.assertIn('enabled', parsed['message'].lower())
        self.assertTrue(self.manager.is_test_mode_enabled())

    def test_process_unknown_flag(self):
        """Test processing unknown flag (T140)"""
        result = self.manager.process_flag("--invalid-flag")
        parsed = json.loads(result)

        self.assertFalse(parsed['success'])
        self.assertIn('unknown', parsed['message'].lower())

    def test_execute_command_in_test_mode(self):
        """Test executing commands in test mode (T145)"""
        self.manager.enable_test_mode()

        def mock_command():
            return {"result": "success", "data": [1, 2, 3]}

        result = self.manager.execute_command_in_test_mode("test command", mock_command)
        parsed = json.loads(result)

        self.assertTrue(parsed['success'])
        self.assertEqual(parsed['data']['result'], 'success')
        self.assertEqual(parsed['data']['data'], [1, 2, 3])

    def test_execute_command_error_in_test_mode(self):
        """Test error handling during command execution (T143)"""
        self.manager.enable_test_mode()

        def mock_error_command():
            raise ValueError("Test error")

        result = self.manager.execute_command_in_test_mode("error command", mock_error_command)
        parsed = json.loads(result)

        self.assertFalse(parsed['success'])
        self.assertIn('error', parsed['message'].lower())

    def test_command_history(self):
        """Test command history tracking (T144)"""
        self.manager.enable_test_mode()

        def mock_command():
            return {"status": "ok"}

        # Execute a few commands
        self.manager.execute_command_in_test_mode("cmd1", mock_command)
        self.manager.execute_command_in_test_mode("cmd2", mock_command)

        history = self.manager.get_command_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["command"], "cmd1")
        self.assertEqual(history[1]["command"], "cmd2")

    def test_deterministic_hash(self):
        """Test deterministic hashing for output verification (T144)"""
        data1 = {"key": "value", "num": 42}
        data2 = {"num": 42, "key": "value"}  # Same data, different order

        hash1 = self.manager.get_deterministic_hash(data1)
        hash2 = self.manager.get_deterministic_hash(data2)

        # Should be the same despite different key order
        self.assertEqual(hash1, hash2)

    def test_schema_validation(self):
        """Test JSON schema validation (T141)"""
        valid_json = '{"success": true, "message": "test", "timestamp": "2023-01-01T00:00:00Z"}'
        invalid_json = '{"wrong_field": "value"}'

        self.assertTrue(self.manager.validate_json_schema(valid_json))
        self.assertFalse(self.manager.validate_json_schema(invalid_json))

    def test_format_for_automation(self):
        """Test automation-specific formatting (T145)"""
        self.manager.enable_test_mode()

        data = {"tasks": [1, 2, 3]}
        result = self.manager.format_for_automation(data)
        parsed = json.loads(result)

        self.assertTrue(parsed['success'])
        self.assertIn('data', parsed)
        self.assertEqual(parsed['data']['tasks'], [1, 2, 3])


class TestTestModeIntegration(unittest.TestCase):
    """Test test mode integration scenarios (T140-T145)"""

    def setUp(self):
        """Set up test fixtures"""
        self.manager = TestModeManager()

    def test_full_test_mode_workflow(self):
        """Test complete test mode workflow (T140-T145)"""
        # 1. Enable test mode
        enable_result = self.manager.process_flag("--test-mode")
        parsed_enable = json.loads(enable_result)
        self.assertTrue(parsed_enable['success'])
        self.assertTrue(self.manager.is_test_mode_enabled())

        # 2. Execute a command in test mode
        def sample_command():
            return {"result": "sample", "items": ["a", "b", "c"]}

        command_result = self.manager.execute_command_in_test_mode("sample_cmd", sample_command)
        parsed_command = json.loads(command_result)

        self.assertTrue(parsed_command['success'])
        self.assertEqual(parsed_command['data']['result'], 'sample')
        self.assertEqual(parsed_command['data']['items'], ['a', 'b', 'c'])

        # 3. Check command history
        history = self.manager.get_command_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['command'], 'sample_cmd')

        # 4. Verify deterministic output structure (timestamps will differ)
        command_result2 = self.manager.execute_command_in_test_mode("sample_cmd", sample_command)

        # Parse both results and compare important fields (excluding timestamp)
        parsed_result1 = json.loads(command_result)
        parsed_result2 = json.loads(command_result2)

        # Compare all fields except timestamp
        for key in parsed_result1.keys():
            if key != 'timestamp':  # Exclude timestamp for deterministic comparison
                self.assertEqual(parsed_result1[key], parsed_result2[key])

        # 5. Disable test mode
        disable_result = self.manager.process_flag("--normal-mode")
        parsed_disable = json.loads(disable_result)
        self.assertTrue(parsed_disable['success'])
        self.assertFalse(self.manager.is_test_mode_enabled())

    def test_error_handling_comprehensive(self):
        """Test comprehensive error handling (T143)"""
        self.manager.enable_test_mode()

        # Test various error scenarios
        def error_command():
            raise RuntimeError("Runtime error occurred")

        result = self.manager.execute_command_in_test_mode("error_cmd", error_command)
        parsed = json.loads(result)

        self.assertFalse(parsed['success'])
        self.assertIn('runtime', parsed['message'].lower())

    def test_multiple_commands_deterministic(self):
        """Test multiple commands maintain determinism (T144)"""
        self.manager.enable_test_mode()

        def command_a():
            return {"value": "a"}

        def command_b():
            return {"value": "b"}

        # Execute sequence first time
        result_a1 = self.manager.execute_command_in_test_mode("cmd_a", command_a)
        result_b1 = self.manager.execute_command_in_test_mode("cmd_b", command_b)

        # Clear and execute again
        self.manager.clear_command_history()
        result_a2 = self.manager.execute_command_in_test_mode("cmd_a", command_a)
        result_b2 = self.manager.execute_command_in_test_mode("cmd_b", command_b)

        # Parse the results and compare the important parts (excluding timestamp)
        parsed_a1 = json.loads(result_a1)
        parsed_a2 = json.loads(result_a2)
        parsed_b1 = json.loads(result_b1)
        parsed_b2 = json.loads(result_b2)

        # Compare all fields except timestamp
        for parsed_pair in [(parsed_a1, parsed_a2), (parsed_b1, parsed_b2)]:
            for key in parsed_pair[0].keys():
                if key != 'timestamp':  # Exclude timestamp for deterministic comparison
                    self.assertEqual(parsed_pair[0][key], parsed_pair[1][key])

    def test_json_format_consistency(self):
        """Test JSON format consistency across different operations (T141, T142)"""
        self.manager.enable_test_mode()

        # Test different types of responses all follow same schema
        def success_command():
            return {"data": "success"}

        def list_command():
            return [{"item": 1}, {"item": 2}]

        def string_command():
            return "simple string"

        results = []
        commands = [
            ("success_cmd", success_command),
            ("list_cmd", list_command),
            ("string_cmd", string_command)
        ]

        for cmd_name, cmd_func in commands:
            result = self.manager.execute_command_in_test_mode(cmd_name, cmd_func)
            parsed = json.loads(result)

            # Verify all responses have required fields
            self.assertIn('success', parsed)
            self.assertIn('message', parsed)
            self.assertIn('timestamp', parsed)
            results.append(parsed)

        # All should have consistent structure
        for result in results:
            self.assertIsInstance(result['success'], bool)
            self.assertIsInstance(result['message'], str)
            self.assertIsInstance(result['timestamp'], str)


if __name__ == '__main__':
    unittest.main()