"""
Tests for Plugin Architecture Components
Testing the Plugin Architecture tasks: T170-T178
"""
import unittest
import tempfile
import os
from pathlib import Path
from typing import Dict, Any
from src.plugin_architecture.plugin_interface import (
    BasePlugin, RendererPlugin, ValidatorPlugin,
    CommandPlugin, ThemePlugin, PluginMetadata
)
from src.plugin_architecture.plugin_loader import PluginLoader, PluginInfo
from src.plugin_architecture.plugin_validator import PluginValidator


class MockPlugin(BasePlugin):
    """Mock plugin for testing"""

    def __init__(self, name: str = "test", version: str = "1.0.0", compliant: bool = True):
        self._name = name
        self._version = version
        self._compliant = compliant

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name=self._name,
            version=self._version,
            author="test",
            description="test plugin",
            phase_i_compliant=self._compliant
        )

    def is_phase_i_compliant(self) -> bool:
        return self._compliant


class MockRendererPlugin(RendererPlugin):
    """Mock renderer plugin for testing"""

    def __init__(self):
        self._name = "test_renderer"
        self._version = "1.0.0"

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name=self._name,
            version=self._version,
            author="test",
            description="test renderer plugin",
            phase_i_compliant=True
        )

    def is_phase_i_compliant(self) -> bool:
        return True

    def render_output(self, data: Any, context=None) -> str:
        return f"Rendered: {str(data)}"

    def supports_format(self, format_type: str) -> bool:
        return format_type == "test"


class MockValidatorPlugin(ValidatorPlugin):
    """Mock validator plugin for testing"""

    def __init__(self):
        self._name = "test_validator"
        self._version = "1.0.0"

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name=self._name,
            version=self._version,
            author="test",
            description="test validator plugin",
            phase_i_compliant=True
        )

    def is_phase_i_compliant(self) -> bool:
        return True

    def validate(self, data: Any, context=None) -> tuple[bool, str]:
        return True, "Valid"

    def get_validation_rules(self) -> list[str]:
        return ["rule1", "rule2"]


class MockCommandPlugin(CommandPlugin):
    """Mock command plugin for testing"""

    def __init__(self):
        self._name = "test_command"
        self._version = "1.0.0"

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name=self._name,
            version=self._version,
            author="test",
            description="test command plugin",
            phase_i_compliant=True
        )

    def is_phase_i_compliant(self) -> bool:
        return True

    def get_commands(self) -> Dict[str, callable]:
        return {"test_cmd": lambda: "test"}

    def can_handle_command(self, command: str) -> bool:
        return command == "test_cmd"


class MockThemePlugin(ThemePlugin):
    """Mock theme plugin for testing"""

    def __init__(self):
        self._name = "test_theme"
        self._version = "1.0.0"

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name=self._name,
            version=self._version,
            author="test",
            description="test theme plugin",
            phase_i_compliant=True
        )

    def is_phase_i_compliant(self) -> bool:
        return True

    def get_theme_config(self) -> Dict[str, Any]:
        return {"color": "blue"}

    def apply_theme(self, content: str) -> str:
        return f"[THEMED] {content}"


class TestBasePlugin(unittest.TestCase):
    """Test base plugin functionality (T170-T173)"""

    def test_base_plugin_abstract_methods(self):
        """Test that base plugin has required abstract methods"""
        plugin = MockPlugin()

        metadata = plugin.get_metadata()
        self.assertIsInstance(metadata, PluginMetadata)
        self.assertEqual(metadata.name, "test")

        compliant = plugin.is_phase_i_compliant()
        self.assertTrue(compliant)

    def test_non_compliant_plugin(self):
        """Test plugin that is not Phase I compliant"""
        plugin = MockPlugin(compliant=False)
        compliant = plugin.is_phase_i_compliant()
        self.assertFalse(compliant)


class TestRendererPlugin(unittest.TestCase):
    """Test renderer plugin interface (T170)"""

    def test_renderer_interface_implementation(self):
        """Test renderer plugin interface methods"""
        plugin = MockRendererPlugin()

        # Test render_output
        result = plugin.render_output("test data")
        self.assertEqual(result, "Rendered: test data")

        # Test supports_format
        result = plugin.supports_format("test")
        self.assertTrue(result)

        result = plugin.supports_format("other")
        self.assertFalse(result)

        # Test metadata
        metadata = plugin.get_metadata()
        self.assertEqual(metadata.name, "test_renderer")

        # Test Phase I compliance
        compliant = plugin.is_phase_i_compliant()
        self.assertTrue(compliant)


