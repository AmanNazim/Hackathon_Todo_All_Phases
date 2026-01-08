"""
Hybrid Interaction Modes for CLI Todo Application
Implements menu mode, natural language mode, and hybrid switching as specified in spec section 8
"""
from enum import Enum
from typing import Dict, Any, Callable, Optional, List
from dataclasses import dataclass
from src.state_machine.cli_state_machine import CLIStateMachine, StateHandler
from src.parsers.command_parser import CommandParser
from src.middleware.pipeline import MiddlewarePipeline
import re


class InteractionMode(Enum):
    """Define the different interaction modes"""
    MENU = "MENU"
    NATURAL_LANGUAGE = "NATURAL_LANGUAGE"
    HYBRID = "HYBRID"


@dataclass
class CommandSuggestion:
    """Represents a command suggestion for fuzzy matching"""
    command: str
    similarity_score: float
    description: str = ""


class MenuMode:
    """
    Implement menu mode with numbered options display (T070)
    """

    def __init__(self, state_machine: CLIStateMachine, state_handler: StateHandler):
        self.state_machine = state_machine
        self.state_handler = state_handler

    def display_menu(self) -> Dict[str, Any]:
        """
        Display the current menu based on the state machine's current state
        """
        result = self.state_handler.handle_current_state()

        if result.get('action') == 'show_main_menu':
            menu_text = "\nCLI Todo App\n"
            menu_options = result.get('menu_options', [])

            for option in menu_options:
                menu_text += f"{option['option']}. {option['description']}\n"

            menu_text += "Choose option: "
            result['menu_display'] = menu_text

        return result

    def handle_menu_selection(self, selection: str) -> Dict[str, Any]:
        """
        Handle the user's menu selection and convert it to appropriate command
        """
        # Get the current state's menu options
        current_result = self.state_handler.handle_current_state()
        menu_options = current_result.get('menu_options', [])

        # Find the matching command for the selection
        for option in menu_options:
            if option['option'] == selection.strip():
                # Convert menu selection to command
                command_mapping = {
                    '1': 'add',
                    '2': 'list',
                    '3': 'update',
                    '4': 'delete',
                    '5': 'complete',
                    '6': 'help',
                    '7': 'exit'
                }

                command = command_mapping.get(selection.strip(), '')
                return {
                    'command': command,
                    'selection': selection.strip(),
                    'mapped_command': command,
                    'success': True
                }

        return {
            'command': '',
            'selection': selection.strip(),
            'mapped_command': '',
            'success': False,
            'error': f'Invalid menu option: {selection}'
        }


class NaturalLanguageMode:
    """
    Implement natural language mode with intelligent parsing (T071)
    """

    def __init__(self, command_parser: CommandParser, middleware_pipeline: MiddlewarePipeline):
        self.command_parser = command_parser
        self.middleware_pipeline = middleware_pipeline

    def parse_natural_language(self, input_text: str) -> Dict[str, Any]:
        """
        Parse natural language input and convert to structured command
        """
        try:
            # Use the existing command parser to parse the input
            parsed_result = self.command_parser.parse(input_text)

            # Process through middleware pipeline
            initial_data = {
                'raw_input': input_text,
                'parsed_command': parsed_result
            }

            result = self.middleware_pipeline.process(initial_data)

            return {
                'success': result.status.name == 'SUCCESS',
                'parsed_command': parsed_result,
                'pipeline_result': result,
                'raw_input': input_text
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'raw_input': input_text
            }


