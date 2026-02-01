import os
import sys
import json
import traceback
import importlib.util
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional


class EventBus:
    def __init__(self):
        self._handlers: Dict[str, List[Callable[..., None]]] = {}

    def subscribe(self, event: str, handler: Callable[..., None]) -> None:
        self._handlers.setdefault(event, []).append(handler)

    def emit(self, event: str, **payload: Any) -> None:
        for handler in list(self._handlers.get(event, [])):
            try:
                handler(**payload)
            except Exception:
                traceback.print_exc()


@dataclass
class PluginInfo:
    plugin_id: str
    name: str
    version: str
    module_path: str
    enabled: bool
    error: Optional[str] = None


class PluginAPI:
    def __init__(self, *, event_bus: EventBus, app_root: str, screen_manager=None, plugin_id: Optional[str] = None):
        self._event_bus = event_bus
        self._app_root = app_root
        self._screen_manager = screen_manager
        self._plugin_id = plugin_id

    @property
    def app_root(self) -> str:
        return self._app_root

    @property
    def screen_manager(self):
        return self._screen_manager

    def set_screen_manager(self, screen_manager) -> None:
        self._screen_manager = screen_manager

    def subscribe(self, event: str, handler: Callable[..., None]) -> None:
        self._event_bus.subscribe(event, handler)

    def emit(self, event: str, **payload: Any) -> None:
        self._event_bus.emit(event, **payload)

    def get_configs_root(self) -> str:
        return os.path.join(self._app_root, 'configs')

    def get_profile_dir(self, profile: str) -> str:
        return os.path.join(self.get_configs_root(), profile)

    def get_plugins_config_root(self) -> str:
        return os.path.join(self.get_configs_root(), 'plugins')

    def get_plugin_config_path(self, plugin_id: Optional[str] = None) -> str:
        pid = plugin_id or self._plugin_id
        if not pid:
            raise ValueError('plugin_id is required')
        safe = str(pid).replace('/', '_').replace('\\', '_')
        return os.path.join(self.get_plugins_config_root(), safe + '.json')

    def load_plugin_config(self, plugin_id: Optional[str] = None, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        path = self.get_plugin_config_path(plugin_id)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
        except Exception:
            pass
        return dict(default or {})

    def save_plugin_config(self, data: Dict[str, Any], plugin_id: Optional[str] = None) -> None:
        path = self.get_plugin_config_path(plugin_id)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp_path = path + '.tmp'
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)


class PluginBase:
    plugin_id: str = 'plugin'
    name: str = 'Plugin'
    version: str = '0.0.0'

    def on_load(self, api: PluginAPI) -> None:
        pass

    def on_unload(self, api: PluginAPI) -> None:
        pass