class TestValidatorPlugin(unittest.TestCase):
    """Test validator plugin interface (T171)"""

    def test_validator_interface_implementation(self):
        """Test validator plugin interface methods"""
        plugin = MockValidatorPlugin()

        # Test validate
        is_valid, message = plugin.validate("test data")
        self.assertTrue(is_valid)
        self.assertEqual(message, "Valid")

        # Test get_validation_rules
        rules = plugin.get_validation_rules()
        self.assertEqual(rules, ["rule1", "rule2"])

        # Test metadata
        metadata = plugin.get_metadata()
        self.assertEqual(metadata.name, "test_validator")

        # Test Phase I compliance
        compliant = plugin.is_phase_i_compliant()
        self.assertTrue(compliant)


class TestCommandPlugin(unittest.TestCase):
    """Test command plugin interface (T172)"""

    def test_command_interface_implementation(self):
        """Test command plugin interface methods"""
        plugin = MockCommandPlugin()

        # Test get_commands
        commands = plugin.get_commands()
        self.assertIn("test_cmd", commands)
        self.assertTrue(callable(commands["test_cmd"]))

        # Test can_handle_command
        can_handle = plugin.can_handle_command("test_cmd")
        self.assertTrue(can_handle)

        can_handle = plugin.can_handle_command("other_cmd")
        self.assertFalse(can_handle)

        # Test metadata
        metadata = plugin.get_metadata()
        self.assertEqual(metadata.name, "test_command")

        # Test Phase I compliance
        compliant = plugin.is_phase_i_compliant()
        self.assertTrue(compliant)


class TestThemePlugin(unittest.TestCase):
    """Test theme plugin interface (T173)"""

    def test_theme_interface_implementation(self):
        """Test theme plugin interface methods"""
        plugin = MockThemePlugin()

        # Test get_theme_config
        config = plugin.get_theme_config()
        self.assertIn("color", config)
        self.assertEqual(config["color"], "blue")

        # Test apply_theme
        themed = plugin.apply_theme("test content")
        self.assertEqual(themed, "[THEMED] test content")

        # Test metadata
        metadata = plugin.get_metadata()
        self.assertEqual(metadata.name, "test_theme")

        # Test Phase I compliance
        compliant = plugin.is_phase_i_compliant()
        self.assertTrue(compliant)


class TestPluginValidator(unittest.TestCase):
    """Test plugin validation functionality (T175, T178)"""

    def test_validate_renderer_plugin_interface(self):
        """Test validation of renderer plugin interface"""
        plugin = MockRendererPlugin()
        is_valid, errors = PluginValidator.validate_plugin_interface(plugin)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_validate_validator_plugin_interface(self):
        """Test validation of validator plugin interface"""
        plugin = MockValidatorPlugin()
        is_valid, errors = PluginValidator.validate_plugin_interface(plugin)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_validate_command_plugin_interface(self):
        """Test validation of command plugin interface"""
        plugin = MockCommandPlugin()
        is_valid, errors = PluginValidator.validate_plugin_interface(plugin)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_validate_theme_plugin_interface(self):
        """Test validation of theme plugin interface"""
        plugin = MockThemePlugin()
        is_valid, errors = PluginValidator.validate_plugin_interface(plugin)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_validate_phase_i_compliance(self):
        """Test Phase I compliance validation (T178)"""
        plugin = MockPlugin()
        is_compliant, errors = PluginValidator.validate_phase_i_compliance(plugin)
        self.assertTrue(is_compliant)
        self.assertEqual(len(errors), 0)

    def test_complete_plugin_validation(self):
        """Test complete plugin validation (T175)"""
        plugin = MockRendererPlugin()
        is_valid, errors = PluginValidator.validate_plugin(plugin)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)


