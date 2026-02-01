# Twitch Plays Bot Plugin System

This page documents how to create, install, configure, and debug plugins.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Plugin Formats](#plugin-formats)
  - [Single-file Plugin (Quick Start)](#single-file-plugin-quick-start)
  - [Manifest Plugin (Recommended)](#manifest-plugin-recommended)
- [Plugin Lifecycle](#plugin-lifecycle)
- [Events](#events)
- [PluginAPI Reference](#pluginapi-reference)
  - [Per-plugin Config](#per-plugin-config)
- [Enable / Disable Plugins](#enable--disable-plugins)
- [Error Handling & Debugging](#error-handling--debugging)
- [Best Practices](#best-practices)

## Overview

Plugins are Python modules loaded by the app at startup. They allow you to add features or modify behavior without changing core code.

Core implementation lives in:

- `scripts/plugin_system.py`

Plugins live in:

- `plugins/`

## Installation

1. Copy your plugin into the `plugins/` folder (see formats below).
2. Start the app.
3. Open **Settings -> Plugins**.

## Plugin Formats

### Single-file Plugin (Quick Start)

Create a file:

```
plugins/my_plugin.py
```

Your module should either:

- Provide a `Plugin` class (recommended), or
- Provide a `plugin` instance.

Example:

```python
from scripts.plugin_system import PluginBase


class Plugin(PluginBase):
    plugin_id = "yourname.my_plugin"
    name = "My Plugin"
    version = "1.0.0"

    def on_load(self, api):
        api.subscribe("app_started", self.on_app_started)

    def on_app_started(self, app=None, **payload):
        print("[MyPlugin] Loaded")
```

### Manifest Plugin (Recommended)

Manifest plugins are folders. They are discoverable without importing Python first, and they support metadata in `plugin.json`.

Folder layout:

```
plugins/my_plugin/
  plugin.json
  plugin.py
```

Example `plugin.json`:

```json
{
  "id": "yourname.my_plugin",
  "name": "My Plugin",
  "version": "1.0.0",
  "entry": "plugin.py"
}
```

Example `plugin.py`:

```python
from scripts.plugin_system import PluginBase


class Plugin(PluginBase):
    plugin_id = "yourname.my_plugin"
    name = "My Plugin"
    version = "1.0.0"

    def on_load(self, api):
        print("[MyPlugin] Loaded via manifest")
```

## Plugin Lifecycle

Your `Plugin` class can implement:

- `on_load(self, api)`
- `on_unload(self, api)`

Both are optional.

## Events

Subscribe with:

`api.subscribe("event_name", handler)`

Emit with:

`api.emit("event_name", **payload)`

### Event List

#### `app_started`

- Payload keys:
  - `app`

#### `screen_manager_ready`

- Payload keys:
  - `screen_manager`

#### `session_started`

- Payload keys:
  - `commands_manager`
  - `profile`
  - `screen`

#### `session_reset`

- Payload keys:
  - `commands_manager`
  - `profile`
  - `screen`

#### `app_stopping`

- Payload keys:
  - `app`

#### `plugin_loaded`

- Payload keys:
  - `plugin_id`
  - `info`

#### `plugin_unloaded`

- Payload keys:
  - `plugin_id`

#### `plugin_error`

- Payload keys:
  - `plugin_id`
  - `error`

## PluginAPI Reference

The `api` object passed into `on_load/on_unload` is a `PluginAPI`.

### Properties

- `api.app_root`
- `api.screen_manager` (available after `screen_manager_ready`)

### Methods

- `api.subscribe(event: str, handler: Callable[..., None])`
- `api.emit(event: str, **payload)`
- `api.get_configs_root() -> str`
- `api.get_profile_dir(profile: str) -> str`

### Per-plugin Config

Each plugin can store config at:

- `configs/plugins/<plugin_id>.json`

Helpers:

- `api.load_plugin_config(default: dict = None) -> dict`
- `api.save_plugin_config(data: dict) -> None`

Example:

```python
def on_load(self, api):
    cfg = api.load_plugin_config(default={"launch_count": 0})
    cfg["launch_count"] = int(cfg.get("launch_count", 0)) + 1
    api.save_plugin_config(cfg)
```

## Enable / Disable Plugins

Plugin enable state is persisted to:

- `configs/plugins/plugins_state.json`

UI:

- **Settings -> Plugins** uses an on/off **toggle switch**.

Important:

- Enabling/disabling currently **requires a restart** to apply.

## Error Handling & Debugging

- Plugin load errors are captured and stored on the plugin info (`PluginInfo.error`).
- In the UI (Settings -> Plugins), plugins with errors display `[ERROR]`.
- Use the **Details** button to surface the last line of the error in the status label.

## Best Practices

- Keep `plugin_id` globally unique (reverse-domain style is recommended).
- Prefer manifest plugins for distributable plugins.
- Avoid blocking work in event handlers (use threads if needed).
