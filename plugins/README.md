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
- [Working Example: WH40K Rogue Trader](#working-example-wh40k-rogue-trader)

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

## Working Example: WH40K Rogue Trader

This repo includes a full featured "command pack" plugin for **Warhammer 40,000: Rogue Trader**.

Use it as the reference implementation for:

- Manifest plugin layout (`plugin.json` + `plugin.py`)
- Subscribing to lifecycle events (installs commands on `session_started`)
- Per-plugin configuration (`configs/plugins/<plugin_id>.json`)
- Exposing plugin settings in the app UI (Settings -> Bindings)

### Files / locations

- Plugin folder: `plugins/warhammer_rogue_trader/`
- Manifest: `plugins/warhammer_rogue_trader/plugin.json`
- Entry code: `plugins/warhammer_rogue_trader/plugin.py`
- UI integration: `screens/settings.py` (Bindings -> Rogue Trader)
- Config file: `configs/plugins/games.rogue_trader.json`

### What it does

On `session_started`, the plugin installs a set of Twitch chat commands into the active profile's `user_commands.json`.

These commands are designed around the bot's existing internal primitives:

- `:tilt` (analog stick)
- `:mash` (buttons)
- `:hat` (d-pad)

The command set is prefixed (default: `rt`) to avoid collisions.

### Event subscription pattern

In `plugin.py`, the plugin subscribes during `on_load`:

```python
def on_load(self, api):
    api.subscribe("session_started", self._on_session_started)
```

Then receives `commands_manager` when a session begins:

```python
def _on_session_started(self, commands_manager=None, profile=None, **payload):
    # install into commands_manager.configs['user_commands'] via commands_manager.set_config(...)
    pass
```

### Per-plugin config

The plugin reads configuration from:

`configs/plugins/games.rogue_trader.json`

Core keys:

- `prefix`: prefix used for installed commands (default `rt`)
- `overwrite_existing`: if true, re-install will overwrite existing `user_commands` keys
- `auto_install`: if true, installs on `session_started`
- `groups`: toggles groups of commands (movement/camera/ui/combat/safety)
- `defaults`: timing defaults used by the command pack

Advanced customization:

- `custom_commands`: dict mapping `chat_command -> internal_command`
- `custom_command_labels`: dict mapping `chat_command -> description` (used by the UI table)

The `custom_commands` format supports a `{p}` placeholder in the chat command key (e.g. `!{p}_u`).

### UI settings integration

The Settings screen includes a game-specific sub-tab:

- **Settings -> Bindings -> Rogue Trader**

It allows you to edit:

- Prefix and behavior toggles
- Group toggles
- Default timings
- Full command mapping table (Chat Command / Internal Command / Label)

Changes are persisted to the plugin config JSON via `PluginAPI`.

### Packaging note (PyInstaller)

If you bundle this bot into a PyInstaller `.exe` and rely on controller backends that require native DLLs (e.g. `ViGEmClient.dll`), you must:

- Bundle the DLL with PyInstaller (use `--add-binary`), and
- Ensure runtime lookup searches PyInstaller's extraction directory (`sys._MEIPASS`).

See `scripts/vigem.py` for the reference DLL discovery pattern.

## Included Plugin: WH40K Rogue Trader Command Pack

This plugin is documented above in [Working Example: WH40K Rogue Trader](#working-example-wh40k-rogue-trader).
