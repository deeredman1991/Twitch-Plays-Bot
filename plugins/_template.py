from scripts.plugin_system import PluginBase


class Plugin(PluginBase):
    plugin_id = 'yourname.plugin'
    name = 'Plugin Name'
    version = '0.1.0'

    def on_load(self, api):
        api.subscribe('app_started', self.on_app_started)
        api.subscribe('screen_manager_ready', self.on_screen_manager_ready)
        api.subscribe('session_started', self.on_session_started)

    def on_unload(self, api):
        pass

    def on_app_started(self, app=None, **payload):
        pass

    def on_screen_manager_ready(self, screen_manager=None, **payload):
        pass

    def on_session_started(self, commands_manager=None, profile=None, screen=None, **payload):
        pass
