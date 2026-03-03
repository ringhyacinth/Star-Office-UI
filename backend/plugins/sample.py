"""Sample plugin demonstrating the plugin system."""


def on_load(app=None):
    """Called when the plugin is loaded."""
    print("[SamplePlugin] on_load called")
    if app:
        print(f"[SamplePlugin] Flask app instance: {app.name}")
    return {"status": "loaded", "plugin": "sample"}


def on_unload():
    """Called when the plugin is unloaded."""
    print("[SamplePlugin] on_unload called")
