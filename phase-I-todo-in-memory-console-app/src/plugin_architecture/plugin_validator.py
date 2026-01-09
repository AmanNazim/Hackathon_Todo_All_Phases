"""
Plugin Validator for CLI Todo Application
Implements T175: Plugin validation against interface contracts
Implements T178: Phase I constraint enforcement for plugins
"""
from typing import Any, List, Dict, Type
from .plugin_interface import (
    BasePlugin, RendererPlugin, ValidatorPlugin,
    CommandPlugin, ThemePlugin
)
import logging


class PluginValidator:
    """
    Validates plugins against interface contracts and Phase I constraints (T175, T178)
    """

    @staticmethod
    def validate_plugin_interface(plugin: BasePlugin) -> tuple[bool, List[str]]:
        """
        Validate that a plugin properly implements its interface contract
        """
        errors = []

        # Check if it's a proper subclass of BasePlugin
        if not isinstance(plugin, BasePlugin):
            errors.append("Plugin is not an instance of BasePlugin")
            return False, errors

        # Check that required methods are implemented
        try:
            metadata = plugin.get_metadata()
            # Validate metadata structure
            if not hasattr(metadata, 'name') or not hasattr(metadata, 'version'):
                errors.append("Plugin metadata is incomplete")
        except Exception as e:
            errors.append(f"Plugin get_metadata method failed: {str(e)}")

        try:
            phase_i_compliant = plugin.is_phase_i_compliant()
            if not isinstance(phase_i_compliant, bool):
                errors.append("is_phase_i_compliant method must return a boolean")
        except Exception as e:
            errors.append(f"Plugin is_phase_i_compliant method failed: {str(e)}")

        # Check specific interface methods based on plugin type
        if isinstance(plugin, RendererPlugin):
            errors.extend(PluginValidator._validate_renderer_plugin(plugin))
        elif isinstance(plugin, ValidatorPlugin):
            errors.extend(PluginValidator._validate_validator_plugin(plugin))
        elif isinstance(plugin, CommandPlugin):
            errors.extend(PluginValidator._validate_command_plugin(plugin))
        elif isinstance(plugin, ThemePlugin):
            errors.extend(PluginValidator._validate_theme_plugin(plugin))

        return len(errors) == 0, errors

    @staticmethod
    def _validate_renderer_plugin(plugin: RendererPlugin) -> List[str]:
        """Validate RendererPlugin interface implementation"""
        errors = []
        try:
            result = plugin.render_output("test")
            if not isinstance(result, str):
                errors.append("render_output method must return a string")
        except Exception as e:
            errors.append(f"render_output method failed: {str(e)}")

        try:
            result = plugin.supports_format("test")
            if not isinstance(result, bool):
                errors.append("supports_format method must return a boolean")
        except Exception as e:
            errors.append(f"supports_format method failed: {str(e)}")

        return errors

    @staticmethod
    def _validate_validator_plugin(plugin: ValidatorPlugin) -> List[str]:
        """Validate ValidatorPlugin interface implementation"""
        errors = []
        try:
            result = plugin.validate("test")
            if not isinstance(result, tuple) or len(result) != 2:
                errors.append("validate method must return a tuple of (bool, str)")
            elif not isinstance(result[0], bool) or not isinstance(result[1], str):
                errors.append("validate method must return (bool, str)")
        except Exception as e:
            errors.append(f"validate method failed: {str(e)}")

        try:
            result = plugin.get_validation_rules()
            if not isinstance(result, list):
                errors.append("get_validation_rules method must return a list")
        except Exception as e:
            errors.append(f"get_validation_rules method failed: {str(e)}")

        return errors

    @staticmethod
    def _validate_command_plugin(plugin: CommandPlugin) -> List[str]:
        """Validate CommandPlugin interface implementation"""
        errors = []
        try:
            result = plugin.get_commands()
            if not isinstance(result, dict):
                errors.append("get_commands method must return a dictionary")
        except Exception as e:
            errors.append(f"get_commands method failed: {str(e)}")

        try:
            result = plugin.can_handle_command("test")
            if not isinstance(result, bool):
                errors.append("can_handle_command method must return a boolean")
        except Exception as e:
            errors.append(f"can_handle_command method failed: {str(e)}")

        return errors

    @staticmethod
    def _validate_theme_plugin(plugin: ThemePlugin) -> List[str]:
        """Validate ThemePlugin interface implementation"""
        errors = []
        try:
            result = plugin.get_theme_config()
            if not isinstance(result, dict):
                errors.append("get_theme_config method must return a dictionary")
        except Exception as e:
            errors.append(f"get_theme_config method failed: {str(e)}")

        try:
            result = plugin.apply_theme("test")
            if not isinstance(result, str):
                errors.append("apply_theme method must return a string")
        except Exception as e:
            errors.append(f"apply_theme method failed: {str(e)}")

        return errors

    @staticmethod
    def validate_phase_i_compliance(plugin: BasePlugin) -> tuple[bool, List[str]]:
        """
        Validate that a plugin complies with Phase I constraints (T178)
        """
        errors = []

        # Check if plugin claims to be Phase I compliant
        try:
            is_compliant = plugin.is_phase_i_compliant()
            if not is_compliant:
                errors.append("Plugin does not claim to be Phase I compliant")
        except Exception as e:
            errors.append(f"is_phase_i_compliant method failed: {str(e)}")

        return len(errors) == 0, errors

    @staticmethod
    def validate_plugin(plugin: BasePlugin) -> tuple[bool, List[str]]:
        """
        Complete validation of a plugin including interface and Phase I compliance
        """
        interface_valid, interface_errors = PluginValidator.validate_plugin_interface(plugin)
        compliance_valid, compliance_errors = PluginValidator.validate_phase_i_compliance(plugin)

        all_errors = interface_errors + compliance_errors
        return interface_valid and compliance_valid, all_errors