class PluginManager:
    def __init__(self, plugins_dir: str, *, app_root: Optional[str] = None):
        self.plugins_dir = plugins_dir
        self.app_root = app_root or os.getcwd()
        self.event_bus = EventBus()
        self.api = PluginAPI(event_bus=self.event_bus, app_root=self.app_root)
        self._plugins: Dict[str, PluginBase] = {}
        self._infos: Dict[str, PluginInfo] = {}
        self._load_errors: Dict[str, str] = {}
        self._plugin_modules: Dict[str, str] = {}

        self._state_path = os.path.join(self.app_root, 'configs', 'plugins', 'plugins_state.json')
        self._enabled_state: Dict[str, bool] = {}
        self._load_state()

    def _load_state(self) -> None:
        try:
            with open(self._state_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict):
                self._enabled_state = {str(k): bool(v) for k, v in data.items()}
        except Exception:
            self._enabled_state = {}

    def _save_state(self) -> None:
        os.makedirs(os.path.dirname(self._state_path), exist_ok=True)
        tmp_path = self._state_path + '.tmp'
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(self._enabled_state, f, ensure_ascii=False, indent=4)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, self._state_path)

    def is_enabled(self, plugin_id: str) -> bool:
        return self._enabled_state.get(str(plugin_id), True)

    def set_enabled(self, plugin_id: str, enabled: bool) -> None:
        self._enabled_state[str(plugin_id)] = bool(enabled)
        self._save_state()

    def errors(self) -> Dict[str, str]:
        return dict(self._load_errors)

    def set_screen_manager(self, screen_manager) -> None:
        self.api.set_screen_manager(screen_manager)

    def emit(self, event: str, **payload: Any) -> None:
        self.event_bus.emit(event, **payload)

    def plugins(self) -> Dict[str, PluginBase]:
        return dict(self._plugins)

    def infos(self) -> Dict[str, PluginInfo]:
        return dict(self._infos)

    def _iter_plugin_files(self) -> List[str]:
        if not os.path.isdir(self.plugins_dir):
            return []
        out: List[str] = []
        for name in os.listdir(self.plugins_dir):
            if name.startswith('_'):
                continue
            full = os.path.join(self.plugins_dir, name)
            if os.path.isdir(full):
                if os.path.isfile(os.path.join(full, 'plugin.json')):
                    out.append(full)
                continue
            if name.lower().endswith('.py'):
                out.append(full)
        return sorted(out)

    def _read_manifest(self, plugin_dir: str) -> Optional[Dict[str, Any]]:
        path = os.path.join(plugin_dir, 'plugin.json')
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
        except Exception:
            traceback.print_exc()
        return None

    def load_all(self) -> None:
        os.makedirs(self.plugins_dir, exist_ok=True)
        if self.plugins_dir not in sys.path:
            sys.path.insert(0, self.plugins_dir)

        for path in self._iter_plugin_files():
            self.load_from_path(path)

    def load_from_path(self, path: str) -> None:
        if os.path.isdir(path):
            manifest = self._read_manifest(path)
            if not manifest:
                return
            plugin_id = str(manifest.get('id') or os.path.basename(path))
            if not self.is_enabled(plugin_id):
                info = PluginInfo(
                    plugin_id=plugin_id,
                    name=str(manifest.get('name') or plugin_id),
                    version=str(manifest.get('version') or '0.0.0'),
                    module_path=path,
                    enabled=False,
                    error=None,
                )
                self._infos[plugin_id] = info
                return
            entry = str(manifest.get('entry') or 'plugin.py')
            module_path = os.path.join(path, entry)
            self.load_from_file(module_path, manifest_id=plugin_id, manifest=manifest)
            return

        if path.lower().endswith('.py'):
            self.load_from_file(path)

    def load_from_file(self, module_path: str, *, manifest_id: Optional[str] = None, manifest: Optional[Dict[str, Any]] = None) -> None:
        module_name = os.path.splitext(os.path.basename(module_path))[0]
        module_key = manifest_id or module_name

        if module_key in self._plugin_modules:
            return

        if manifest_id is not None and not self.is_enabled(manifest_id):
            info = PluginInfo(
                plugin_id=str(manifest_id),
                name=str((manifest or {}).get('name') or manifest_id),
                version=str((manifest or {}).get('version') or '0.0.0'),
                module_path=module_path,
                enabled=False,
                error=None,
            )
            self._infos[info.plugin_id] = info
            return

        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None or spec.loader is None:
            return
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception:
            err = traceback.format_exc()
            self._load_errors[module_key] = err
            traceback.print_exc()
            return

        plugin_obj = getattr(module, 'plugin', None)
        plugin_cls = getattr(module, 'Plugin', None)

        plugin: Optional[PluginBase] = None
        if isinstance(plugin_obj, PluginBase):
            plugin = plugin_obj
        elif callable(plugin_cls):
            try:
                plugin = plugin_cls()
            except Exception:
                traceback.print_exc()
                return

        if plugin is None:
            return

        plugin_id = manifest_id or getattr(plugin, 'plugin_id', module_name)
        if plugin_id in self._plugins:
            return

        info = PluginInfo(
            plugin_id=str(plugin_id),
            name=str(((manifest or {}).get('name')) or getattr(plugin, 'name', plugin_id)),
            version=str(((manifest or {}).get('version')) or getattr(plugin, 'version', '0.0.0')),
            module_path=module_path,
            enabled=self.is_enabled(str(plugin_id)),
            error=self._load_errors.get(module_key),
        )

        self._plugins[info.plugin_id] = plugin
        self._infos[info.plugin_id] = info
        self._plugin_modules[module_key] = module_name

        try:
            plugin_api = PluginAPI(
                event_bus=self.event_bus,
                app_root=self.app_root,
                screen_manager=self.api.screen_manager,
                plugin_id=str(info.plugin_id),
            )
            plugin.on_load(plugin_api)
        except Exception:
            err = traceback.format_exc()
            self._load_errors[info.plugin_id] = err
            traceback.print_exc()

        if info.plugin_id in self._load_errors:
            info.error = self._load_errors.get(info.plugin_id)
            self.emit('plugin_error', plugin_id=info.plugin_id, error=info.error)

        self.emit('plugin_loaded', plugin_id=info.plugin_id, info=info)

    def unload_all(self) -> None:
        for plugin_id, plugin in list(self._plugins.items()):
            try:
                plugin_api = PluginAPI(
                    event_bus=self.event_bus,
                    app_root=self.app_root,
                    screen_manager=self.api.screen_manager,
                    plugin_id=str(plugin_id),
                )
                plugin.on_unload(plugin_api)
            except Exception:
                traceback.print_exc()
            self.emit('plugin_unloaded', plugin_id=plugin_id)

        self._plugins.clear()
        self._infos.clear()
        self._plugin_modules.clear()
