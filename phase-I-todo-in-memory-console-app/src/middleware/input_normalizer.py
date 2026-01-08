"""
Input Normalizer Middleware for CLI Todo Application
T050: Create InputNormalizer middleware for standardizing command format
"""
import re
from typing import Dict, Any, Callable
from src.middleware.pipeline import MiddlewareResult


class InputNormalizer:
    """
    Middleware to standardize command format and normalize input
    Implements T050: Create InputNormalizer middleware for standardizing command format
    """

    def __init__(self):
        self.name = "InputNormalizer"

    def process(self, data: Dict[str, Any], next_middleware: Callable) -> MiddlewareResult:
        """
        Process the input data by normalizing the command format
        """
        # Get the raw input command
        raw_input = data.get('raw_input', '')

        # Normalize the input: trim whitespace, standardize spacing, etc.
        normalized_input = self._normalize_input(raw_input)

        # Update the data with normalized input
        data['normalized_input'] = normalized_input

        # Pass to the next middleware in the chain
        return next_middleware(data)

    def _normalize_input(self, raw_input: str) -> str:
        """
        Normalize the raw input command
        - Remove extra whitespace
        - Convert to lowercase for command matching
        - Standardize spacing between tokens
        """
        if not raw_input:
            return raw_input

        # Strip leading/trailing whitespace
        normalized = raw_input.strip()

        # Replace multiple consecutive spaces with single space
        normalized = re.sub(r'\s+', ' ', normalized)

        # Handle common variations and synonyms
        normalized = self._normalize_synonyms(normalized)

        return normalized

    def _normalize_synonyms(self, input_text: str) -> str:
        """
        Normalize common command synonyms to canonical forms
        """
        # Define command synonyms mapping
        synonyms = {
            r'\bcomplete\b': 'complete',
            r'\bdone\b': 'complete',
            r'\bfinish\b': 'complete',
            r'\bc\b': 'complete',
            r'\bincomplete\b': 'incomplete',
            r'\breopen\b': 'incomplete',
            r'\bopen\b': 'incomplete',
            r'\bi\b': 'incomplete',
            r'\bdelete\b': 'delete',
            r'\bremove\b': 'delete',
            r'\bdel\b': 'delete',
            r'\bd\b': 'delete',
            r'\blist\b': 'list',
            r'\bview\b': 'list',
            r'\bl\b': 'list',
            r'\bupdate\b': 'update',
            r'\bedit\b': 'update',
            r'\bhelp\b': 'help',
            r'\bh\b': 'help',
            r'\?\b': 'help',
            r'\b--help\b': 'help',
            r'\bundo\b': 'undo',
            r'\brevert\b': 'undo',
        }

        # Apply synonym replacements
        normalized = input_text.lower()
        for pattern, replacement in synonyms.items():
            normalized = re.sub(pattern, replacement, normalized)

        return normalized