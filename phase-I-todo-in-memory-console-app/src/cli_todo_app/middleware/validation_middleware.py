"""
Validation Middleware for CLI Todo Application
T053: Create ValidationMiddleware for verifying parameters and task IDs
"""
import re
from typing import Dict, Any, Callable
from .pipeline import MiddlewareResult, MiddlewareResultStatus


class ValidationMiddleware:
    """
    Middleware to validate command parameters and task IDs
    Implements T053: Create ValidationMiddleware for verifying parameters and task IDs
    """

    def __init__(self, repository=None):
        self.name = "ValidationMiddleware"
        self.repository = repository  # Optional repository for checking if task IDs exist
        self.valid_themes = {'minimal', 'emoji', 'hacker', 'professional'}
        self.valid_filters = {'completed', 'pending', 'all'}
        self.valid_snapshot_actions = {'save', 'load', 'list'}
        self.valid_macro_actions = {'record', 'play', 'list'}

    def process(self, data: Dict[str, Any], next_middleware: Callable) -> MiddlewareResult:
        """
        Process the input data by validating command parameters and task IDs
        """
        # Get the intent and parameters from previous middleware
        intent = data.get('intent', 'unknown')
        parsed_params = data.get('parsed_params', {})

        # Validate based on the intent
        validation_result = self._validate_parameters(intent, parsed_params, data)

        if not validation_result['is_valid']:
            return MiddlewareResult(
                status=validation_result['status'],
                data=data,
                error_message=validation_result['error_message'],
                suggestions=validation_result['suggestions']
            )

        # If validation passes, update the data and pass to the next middleware
        data['validated_params'] = validation_result['validated_params']

        return next_middleware(data)

    def _validate_parameters(self, intent: str, params: Dict[str, Any], full_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate parameters based on the intent
        """
        result = {
            'is_valid': True,
            'status': MiddlewareResultStatus.SUCCESS,
            'error_message': None,
            'suggestions': [],
            'validated_params': params.copy()
        }

        try:
            if intent == 'add':
                # Validate add command parameters
                title = params.get('title', '').strip()
                description = params.get('description')

                # Validate title
                if not title:
                    return self._create_validation_error(
                        "Add command requires a title",
                        ["Provide a title: add <title>"]
                    )

                # Validate title length
                if len(title) > 256:
                    return self._create_validation_error(
                        f"Task title exceeds maximum length of 256 characters, got {len(title)}",
                        ["Shorten the title to 256 characters or less"]
                    )

                # Validate description if present
                if description:
                    if len(description) > 1024:
                        return self._create_validation_error(
                            f"Task description exceeds maximum length of 1024 characters, got {len(description)}",
                            ["Shorten the description to 1024 characters or less"]
                        )

            elif intent in ['update', 'delete', 'complete', 'incomplete']:
                # Validate task ID exists
                task_id = params.get('task_id', '').strip()

                if not task_id:
                    return self._create_validation_error(
                        f"{intent.capitalize()} command requires a task ID",
                        [f"Provide a task ID: {intent} <task_id>"]
                    )

                # If repository is provided, check if task exists
                if self.repository:
                    task = self.repository.get(task_id)
                    if not task:
                        return self._create_validation_error(
                            f"Task with ID '{task_id}' does not exist",
                            [f"Provide a valid task ID or create a task first"]
                        )

                # For update, also validate new title if provided
                if intent == 'update':
                    title = params.get('title', '').strip()

                    if not title:
                        return self._create_validation_error(
                            "Update command requires a new title",
                            ["Provide a new title: update <task_id> <new_title>"]
                        )

                    # Validate title length
                    if len(title) > 256:
                        return self._create_validation_error(
                            f"Task title exceeds maximum length of 256 characters, got {len(title)}",
                            ["Shorten the new title to 256 characters or less"]
                        )

                    # Validate description if present
                    description = params.get('description')
                    if description and len(description) > 1024:
                        return self._create_validation_error(
                            f"Task description exceeds maximum length of 1024 characters, got {len(description)}",
                            ["Shorten the description to 1024 characters or less"]
                        )

            elif intent == 'list':
                # Validate filter parameter if present
                filter_value = params.get('filter')
                if filter_value and filter_value not in self.valid_filters:
                    return self._create_validation_error(
                        f"Invalid filter '{filter_value}'. Valid filters: {', '.join(self.valid_filters)}",
                        [f"Use one of: {', '.join(self.valid_filters)}"]
                    )

            elif intent == 'theme':
                # Validate theme name
                theme_name = params.get('theme_name')
                if theme_name and theme_name not in self.valid_themes:
                    return self._create_validation_error(
                        f"Invalid theme '{theme_name}'. Valid themes: {', '.join(self.valid_themes)}",
                        [f"Use one of: {', '.join(self.valid_themes)}"]
                    )

            elif intent == 'snapshot':
                # Validate snapshot action if present
                action = params.get('action')
                if action and action not in self.valid_snapshot_actions:
                    return self._create_validation_error(
                        f"Invalid snapshot action '{action}'. Valid actions: {', '.join(self.valid_snapshot_actions)}",
                        [f"Use one of: {', '.join(self.valid_snapshot_actions)}"]
                    )

            elif intent == 'macro':
                # Validate macro action if present
                action = params.get('action')
                if action and action not in self.valid_macro_actions:
                    return self._create_validation_error(
                        f"Invalid macro action '{action}'. Valid actions: {', '.join(self.valid_macro_actions)}",
                        [f"Use one of: {', '.join(self.valid_macro_actions)}"]
                    )

                # Validate that certain actions require a name
                if action in ['record', 'play'] and not params.get('name'):
                    return self._create_validation_error(
                        f"Macro {action} requires a macro name",
                        [f"Provide a macro name: macro {action} <name>"]
                    )

            # Additional validation for tags
            if 'tags' in params and params['tags']:
                tags = params['tags']
                if isinstance(tags, list):
                    if len(tags) > 10:
                        return self._create_validation_error(
                            f"Task cannot have more than 10 tags, got {len(tags)}",
                            ["Reduce the number of tags to 10 or fewer"]
                        )

                    for tag in tags:
                        if not self._is_valid_tag(tag):
                            return self._create_validation_error(
                                f"Invalid tag format: {tag}. Tags must be alphanumeric with hyphens/underscores only.",
                                ["Use only alphanumeric characters, hyphens, and underscores in tags"]
                            )

        except Exception as e:
            return self._create_validation_error(
                f"Validation error: {str(e)}",
                ["Check the input format and try again"]
            )

        return result

    def _create_validation_error(self, error_message: str, suggestions: list) -> Dict[str, Any]:
        """
        Create a validation error result
        """
        return {
            'is_valid': False,
            'status': MiddlewareResultStatus.VALIDATION_FAILED,
            'error_message': error_message,
            'suggestions': suggestions,
            'validated_params': {}
        }

    def _is_valid_tag(self, tag: str) -> bool:
        """
        Validate tag format according to spec
        """
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', tag))