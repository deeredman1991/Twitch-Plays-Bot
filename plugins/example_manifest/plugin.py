from scripts.plugin_system import PluginBase


class Plugin(PluginBase):
    plugin_id = 'example.manifest'
    name = 'Manifest Example'
    version = '1.0.0'

    def on_load(self, api):
        cfg = api.load_plugin_config(default={'enabled_message': 'Manifest plugin loaded'})
        print('[Plugin:Manifest]', cfg.get('enabled_message'))

        api.subscribe('session_started', self.on_session_started)

    def on_session_started(self, profile=None, **payload):
        print('[Plugin:Manifest] session_started profile=%s' % (profile,))
