"""
Tests for Hybrid Interaction Modes Components
Testing the Hybrid Interaction Modes tasks: T070-T074
"""
import unittest
from unittest.mock import Mock, MagicMock
from src.interaction_modes.interaction_modes import (
    InteractionMode,
    MenuMode,
    NaturalLanguageMode,
    HybridModeManager,
    FuzzyCommandMatcher,
    ConfirmationManager,
    InteractionController
)
from src.state_machine.cli_state_machine import CLIStateMachine, StateHandler, CLIState
from src.parsers.command_parser import CommandParser
from src.middleware.pipeline import MiddlewarePipeline


class TestMenuMode(unittest.TestCase):
    """Test the menu mode with numbered options display (T070)"""

    def setUp(self):
        """Set up test fixtures"""
        self.state_machine = CLIStateMachine()
        self.state_handler = StateHandler(self.state_machine)
        self.menu_mode = MenuMode(self.state_machine, self.state_handler)

    def test_display_menu_shows_options(self):
        """Test that menu displays numbered options (T070)"""
        result = self.menu_mode.display_menu()

        self.assertIn('menu_display', result)
        self.assertIn('1. Add Task', result['menu_display'])
        self.assertIn('2. View Tasks', result['menu_display'])
        self.assertIn('Choose option:', result['menu_display'])

    def test_handle_valid_menu_selection(self):
        """Test handling valid menu selections (T070)"""
        result = self.menu_mode.handle_menu_selection('1')

        self.assertTrue(result['success'])
        self.assertEqual(result['mapped_command'], 'add')

    def test_handle_invalid_menu_selection(self):
        """Test handling invalid menu selections (T070)"""
        result = self.menu_mode.handle_menu_selection('99')

        self.assertFalse(result['success'])
        self.assertIn('error', result)


class TestNaturalLanguageMode(unittest.TestCase):
    """Test the natural language mode with intelligent parsing (T071)"""

    def setUp(self):
        """Set up test fixtures"""
        # Mock the command parser and middleware pipeline
        self.mock_command_parser = Mock()
        self.mock_command_parser.parse.return_value = {
            'command_type': 'add',
            'params': {'title': 'test task'}
        }

        self.mock_middleware_pipeline = Mock()
        mock_result = Mock()
        mock_result.status.name = 'SUCCESS'
        self.mock_middleware_pipeline.process.return_value = mock_result

        self.natural_language_mode = NaturalLanguageMode(
            self.mock_command_parser,
            self.mock_middleware_pipeline
        )

    def test_parse_natural_language_command(self):
        """Test parsing natural language commands (T071)"""
        result = self.natural_language_mode.parse_natural_language('add Buy groceries')

        self.assertTrue(result['success'])
        self.assertIn('parsed_command', result)
        self.assertIn('pipeline_result', result)

    def test_parse_natural_language_failure(self):
        """Test handling parsing failures (T071)"""
        # Replace with a parser that raises an exception
        failing_parser = Mock()
        failing_parser.parse.side_effect = Exception("Parse error")

        failing_mode = NaturalLanguageMode(failing_parser, self.mock_middleware_pipeline)
        result = failing_mode.parse_natural_language('invalid command')

        self.assertFalse(result['success'])
        self.assertIn('error', result)