class HybridModeManager:
    """
    Create hybrid mode switching mechanism (T072)
    """

    def __init__(self, menu_mode: MenuMode, natural_language_mode: NaturalLanguageMode):
        self.menu_mode = menu_mode
        self.natural_language_mode = natural_language_mode
        self.current_mode = InteractionMode.NATURAL_LANGUAGE  # Default to natural language
        self.mode_history: List[InteractionMode] = [self.current_mode]

    def switch_mode(self, mode: InteractionMode) -> bool:
        """
        Switch between different interaction modes
        """
        if mode in InteractionMode:
            self.current_mode = mode
            self.mode_history.append(mode)
            return True
        return False

    def get_current_mode(self) -> InteractionMode:
        """
        Get the current interaction mode
        """
        return self.current_mode

    def process_input(self, input_text: str) -> Dict[str, Any]:
        """
        Process input based on current mode
        """
        if self.current_mode == InteractionMode.MENU:
            return self.menu_mode.handle_menu_selection(input_text)
        elif self.current_mode == InteractionMode.NATURAL_LANGUAGE:
            return self.natural_language_mode.parse_natural_language(input_text)
        elif self.current_mode == InteractionMode.HYBRID:
            # In hybrid mode, try to determine the best approach
            # If input looks like a number, treat as menu selection
            if input_text.strip().isdigit():
                return self.menu_mode.handle_menu_selection(input_text)
            else:
                return self.natural_language_mode.parse_natural_language(input_text)

        return {
            'success': False,
            'error': f'Unknown interaction mode: {self.current_mode}',
            'mode': self.current_mode
        }

    def toggle_mode(self) -> InteractionMode:
        """
        Toggle between menu and natural language modes
        """
        if self.current_mode == InteractionMode.MENU:
            self.switch_mode(InteractionMode.NATURAL_LANGUAGE)
        else:
            self.switch_mode(InteractionMode.MENU)

        return self.current_mode


