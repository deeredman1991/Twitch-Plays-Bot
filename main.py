import os
import time
import faulthandler

os.environ.setdefault('KIVY_NO_CONFIG', '1')

os.makedirs('logs', exist_ok=True)
os.makedirs('kivy_logs', exist_ok=True)

_DEBUG_PATH = os.path.join(os.getcwd(), 'startup_debug.out')


def _dbg(msg):
    try:
        with open(_DEBUG_PATH, 'a', encoding='utf-8') as f:
            f.write('{}\t{}\n'.format(time.time(), msg))
    except Exception:
        pass


try:
    faulthandler.enable(open(_DEBUG_PATH, 'a', encoding='utf-8'))
except Exception:
    pass

_dbg('startup')

from kivy.config import Config
Config.set('kivy', 'log_enable', '1')
Config.set('kivy', 'log_level', 'debug')
Config.set('kivy', 'log_name', 'log_%y-%m-%d_%_.out')
Config.set('kivy', 'log_dir', 'kivy_logs')
Config.set('graphics', 'resizable', False)
Config.set('graphics', 'width', '1920')
Config.set('graphics', 'height', '1080')

try:
    if Config.has_section('input'):
        for key, _ in list(Config.items('input')):
            if key.lower().startswith('tuio'):
                Config.remove_option('input', key)
except Exception:
    pass

from pathlib import Path
from kivy.logger import Logger
from kivy.app import App
from kivy.core.window import Window
from kivy.utils import platform as PLATFORM
from scripts.screen_manager import ScreenManager
import threading
import traceback

# Constants
MAX_WIDTH = 1920
MIN_WIDTH = 1280
DEFAULT_SIZE = (1920, 1080)

# Configuration
CONFIG = {
   'graphics': {
       'width': '1920',
       'height': '1080',
       'resizable': '0',
   },
   'icons': {
       '16': 'images/icons/icon-16.png',
       '24': 'images/icons/icon-24.png',
       '32': 'images/icons/icon-32.png',
       '48': 'images/icons/icon-48.png',
       '64': 'images/icons/icon-64.png',
       '128': 'images/icons/icon-128.png',
       '256': 'images/icons/icon-256.png',
       '512': 'images/icons/icon-256.png',
   },
}

class GameApp(App):
    def build(self):
        _dbg('build()')
        Logger.info('Running - build()')

        # Set the window size to 1080p
        Config.set('graphics', 'width', CONFIG['graphics']['width'])
        Config.set('graphics', 'height', CONFIG['graphics']['height'])
        Window.size = (int(CONFIG['graphics']['width']), int(CONFIG['graphics']['height']))

        self.title = 'Twitch Plays Bot'

        def load_icons():
            icons = {size: Path(path) for size, path in CONFIG['icons'].items()}
            self.icon = next((str(Path(icons[size])) for size in ('256', '64', '48', '32', '24', '16') if Path(icons[size]).exists()), None)

        icon_thread = threading.Thread(target=load_icons)
        icon_thread.daemon = True
        icon_thread.start()

        _r = ScreenManager()
        return _r

if __name__ == "__main__":
   try:
       _dbg('run() begin')
       GAMEAPP = GameApp()
       GAMEAPP.run()
       _dbg('run() end')
   except IOError as e:
       Logger.exception("IO Error occurred")
       _dbg('IOError: {}'.format(e))
       traceback.print_exc()
   except AttributeError as e:
       Logger.exception("Attribute Error occurred")
       _dbg('AttributeError: {}'.format(e))
       traceback.print_exc()
   except SystemExit:
       _dbg('SystemExit')
       pass
   except Exception as e:
       Logger.exception("An unexpected error occurred")
       _dbg('Exception: {}'.format(e))
       traceback.print_exc()
   finally:
       _dbg('finally')
       quit()