class TestHybridModeManager(unittest.TestCase):
    """Test the hybrid mode switching mechanism (T072)"""

    def setUp(self):
        """Set up test fixtures"""
        # Create mock modes
        self.mock_menu_mode = Mock()
        self.mock_natural_language_mode = Mock()

        self.hybrid_manager = HybridModeManager(
            self.mock_menu_mode,
            self.mock_natural_language_mode
        )

    def test_initial_mode_is_natural_language(self):
        """Test that initial mode is natural language (T072)"""
        self.assertEqual(self.hybrid_manager.get_current_mode(), InteractionMode.NATURAL_LANGUAGE)

    def test_switch_mode_functionality(self):
        """Test switching between modes (T072)"""
        # Switch to menu mode
        result = self.hybrid_manager.switch_mode(InteractionMode.MENU)
        self.assertTrue(result)
        self.assertEqual(self.hybrid_manager.get_current_mode(), InteractionMode.MENU)

        # Switch back to natural language
        result = self.hybrid_manager.switch_mode(InteractionMode.NATURAL_LANGUAGE)
        self.assertTrue(result)
        self.assertEqual(self.hybrid_manager.get_current_mode(), InteractionMode.NATURAL_LANGUAGE)

    def test_toggle_mode_functionality(self):
        """Test toggling between modes (T072)"""
        initial_mode = self.hybrid_manager.get_current_mode()
        toggled_mode = self.hybrid_manager.toggle_mode()

        # Should have switched from initial mode
        self.assertNotEqual(initial_mode, toggled_mode)

    def test_process_input_based_on_mode_menu(self):
        """Test processing input based on current mode - menu (T072)"""
        self.hybrid_manager.switch_mode(InteractionMode.MENU)
        self.mock_menu_mode.handle_menu_selection.return_value = {'result': 'menu_result'}

        result = self.hybrid_manager.process_input('1')

        self.mock_menu_mode.handle_menu_selection.assert_called_once_with('1')
        self.assertIn('result', result)

    def test_process_input_based_on_mode_natural_language(self):
        """Test processing input based on current mode - natural language (T072)"""
        self.hybrid_manager.switch_mode(InteractionMode.NATURAL_LANGUAGE)
        self.mock_natural_language_mode.parse_natural_language.return_value = {'result': 'nl_result'}

        result = self.hybrid_manager.process_input('add test')

        self.mock_natural_language_mode.parse_natural_language.assert_called_once_with('add test')
        self.assertIn('result', result)

    def test_process_input_hybrid_mode_number_treated_as_menu(self):
        """Test hybrid mode treats numbers as menu selections (T072)"""
        self.hybrid_manager.switch_mode(InteractionMode.HYBRID)
        self.mock_menu_mode.handle_menu_selection.return_value = {'result': 'menu_result'}

        result = self.hybrid_manager.process_input('1')

        self.mock_menu_mode.handle_menu_selection.assert_called_once_with('1')
        self.assertIn('result', result)

    def test_process_input_hybrid_mode_text_treated_as_natural_language(self):
        """Test hybrid mode treats text as natural language (T072)"""
        self.hybrid_manager.switch_mode(InteractionMode.HYBRID)
        self.mock_natural_language_mode.parse_natural_language.return_value = {'result': 'nl_result'}

        result = self.hybrid_manager.process_input('add test')

        self.mock_natural_language_mode.parse_natural_language.assert_called_once_with('add test')
        self.assertIn('result', result)


class TestFuzzyCommandMatcher(unittest.TestCase):
    """Test fuzzy command suggestions for unrecognized inputs (T073)"""

    def setUp(self):
        """Set up test fixtures"""
        self.fuzzy_matcher = FuzzyCommandMatcher()

    def test_fuzzy_suggestions_for_similar_commands(self):
        """Test fuzzy suggestions for similar commands (T073)"""
        suggestions = self.fuzzy_matcher.find_suggestions('complet')

        # Should find 'complete' as a suggestion
        complete_suggestions = [s for s in suggestions if s.command == 'complete']
        self.assertGreater(len(complete_suggestions), 0)
        self.assertGreater(complete_suggestions[0].similarity_score, 0.5)

    def test_fuzzy_suggestions_for_exact_match(self):
        """Test fuzzy suggestions for exact match (T073)"""
        suggestions = self.fuzzy_matcher.find_suggestions('add')

        # Should find 'add' as an exact match
        add_suggestions = [s for s in suggestions if s.command == 'add' and s.similarity_score == 1.0]
        self.assertGreater(len(add_suggestions), 0)

    def test_fuzzy_suggestions_for_variations(self):
        """Test fuzzy suggestions for command variations (T073)"""
        suggestions = self.fuzzy_matcher.find_suggestions('create')

        # 'create' is a variation of 'add'
        add_suggestions = [s for s in suggestions if s.command == 'add']
        self.assertGreater(len(add_suggestions), 0)

    def test_no_suggestions_for_unrelated_input(self):
        """Test no suggestions for unrelated input (T073)"""
        suggestions = self.fuzzy_matcher.find_suggestions('xyz123')

        # Should have no suggestions above threshold
        self.assertEqual(len(suggestions), 0)

    def test_suggestions_sorted_by_similarity(self):
        """Test suggestions are sorted by similarity score (T073)"""
        suggestions = self.fuzzy_matcher.find_suggestions('complet')

        # Check that suggestions are sorted in descending order
        for i in range(len(suggestions) - 1):
            self.assertGreaterEqual(suggestions[i].similarity_score, suggestions[i + 1].similarity_score)