class TestPluginLoader(unittest.TestCase):
    """Test plugin loader functionality (T174, T176, T177)"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.loader = PluginLoader(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_discover_plugins_empty_directory(self):
        """Test plugin discovery in empty directory"""
        plugin_infos = self.loader.discover_plugins()
        self.assertEqual(len(plugin_infos), 0)

    def test_load_all_plugins_empty_directory(self):
        """Test loading plugins from empty directory"""
        plugins = self.loader.load_all_plugins()
        self.assertEqual(len(plugins), 0)

    def test_get_loaded_plugins(self):
        """Test getting loaded plugins"""
        plugins = self.loader.get_loaded_plugins()
        self.assertEqual(len(plugins), 0)

    def test_get_failed_plugins(self):
        """Test getting failed plugins (T177)"""
        failed_plugins = self.loader.get_failed_plugins()
        # Initially should be empty since no plugins attempted to load
        self.assertEqual(len(failed_plugins), 0)

    def test_plugin_info_structure(self):
        """Test PluginInfo data structure"""
        info = PluginInfo(
            name="test",
            path="/path/to/test",
            plugin_class=MockPlugin,
            loaded_successfully=True
        )
        self.assertEqual(info.name, "test")
        self.assertEqual(info.path, "/path/to/test")
        self.assertEqual(info.plugin_class, MockPlugin)
        self.assertTrue(info.loaded_successfully)


class TestPluginArchitectureIntegration(unittest.TestCase):
    """Test plugin architecture integration scenarios (T170-T178)"""

    def test_full_plugin_workflow(self):
        """Test complete plugin workflow"""
        # Create a mock plugin
        renderer_plugin = MockRendererPlugin()

        # Validate the plugin
        is_valid, errors = PluginValidator.validate_plugin(renderer_plugin)
        self.assertTrue(is_valid, f"Plugin validation failed: {errors}")

        # Verify it meets interface requirements
        self.assertIsInstance(renderer_plugin, RendererPlugin)
        self.assertIsInstance(renderer_plugin, BasePlugin)

        # Test plugin functionality
        rendered = renderer_plugin.render_output("test")
        self.assertEqual(rendered, "Rendered: test")

        # Test Phase I compliance
        self.assertTrue(renderer_plugin.is_phase_i_compliant())

        # Test metadata
        metadata = renderer_plugin.get_metadata()
        self.assertIsInstance(metadata, PluginMetadata)
        self.assertEqual(metadata.name, "test_renderer")

    def test_plugin_type_validation(self):
        """Test validation of different plugin types"""
        plugins = [
            MockRendererPlugin(),
            MockValidatorPlugin(),
            MockCommandPlugin(),
            MockThemePlugin()
        ]

        for plugin in plugins:
            # Validate interface implementation
            is_valid, errors = PluginValidator.validate_plugin_interface(plugin)
            self.assertTrue(is_valid, f"Plugin {type(plugin).__name__} interface validation failed: {errors}")

            # Validate Phase I compliance
            is_compliant, errors = PluginValidator.validate_phase_i_compliance(plugin)
            self.assertTrue(is_compliant, f"Plugin {type(plugin).__name__} compliance validation failed: {errors}")

            # Validate complete plugin
            is_valid, errors = PluginValidator.validate_plugin(plugin)
            self.assertTrue(is_valid, f"Plugin {type(plugin).__name__} complete validation failed: {errors}")

    def test_plugin_metadata_consistency(self):
        """Test that all plugins have consistent metadata"""
        plugins = [
            MockRendererPlugin(),
            MockValidatorPlugin(),
            MockCommandPlugin(),
            MockThemePlugin()
        ]

        for plugin in plugins:
            metadata = plugin.get_metadata()
            self.assertIsInstance(metadata.name, str)
            self.assertIsInstance(metadata.version, str)
            self.assertIsInstance(metadata.author, str)
            self.assertIsInstance(metadata.description, str)
            self.assertIsInstance(metadata.phase_i_compliant, bool)

    def test_plugin_interface_contracts(self):
        """Test that plugins properly implement their interface contracts (T170-T173)"""
        # Test RendererPlugin contract
        renderer = MockRendererPlugin()
        self.assertTrue(hasattr(renderer, 'render_output'))
        self.assertTrue(hasattr(renderer, 'supports_format'))
        self.assertTrue(callable(renderer.render_output))
        self.assertTrue(callable(renderer.supports_format))

        # Test ValidatorPlugin contract
        validator = MockValidatorPlugin()
        self.assertTrue(hasattr(validator, 'validate'))
        self.assertTrue(hasattr(validator, 'get_validation_rules'))
        self.assertTrue(callable(validator.validate))
        self.assertTrue(callable(validator.get_validation_rules))

        # Test CommandPlugin contract
        command = MockCommandPlugin()
        self.assertTrue(hasattr(command, 'get_commands'))
        self.assertTrue(hasattr(command, 'can_handle_command'))
        self.assertTrue(callable(command.get_commands))
        self.assertTrue(callable(command.can_handle_command))

        # Test ThemePlugin contract
        theme = MockThemePlugin()
        self.assertTrue(hasattr(theme, 'get_theme_config'))
        self.assertTrue(hasattr(theme, 'apply_theme'))
        self.assertTrue(callable(theme.get_theme_config))
        self.assertTrue(callable(theme.apply_theme))


if __name__ == '__main__':
    unittest.main()