class FuzzyCommandMatcher:
    """
    Implement fuzzy command suggestions for unrecognized inputs (T073)
    """

    def __init__(self):
        # Define known commands and their variations
        self.known_commands = {
            'add': ['add', 'create', 'make', 'new'],
            'list': ['list', 'show', 'view', 'display', 'ls'],
            'update': ['update', 'edit', 'change', 'modify'],
            'delete': ['delete', 'remove', 'del', 'rm'],
            'complete': ['complete', 'done', 'finish', 'done'],
            'help': ['help', 'info', 'manual', '?'],
            'exit': ['exit', 'quit', 'bye', 'leave'],
            'theme': ['theme', 'style', 'appearance'],
            'undo': ['undo', 'revert', 'back'],
            'snapshot': ['snapshot', 'save', 'backup', 'checkpoint'],
            'macro': ['macro', 'record', 'play']
        }

    def find_suggestions(self, input_command: str, threshold: float = 0.6) -> List[CommandSuggestion]:
        """
        Find command suggestions based on similarity to known commands
        """
        suggestions: List[CommandSuggestion] = []
        input_lower = input_command.lower().strip()

        for canonical_cmd, variations in self.known_commands.items():
            # Check exact match first
            if input_lower == canonical_cmd:
                suggestions.append(CommandSuggestion(
                    command=canonical_cmd,
                    similarity_score=1.0,
                    description=f"Exact match for {canonical_cmd}"
                ))
                continue

            # Calculate similarity with all variations
            max_similarity = 0.0
            best_match = ""

            for variation in variations:
                similarity = self._calculate_similarity(input_lower, variation)
                if similarity > max_similarity:
                    max_similarity = similarity
                    best_match = variation

            # Add to suggestions if similarity is above threshold
            if max_similarity >= threshold:
                suggestions.append(CommandSuggestion(
                    command=canonical_cmd,
                    similarity_score=max_similarity,
                    description=f"Did you mean '{canonical_cmd}' (matched '{best_match}' with {max_similarity:.2f} confidence)?"
                ))

        # Sort suggestions by similarity score (highest first)
        suggestions.sort(key=lambda x: x.similarity_score, reverse=True)

        return suggestions[:5]  # Return top 5 suggestions

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity between two strings using a simple algorithm
        """
        # Use a simple character-based similarity measure
        if len(str1) == 0 and len(str2) == 0:
            return 1.0
        if len(str1) == 0 or len(str2) == 0:
            return 0.0

        # Calculate similarity using longest common subsequence approach
        common_chars = sum(min(str1.count(c), str2.count(c)) for c in set(str1 + str2))
        total_chars = len(str1) + len(str2)

        return (2 * common_chars) / total_chars if total_chars > 0 else 0.0


class ConfirmationManager:
    """
    Add confirmation prompts for critical operations (T074)
    """

    def __init__(self):
        # Define which operations require confirmation
        self.critical_operations = {
            'delete': 'This will permanently remove the task',
            'exit': 'This will end your session',
            'clear': 'This will clear all tasks',
            'reset': 'This will reset the application state',
            'theme': 'This will change the application appearance'
        }

        # Patterns for detecting critical operations in natural language
        self.confirmation_patterns = [
            r'.*delete.*',
            r'.*remove.*',
            r'.*erase.*',
            r'.*quit.*',
            r'.*exit.*',
            r'.*clear.*',
            r'.*reset.*'
        ]

    def requires_confirmation(self, command: str, params: Dict[str, Any] = None) -> tuple[bool, str]:
        """
        Check if a command requires confirmation
        """
        cmd_lower = command.lower()

        # Check against known critical operations
        if cmd_lower in self.critical_operations:
            return True, self.critical_operations[cmd_lower]

        # Check against patterns
        for pattern in self.confirmation_patterns:
            if re.match(pattern, command, re.IGNORECASE):
                return True, f"This is a critical operation: {command}"

        return False, ""

    def generate_confirmation_prompt(self, operation: str, details: str = "") -> str:
        """
        Generate a confirmation prompt for a critical operation
        """
        if details:
            return f"Confirm {operation} operation ({details})? (y/N): "
        else:
            return f"Confirm {operation} operation? (y/N): "

    def validate_confirmation_response(self, response: str) -> bool:
        """
        Validate the user's confirmation response
        """
        response_lower = response.lower().strip()
        return response_lower in ['y', 'yes', 'ye', 'ok', 'true', '1']


class InteractionController:
    """
    Main controller for managing all interaction modes
    """

    def __init__(self,
                 state_machine: CLIStateMachine,
                 state_handler: StateHandler,
                 command_parser: CommandParser,
                 middleware_pipeline: MiddlewarePipeline):

        self.menu_mode = MenuMode(state_machine, state_handler)
        self.natural_language_mode = NaturalLanguageMode(command_parser, middleware_pipeline)
        self.hybrid_manager = HybridModeManager(self.menu_mode, self.natural_language_mode)
        self.fuzzy_matcher = FuzzyCommandMatcher()
        self.confirmation_manager = ConfirmationManager()

        # Track current state
        self.waiting_for_confirmation = False
        self.pending_operation = None

    def process_user_input(self, input_text: str) -> Dict[str, Any]:
        """
        Process user input through the appropriate interaction mode
        """
        # If waiting for confirmation, handle confirmation response
        if self.waiting_for_confirmation and self.pending_operation:
            confirmed = self.confirmation_manager.validate_confirmation_response(input_text)
            if confirmed:
                # Execute the pending operation
                result = self.execute_pending_operation()
                self.waiting_for_confirmation = False
                self.pending_operation = None
                return result
            else:
                # Cancel the operation
                self.waiting_for_confirmation = False
                self.pending_operation = None
                return {
                    'success': False,
                    'cancelled': True,
                    'message': 'Operation cancelled by user'
                }

        # Process input through hybrid manager
        result = self.hybrid_manager.process_input(input_text)

        # Check if this is a command that requires confirmation
        if result.get('success', False) and 'parsed_command' in result:
            parsed_cmd = result['parsed_command']
            cmd_type = parsed_cmd.get('command_type', '')
            params = parsed_cmd.get('params', {})

            requires_conf, reason = self.confirmation_manager.requires_confirmation(cmd_type, params)

            if requires_conf:
                prompt = self.confirmation_manager.generate_confirmation_prompt(cmd_type, reason)
                self.waiting_for_confirmation = True
                self.pending_operation = result
                return {
                    'requires_confirmation': True,
                    'confirmation_prompt': prompt,
                    'pending_operation': cmd_type
                }

        return result

    def execute_pending_operation(self):
        """
        Execute the operation that was waiting for confirmation
        """
        # In a real implementation, this would execute the actual operation
        # For now, we'll just return a success result
        if self.pending_operation:
            return {
                'success': True,
                'executed_operation': self.pending_operation,
                'message': 'Operation completed successfully'
            }
        return {'success': False, 'error': 'No pending operation'}

    def get_current_mode(self) -> InteractionMode:
        """
        Get the current interaction mode
        """
        return self.hybrid_manager.get_current_mode()

    def switch_mode(self, mode: InteractionMode) -> bool:
        """
        Switch to a different interaction mode
        """
        return self.hybrid_manager.switch_mode(mode)

    def get_menu_display(self) -> str:
        """
        Get the menu display if in menu mode
        """
        if self.hybrid_manager.get_current_mode() == InteractionMode.MENU:
            result = self.menu_mode.display_menu()
            return result.get('menu_display', '')
        return ""

    def get_fuzzy_suggestions(self, input_text: str) -> List[CommandSuggestion]:
        """
        Get fuzzy command suggestions for unrecognized input
        """
        return self.fuzzy_matcher.find_suggestions(input_text)