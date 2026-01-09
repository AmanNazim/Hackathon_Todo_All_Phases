"""
Plugin Interface Definitions for CLI Todo Application
Implements T170-T173: Plugin interface contracts
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Protocol
from dataclasses import dataclass


@dataclass
class PluginMetadata:
    """Metadata for plugins"""
    name: str
    version: str
    author: str
    description: str
    phase_i_compliant: bool = True


class BasePlugin(ABC):
    """
    Base plugin interface that all plugins must inherit from
    """

    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata"""
        pass

    @abstractmethod
    def is_phase_i_compliant(self) -> bool:
        """Check if plugin complies with Phase I constraints"""
        pass


class RendererPlugin(BasePlugin):
    """
    Plugin interface for modifying display/output formatting (T170)
    """

    @abstractmethod
    def render_output(self, data: Any, context: Optional[Dict] = None) -> str:
        """Render output with custom formatting"""
        pass

    @abstractmethod
    def supports_format(self, format_type: str) -> bool:
        """Check if plugin supports a specific output format"""
        pass


class ValidatorPlugin(BasePlugin):
    """
    Plugin interface for adding custom validation rules (T171)
    """

    @abstractmethod
    def validate(self, data: Any, context: Optional[Dict] = None) -> tuple[bool, str]:
        """Validate data and return (is_valid, error_message)"""
        pass

    @abstractmethod
    def get_validation_rules(self) -> List[str]:
        """Get list of validation rules implemented by this plugin"""
        pass


class CommandPlugin(BasePlugin):
    """
    Plugin interface for extending command vocabulary (T172)
    """

    @abstractmethod
    def get_commands(self) -> Dict[str, callable]:
        """Return dictionary of command names to handler functions"""
        pass

    @abstractmethod
    def can_handle_command(self, command: str) -> bool:
        """Check if plugin can handle a specific command"""
        pass


class ThemePlugin(BasePlugin):
    """
    Plugin interface for providing new visual themes (T173)
    """

    @abstractmethod
    def get_theme_config(self) -> Dict[str, Any]:
        """Return theme configuration"""
        pass

    @abstractmethod
    def apply_theme(self, content: str) -> str:
        """Apply theme styling to content"""
        pass