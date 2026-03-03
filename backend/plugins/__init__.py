"""Plugin system for Flask app."""

import importlib
import importlib.util
import os
import sys
from pathlib import Path


class PluginManager:
    """Manages plugin lifecycle: discovery, loading, and unloading."""

    def __init__(self, plugins_dir: str):
        self.plugins_dir = Path(plugins_dir)
        self.loaded_plugins = {}
        self.plugin_instances = {}

    def discover(self):
        """Discover available plugins in the plugins directory."""
        if not self.plugins_dir.exists():
            print(f"[PluginManager] Plugins directory not found: {self.plugins_dir}")
            return []

        plugins = []
        for file in self.plugins_dir.iterdir():
            if (
                file.suffix == ".py"
                and file.name != "__init__.py"
                and not file.name.startswith("_")
            ):
                plugins.append(file.stem)
        return plugins

    def load(self, app=None):
        """Load all discovered plugins, calling their on_load hooks."""
        plugin_names = self.discover()

        for name in plugin_names:
            try:
                spec = importlib.util.spec_from_file_location(
                    name, self.plugins_dir / f"{name}.py"
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[f"plugins.{name}"] = module
                    spec.loader.exec_module(module)

                    self.loaded_plugins[name] = module

                    if hasattr(module, "on_load"):
                        if app:
                            result = module.on_load(app)
                        else:
                            result = module.on_load()
                        print(f"[PluginManager] Loaded plugin: {name}")
                    else:
                        print(f"[PluginManager] Loaded plugin (no on_load): {name}")

                    self.plugin_instances[name] = module

            except Exception as e:
                print(f"[PluginManager] Failed to load plugin '{name}': {e}")

    def unload(self, name: str):
        """Unload a specific plugin."""
        if name in self.loaded_plugins:
            module = self.loaded_plugins[name]

            if hasattr(module, "on_unload"):
                try:
                    module.on_unload()
                except Exception as e:
                    print(f"[PluginManager] Error during on_unload for '{name}': {e}")

            del self.loaded_plugins[name]
            if name in self.plugin_instances:
                del self.plugin_instances[name]

            if f"plugins.{name}" in sys.modules:
                del sys.modules[f"plugins.{name}"]

            print(f"[PluginManager] Unloaded plugin: {name}")

    def unload_all(self):
        """Unload all loaded plugins."""
        for name in list(self.loaded_plugins.keys()):
            self.unload(name)

    def get_plugin(self, name: str):
        """Get a loaded plugin module by name."""
        return self.plugin_instances.get(name)

    def list_loaded(self):
        """Return list of loaded plugin names."""
        return list(self.loaded_plugins.keys())