class TestConfirmationManager(unittest.TestCase):
    """Test confirmation prompts for critical operations (T074)"""

    def setUp(self):
        """Set up test fixtures"""
        self.confirmation_manager = ConfirmationManager()

    def test_critical_operations_require_confirmation(self):
        """Test that critical operations require confirmation (T074)"""
        requires_conf, reason = self.confirmation_manager.requires_confirmation('delete')

        self.assertTrue(requires_conf)
        self.assertIn('remove', reason.lower())

    def test_non_critical_operations_dont_require_confirmation(self):
        """Test that non-critical operations don't require confirmation (T074)"""
        requires_conf, reason = self.confirmation_manager.requires_confirmation('list')

        self.assertFalse(requires_conf)
        self.assertEqual(reason, "")

    def test_confirmation_patterns_match(self):
        """Test confirmation patterns match critical operations (T074)"""
        requires_conf, reason = self.confirmation_manager.requires_confirmation('remove task 1')

        self.assertTrue(requires_conf)

    def test_generate_confirmation_prompt(self):
        """Test generating confirmation prompts (T074)"""
        prompt = self.confirmation_manager.generate_confirmation_prompt('delete', 'This will remove the task')

        self.assertIn('Confirm', prompt)
        self.assertIn('delete', prompt)
        self.assertIn('(This will remove the task)', prompt)

    def test_generate_simple_confirmation_prompt(self):
        """Test generating simple confirmation prompts (T074)"""
        prompt = self.confirmation_manager.generate_confirmation_prompt('exit')

        self.assertIn('Confirm', prompt)
        self.assertIn('exit', prompt)

    def test_validate_confirmation_response_positive(self):
        """Test validating positive confirmation responses (T074)"""
        self.assertTrue(self.confirmation_manager.validate_confirmation_response('y'))
        self.assertTrue(self.confirmation_manager.validate_confirmation_response('yes'))
        self.assertTrue(self.confirmation_manager.validate_confirmation_response('Y'))
        self.assertTrue(self.confirmation_manager.validate_confirmation_response('YES'))

    def test_validate_confirmation_response_negative(self):
        """Test validating negative confirmation responses (T074)"""
        self.assertFalse(self.confirmation_manager.validate_confirmation_response('n'))
        self.assertFalse(self.confirmation_manager.validate_confirmation_response('no'))
        self.assertFalse(self.confirmation_manager.validate_confirmation_response(''))
        self.assertFalse(self.confirmation_manager.validate_confirmation_response('maybe'))


class TestInteractionController(unittest.TestCase):
    """Test the main interaction controller"""

    def setUp(self):
        """Set up test fixtures"""
        # Create mock dependencies
        self.mock_state_machine = Mock()
        self.mock_state_handler = Mock()
        self.mock_command_parser = Mock()
        self.mock_middleware_pipeline = Mock()

        self.controller = InteractionController(
            self.mock_state_machine,
            self.mock_state_handler,
            self.mock_command_parser,
            self.mock_middleware_pipeline
        )

    def test_get_current_mode(self):
        """Test getting current interaction mode"""
        mode = self.controller.get_current_mode()
        self.assertIsInstance(mode, InteractionMode)

    def test_switch_mode(self):
        """Test switching interaction modes"""
        result = self.controller.switch_mode(InteractionMode.MENU)
        self.assertTrue(result)
        self.assertEqual(self.controller.get_current_mode(), InteractionMode.MENU)

    def test_get_menu_display_in_menu_mode(self):
        """Test getting menu display when in menu mode"""
        self.controller.switch_mode(InteractionMode.MENU)
        self.mock_state_handler.handle_current_state.return_value = {
            'action': 'show_main_menu',
            'menu_options': [
                {'option': '1', 'description': 'Add Task'}
            ]
        }

        menu_display = self.controller.get_menu_display()
        self.assertIn('CLI Todo App', menu_display)
        self.assertIn('1. Add Task', menu_display)

    def test_get_menu_display_not_in_menu_mode(self):
        """Test getting menu display when not in menu mode"""
        self.controller.switch_mode(InteractionMode.NATURAL_LANGUAGE)

        menu_display = self.controller.get_menu_display()
        self.assertEqual(menu_display, "")


if __name__ == '__main__':
    unittest.main()