"""
Intent Classifier Middleware for CLI Todo Application
T051: Create IntentClassifier middleware for determining command type
"""
import re
from typing import Dict, Any, Callable
from src.middleware.pipeline import MiddlewareResult


class IntentClassifier:
    """
    Middleware to classify user intent and determine command type
    Implements T051: Create IntentClassifier middleware for determining command type
    """

    def __init__(self):
        self.name = "IntentClassifier"
        # Define command patterns for classification
        self.command_patterns = {
            'add': [
                r'^(?:add|a)\s+(.+)',
            ],
            'list': [
                r'^(?:list|view|l)(?:\s+(\w+))?$',
            ],
            'update': [
                r'^(?:update|edit)\s+(\w+)\s+(.+)',
            ],
            'delete': [
                r'^(?:delete|remove|del|d)\s+(\w+)$',
            ],
            'complete': [
                r'^(?:complete|done|finish|c)\s+(\w+)$',
            ],
            'incomplete': [
                r'^(?:incomplete|reopen|open|i)\s+(\w+)$',
            ],
            'undo': [
                r'^(?:undo|revert)$',
            ],
            'help': [
                r'^(?:help|h|\?|--help)(?:\s+(\w+))?$',
            ],
            'theme': [
                r'^(?:theme)\s+(\w+)$',
            ],
            'snapshot': [
                r'^(?:snapshot)(?:\s+(\w+))?$',
            ],
            'macro': [
                r'^(?:macro)(?:\s+(\w+))?(?:\s+(\w+))?$',
            ]
        }

    def process(self, data: Dict[str, Any], next_middleware: Callable) -> MiddlewareResult:
        """
        Process the input data by classifying the user intent/command type
        """
        # Get the normalized input from previous middleware
        normalized_input = data.get('normalized_input', '')

        # Classify the intent
        intent_result = self._classify_intent(normalized_input)

        # Update the data with intent information
        data['intent'] = intent_result['intent']
        data['intent_confidence'] = intent_result['confidence']
        data['parsed_params'] = intent_result['params']

        # Pass to the next middleware in the chain
        return next_middleware(data)

    def _classify_intent(self, normalized_input: str) -> Dict[str, Any]:
        """
        Classify the user intent based on the normalized input
        """
        if not normalized_input:
            return {
                'intent': 'unknown',
                'confidence': 'none',
                'params': {}
            }

        # Try to match each command pattern
        for command_type, patterns in self.command_patterns.items():
            for pattern in patterns:
                match = re.match(pattern, normalized_input, re.IGNORECASE)
                if match:
                    # Extract parameters based on the match
                    groups = match.groups()

                    if command_type == 'add':
                        params = {
                            'title': groups[0].strip() if groups and groups[0] else '',
                            'description': None  # Will be extracted if present
                        }
                    elif command_type == 'list':
                        params = {
                            'filter': groups[0].lower() if groups and groups[0] else None
                        }
                    elif command_type == 'update':
                        params = {
                            'task_id': groups[0] if groups and len(groups) > 0 else '',
                            'title': groups[1].strip() if groups and len(groups) > 1 else '',
                            'description': None  # Will be extracted if present
                        }
                    elif command_type in ['delete', 'complete', 'incomplete']:
                        params = {
                            'task_id': groups[0] if groups and groups[0] else ''
                        }
                    elif command_type == 'help':
                        params = {
                            'topic': groups[0] if groups and groups[0] else None
                        }
                    elif command_type == 'theme':
                        params = {
                            'theme_name': groups[0].lower() if groups and groups[0] else None
                        }
                    elif command_type == 'snapshot':
                        params = {
                            'action': groups[0].lower() if groups and groups[0] else 'list'
                        }
                    elif command_type == 'macro':
                        params = {
                            'action': groups[0].lower() if groups and len(groups) > 0 and groups[0] else 'list',
                            'name': groups[1] if len(groups) > 1 and groups[1] else None
                        }
                    else:
                        params = {}

                    return {
                        'intent': command_type,
                        'confidence': 'high',
                        'params': params
                    }

        # If no pattern matches, return unknown intent
        return {
            'intent': 'unknown',
            'confidence': 'none',
            'params': {}
        }