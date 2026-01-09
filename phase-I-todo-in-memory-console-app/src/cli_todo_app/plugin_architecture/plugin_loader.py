"""
Plugin Loader for CLI Todo Application
Implements T174: Plugin loader from designated directory
"""
import os
import sys
import importlib
import importlib.util
from pathlib import Path
from typing import List, Dict, Any, Optional, Type
from dataclasses import dataclass
import logging
from .plugin_interface import BasePlugin


@dataclass
class PluginInfo:
    """Information about a loaded plugin"""
    name: str
    path: str
    plugin_class: Type[BasePlugin]
    loaded_successfully: bool
    error_message: Optional[str] = None


class PluginLoader:
    """
    Loads plugins from a designated directory (T174)
    """

    def __init__(self, plugin_directory: Optional[str] = None):
        self.plugin_directory = plugin_directory or "./plugins"
        self._loaded_plugins: Dict[str, BasePlugin] = {}
        self._plugin_infos: List[PluginInfo] = []
        self._failed_plugins: List[PluginInfo] = []

    def discover_plugins(self) -> List[PluginInfo]:
        """
        Discover plugins in the designated directory
        """
        if not os.path.exists(self.plugin_directory):
            logging.info(f"Plugin directory {self.plugin_directory} does not exist, creating it")
            os.makedirs(self.plugin_directory, exist_ok=True)
            return []

        plugin_infos = []
        plugin_dir_path = Path(self.plugin_directory)

        # Look for Python files in the plugin directory
        for file_path in plugin_dir_path.glob("*.py"):
            if file_path.name.startswith("__"):
                continue  # Skip __init__.py and other special files

            plugin_name = file_path.stem
            plugin_info = PluginInfo(
                name=plugin_name,
                path=str(file_path),
                plugin_class=None,
                loaded_successfully=False
            )
            plugin_infos.append(plugin_info)

        return plugin_infos

    def load_plugin(self, plugin_path: str) -> Optional[BasePlugin]:
        """
        Load a single plugin from the given path
        """
        try:
            # Add the plugin directory to the Python path temporarily
            plugin_dir = os.path.dirname(plugin_path)
            if plugin_dir not in sys.path:
                sys.path.insert(0, plugin_dir)

            # Import the module
            spec = importlib.util.spec_from_file_location(
                os.path.basename(plugin_path)[:-3],  # Remove .py extension
                plugin_path
            )
            if spec is None or spec.loader is None:
                logging.error(f"Could not load plugin from {plugin_path}")
                return None

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Look for plugin classes in the module
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type) and
                    issubclass(attr, BasePlugin) and
                    attr != BasePlugin
                ):
                    # Found a plugin class, instantiate it
                    plugin_instance = attr()
                    return plugin_instance

            logging.warning(f"No plugin class found in {plugin_path}")
            return None

        except Exception as e:
            logging.error(f"Failed to load plugin from {plugin_path}: {str(e)}")
            return None

    def load_all_plugins(self) -> List[BasePlugin]:
        """
        Load all plugins from the designated directory (T176)
        """
        plugin_infos = self.discover_plugins()
        loaded_plugins = []

        for plugin_info in plugin_infos:
            plugin_instance = self.load_plugin(plugin_info.path)

            if plugin_instance is not None:
                # Validate that the plugin is Phase I compliant
                if plugin_instance.is_phase_i_compliant():
                    plugin_info.plugin_class = type(plugin_instance)
                    plugin_info.loaded_successfully = True
                    self._loaded_plugins[plugin_info.name] = plugin_instance
                    loaded_plugins.append(plugin_instance)
                else:
                    # Plugin is not Phase I compliant
                    plugin_info.loaded_successfully = False
                    plugin_info.error_message = "Plugin is not Phase I compliant"
                    self._failed_plugins.append(plugin_info)
                    logging.warning(f"Plugin {plugin_info.name} is not Phase I compliant and was not loaded")
            else:
                # Plugin failed to load
                plugin_info.loaded_successfully = False
                plugin_info.error_message = f"Failed to load plugin from {plugin_info.path}"
                self._failed_plugins.append(plugin_info)
                logging.error(f"Failed to load plugin: {plugin_info.name}")

        return loaded_plugins

    def get_loaded_plugins(self) -> Dict[str, BasePlugin]:
        """
        Get all successfully loaded plugins
        """
        return self._loaded_plugins.copy()

    def get_failed_plugins(self) -> List[PluginInfo]:
        """
        Get information about failed plugins (T177)
        """
        return self._failed_plugins.copy()

    def get_all_plugins(self) -> Dict[str, BasePlugin]:
        """
        Get all plugins (both loaded and failed)
        """
        all_plugins = self._loaded_plugins.copy()
        for failed_plugin in self._failed_plugins:
            if failed_plugin.name not in all_plugins:
                all_plugins[failed_plugin.name] = None
        return all_plugins