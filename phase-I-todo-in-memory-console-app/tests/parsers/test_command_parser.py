"""
Unit tests for Command Parser implementation
Testing the Command Grammar & Parsing tasks: T040-T048
"""
import unittest
from src.parsers.command_parser import CommandParser, CommandType, ParseResult


class TestCommandParser(unittest.TestCase):
    """Test the command parser functionality (T046)"""

    def setUp(self):
        """Set up test data"""
        self.parser = CommandParser()

    def test_add_command_basic(self):
        """Test basic add command with title (T040)"""
        result = self.parser.parse("add Buy groceries")

        self.assertTrue(result.is_valid)
        self.assertEqual(result.command_type, CommandType.ADD)
        self.assertEqual(result.parameters['title'], 'Buy groceries')
        self.assertIsNone(result.parameters['description'])

    def test_add_command_with_description(self):
        """Test add command with title and description (T040)"""
        result = self.parser.parse("add Buy groceries Buy organic items")

        self.assertTrue(result.is_valid)
        self.assertEqual(result.command_type, CommandType.ADD)
        self.assertEqual(result.parameters['title'], 'Buy groceries')
        self.assertEqual(result.parameters['description'], 'Buy organic items')

    def test_add_command_shortcut(self):
        """Test add command shortcut 'a' (T047)"""
        result = self.parser.parse("a Buy groceries")

        self.assertTrue(result.is_valid)
        self.assertEqual(result.command_type, CommandType.ADD)
        self.assertEqual(result.parameters['title'], 'Buy groceries')

    def test_add_command_validation_missing_title(self):
        """Test add command validation for missing title (T040)"""
        result = self.parser.parse("add")

        self.assertFalse(result.is_valid)
        self.assertIn("requires a title", result.error_message)

    def test_list_command_basic(self):
        """Test basic list command (T041)"""
        result = self.parser.parse("list")

        self.assertTrue(result.is_valid)
        self.assertEqual(result.command_type, CommandType.LIST)
        self.assertIsNone(result.parameters['filter'])

    def test_list_command_with_filter(self):
        """Test list command with filter (T041)"""
        result = self.parser.parse("list completed")

        self.assertTrue(result.is_valid)
        self.assertEqual(result.command_type, CommandType.LIST)
        self.assertEqual(result.parameters['filter'], 'completed')

    def test_list_command_shortcut(self):
        """Test list command shortcut 'l' (T047)"""
        result = self.parser.parse("l")

        self.assertTrue(result.is_valid)
        self.assertEqual(result.command_type, CommandType.LIST)

    def test_list_command_view_synonym(self):
        """Test list command 'view' synonym (T041)"""
        result = self.parser.parse("view pending")

        self.assertTrue(result.is_valid)
        self.assertEqual(result.command_type, CommandType.LIST)
        self.assertEqual(result.parameters['filter'], 'pending')

    def test_list_command_invalid_filter(self):
        """Test list command with invalid filter (T041)"""
        result = self.parser.parse("list invalid_filter")

        self.assertFalse(result.is_valid)
        self.assertIn("Invalid filter", result.error_message)

    def test_update_command_basic(self):
        """Test basic update command (T042)"""
        result = self.parser.parse("update 123 New title")

        self.assertTrue(result.is_valid)
        self.assertEqual(result.command_type, CommandType.UPDATE)
        self.assertEqual(result.parameters['task_id'], '123')
        self.assertEqual(result.parameters['title'], 'New title')
        self.assertIsNone(result.parameters['description'])

    def test_update_command_with_description(self):
        """Test update command with description (T042)"""
        result = self.parser.parse("update 123 New title New description")

        self.assertTrue(result.is_valid)
        self.assertEqual(result.command_type, CommandType.UPDATE)
        self.assertEqual(result.parameters['task_id'], '123')
        self.assertEqual(result.parameters['title'], 'New title')
        self.assertEqual(result.parameters['description'], 'New description')

    def test_update_command_edit_synonym(self):
        """Test update command 'edit' synonym (T042)"""
        result = self.parser.parse("edit 456 Updated title")

        self.assertTrue(result.is_valid)
        self.assertEqual(result.command_type, CommandType.UPDATE)

    def test_update_command_validation_missing_id(self):
        """Test update command validation for missing ID (T042)"""
        result = self.parser.parse("update New title")

        self.assertFalse(result.is_valid)
        self.assertIn("requires a task ID", result.error_message)

    def test_update_command_validation_missing_title(self):
        """Test update command validation for missing title (T042)"""
        result = self.parser.parse("update 123")

        self.assertFalse(result.is_valid)
        self.assertIn("requires a new title", result.error_message)

    def test_delete_command_basic(self):
        """Test basic delete command (T043)"""
        result = self.parser.parse("delete 123")

        self.assertTrue(result.is_valid)
        self.assertEqual(result.command_type, CommandType.DELETE)
        self.assertEqual(result.parameters['task_id'], '123')

    def test_delete_command_shortcuts(self):
        """Test delete command shortcuts (T047)"""
        shortcuts = ["del 123", "remove 123", "d 123"]

        for cmd in shortcuts:
            result = self.parser.parse(cmd)
            self.assertTrue(result.is_valid, f"Command {cmd} should be valid")
            self.assertEqual(result.command_type, CommandType.DELETE)
            self.assertEqual(result.parameters['task_id'], '123')

    def test_delete_command_validation_missing_id(self):
        """Test delete command validation for missing ID (T043)"""
        result = self.parser.parse("delete")

        self.assertFalse(result.is_valid)
        self.assertIn("requires a task ID", result.error_message)

    def test_complete_command_basic(self):
        """Test basic complete command (T044)"""
        result = self.parser.parse("complete 123")

        self.assertTrue(result.is_valid)
        self.assertEqual(result.command_type, CommandType.COMPLETE)
        self.assertEqual(result.parameters['task_id'], '123')

    def test_complete_command_shortcuts(self):
        """Test complete command shortcuts (T047)"""
        shortcuts = ["done 123", "finish 123", "c 123"]

        for cmd in shortcuts:
            result = self.parser.parse(cmd)
            self.assertTrue(result.is_valid, f"Command {cmd} should be valid")
            self.assertEqual(result.command_type, CommandType.COMPLETE)
            self.assertEqual(result.parameters['task_id'], '123')

    def test_incomplete_command_basic(self):
        """Test basic incomplete command (T044)"""
        result = self.parser.parse("incomplete 123")

        self.assertTrue(result.is_valid)
        self.assertEqual(result.command_type, CommandType.IN_COMPLETE)
        self.assertEqual(result.parameters['task_id'], '123')

    def test_incomplete_command_shortcuts(self):
        """Test incomplete command shortcuts (T047)"""
        shortcuts = ["reopen 123", "open 123", "i 123"]

        for cmd in shortcuts:
            result = self.parser.parse(cmd)
            self.assertTrue(result.is_valid, f"Command {cmd} should be valid")
            self.assertEqual(result.command_type, CommandType.IN_COMPLETE)
            self.assertEqual(result.parameters['task_id'], '123')

    def test_undo_command(self):
        """Test undo command (T045)"""
        result = self.parser.parse("undo")

        self.assertTrue(result.is_valid)
        self.assertEqual(result.command_type, CommandType.UNDO)

    def test_undo_command_synonym(self):
        """Test undo command synonym (T045)"""
        result = self.parser.parse("revert")

        self.assertTrue(result.is_valid)
        self.assertEqual(result.command_type, CommandType.UNDO)

    def test_help_command_basic(self):
        """Test basic help command (T045)"""
        result = self.parser.parse("help")

        self.assertTrue(result.is_valid)
        self.assertEqual(result.command_type, CommandType.HELP)
        self.assertIsNone(result.parameters['topic'])

    def test_help_command_with_topic(self):
        """Test help command with topic (T045)"""
        result = self.parser.parse("help add")

        self.assertTrue(result.is_valid)
        self.assertEqual(result.command_type, CommandType.HELP)
        self.assertEqual(result.parameters['topic'], 'add')

    def test_help_command_shortcuts(self):
        """Test help command shortcuts (T045)"""
        shortcuts = ["h", "?", "--help"]

        for cmd in shortcuts:
            result = self.parser.parse(cmd)
            self.assertTrue(result.is_valid, f"Command {cmd} should be valid")
            self.assertEqual(result.command_type, CommandType.HELP)

    def test_theme_command(self):
        """Test theme command (T045)"""
        result = self.parser.parse("theme minimal")

        self.assertTrue(result.is_valid)
        self.assertEqual(result.command_type, CommandType.THEME)
        self.assertEqual(result.parameters['theme_name'], 'minimal')

    def test_theme_command_invalid(self):
        """Test theme command with invalid theme (T045)"""
        result = self.parser.parse("theme invalid_theme")

        self.assertFalse(result.is_valid)
        self.assertIn("Invalid theme", result.error_message)

    def test_theme_command_missing_name(self):
        """Test theme command with missing name (T045)"""
        result = self.parser.parse("theme")

        self.assertFalse(result.is_valid)
        self.assertIn("requires a theme name", result.error_message)

    def test_snapshot_command_basic(self):
        """Test basic snapshot command (T045)"""
        result = self.parser.parse("snapshot")

        self.assertTrue(result.is_valid)
        self.assertEqual(result.command_type, CommandType.SNAPSHOT)
        self.assertEqual(result.parameters['action'], 'list')

    def test_snapshot_command_with_action(self):
        """Test snapshot command with action (T045)"""
        result = self.parser.parse("snapshot save")

        self.assertTrue(result.is_valid)
        self.assertEqual(result.command_type, CommandType.SNAPSHOT)
        self.assertEqual(result.parameters['action'], 'save')

    def test_snapshot_command_invalid_action(self):
        """Test snapshot command with invalid action (T045)"""
        result = self.parser.parse("snapshot invalid_action")

        self.assertFalse(result.is_valid)
        self.assertIn("Invalid snapshot action", result.error_message)

    def test_macro_command_basic(self):
        """Test basic macro command (T045)"""
        result = self.parser.parse("macro")

        self.assertTrue(result.is_valid)
        self.assertEqual(result.command_type, CommandType.MACRO)
        self.assertEqual(result.parameters['action'], 'list')

    def test_macro_command_with_action(self):
        """Test macro command with action (T045)"""
        result = self.parser.parse("macro record")

        self.assertTrue(result.is_valid)
        self.assertEqual(result.command_type, CommandType.MACRO)
        self.assertEqual(result.parameters['action'], 'record')

    def test_macro_command_with_action_and_name(self):
        """Test macro command with action and name (T045)"""
        result = self.parser.parse("macro record my_macro")

        self.assertTrue(result.is_valid)
        self.assertEqual(result.command_type, CommandType.MACRO)
        self.assertEqual(result.parameters['action'], 'record')
        self.assertEqual(result.parameters['name'], 'my_macro')

    def test_macro_command_play_by_name(self):
        """Test macro command playing by name (T045)"""
        result = self.parser.parse("macro my_macro")

        # This should be treated as playing the macro
        self.assertTrue(result.is_valid)
        self.assertEqual(result.command_type, CommandType.MACRO)
        self.assertEqual(result.parameters['action'], 'play')
        self.assertEqual(result.parameters['name'], 'my_macro')

    def test_unknown_command(self):
        """Test parsing of unknown command"""
        result = self.parser.parse("unknown_command")

        self.assertFalse(result.is_valid)
        self.assertIn("Unknown command", result.error_message)

    def test_empty_command(self):
        """Test parsing of empty command"""
        result = self.parser.parse("")

        self.assertFalse(result.is_valid)
        self.assertIn("Empty command", result.error_message)

    def test_whitespace_command(self):
        """Test parsing of whitespace-only command"""
        result = self.parser.parse("   ")

        self.assertFalse(result.is_valid)
        self.assertIn("Empty command", result.error_message)

    def test_case_insensitive_parsing(self):
        """Test that parsing is case-insensitive"""
        test_cases = [
            ("ADD Buy Groceries", CommandType.ADD),
            ("LIST", CommandType.LIST),
            ("UPDATE 123 New Title", CommandType.UPDATE),
            ("DELETE 123", CommandType.DELETE),
            ("COMPLETE 123", CommandType.COMPLETE),
        ]

        for cmd, expected_type in test_cases:
            result = self.parser.parse(cmd)
            self.assertTrue(result.is_valid, f"Command {cmd} should be valid")
            self.assertEqual(result.command_type, expected_type)

    def test_parameter_extraction(self):
        """Test parameter extraction functionality (T048)"""
        # Test with ADD command
        result = self.parser.parse("add Buy groceries")
        params = result.parameters

        self.assertEqual(params['title'], 'Buy groceries')
        self.assertIsNone(params['description'])

    def test_parse_result_structure(self):
        """Test that parse result follows expected structure"""
        result = self.parser.parse("add Test task")

        # Check that result has all required fields from ParseResult
        self.assertIsInstance(result.intent_name, str)
        self.assertIsInstance(result.intent_confidence, str)
        self.assertIsInstance(result.normalized_command, str)
        self.assertIsInstance(result.extracted_entities, dict)
        self.assertIsInstance(result.missing_information, list)
        self.assertIsInstance(result.ambiguity_flags, list)
        self.assertIsInstance(result.suggested_clarifications, list)
        self.assertIsInstance(result.parse_status, str)
        self.assertIsInstance(result.parse_reasoning, str)
        self.assertEqual(result.command_type, CommandType.ADD)
        self.assertTrue(result.is_valid)

    def test_extracted_entities_content(self):
        """Test that extracted entities contain expected content"""
        result = self.parser.parse("add Buy groceries Buy organic items")

        entities = result.extracted_entities
        self.assertIn('Buy groceries', entities['titles'])
        self.assertIn('Buy organic items', entities['descriptions'])
        self.assertEqual(entities['ids'], [])

    def test_performance_validation(self):
        """Test that parsing completes within performance requirements (T046)"""
        import time

        start_time = time.time()
        result = self.parser.parse("add Test task")
        end_time = time.time()

        duration_ms = (end_time - start_time) * 1000

        # Parsing should complete within 50ms as per spec
        self.assertLess(duration_ms, 50, f"Parsing took {duration_ms}ms, exceeds 50ms limit")
        self.assertTrue(result.is_valid)

    def test_security_input_validation(self):
        """Test that parser handles potentially malicious input safely"""
        malicious_inputs = [
            "; rm -rf /",
            "$(rm -rf /)",
            "`rm -rf /`",
            "<script>alert('xss')</script>",
            "add || echo 'command injection'",
            "list && rm -rf /",
            "delete $(whoami)"
        ]

        for malicious_input in malicious_inputs:
            # Parser should not crash and should return invalid result
            result = self.parser.parse(malicious_input)

            # Result should either be invalid or not execute malicious code
            # (The parser should recognize these as invalid commands)
            self.assertIsInstance(result, ParseResult)


if __name__ == '__main__':
    unittest.main()