from scripts.plugin_system import PluginBase


class Plugin(PluginBase):
    plugin_id = 'example.hello'
    name = 'Hello Example'
    version = '1.0.0'

    def on_load(self, api):
        api.subscribe('app_started', self._on_app_started)
        api.subscribe('screen_manager_ready', self._on_screen_manager_ready)
        api.subscribe('session_started', self._on_session_started)

    def _on_app_started(self, **payload):
        print('[Plugin:Hello] app_started')

    def _on_screen_manager_ready(self, screen_manager=None, **payload):
        print('[Plugin:Hello] screen_manager_ready:', type(screen_manager))

    def _on_session_started(self, commands_manager=None, profile=None, **payload):
        print('[Plugin:Hello] session_started profile=%s commands_manager=%s' % (profile, type(commands_manager)))
