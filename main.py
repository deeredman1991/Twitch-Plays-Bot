from kivy.config import Config
Config.set('graphics', 'resizable', False)
from pathlib import Path
from kivy.logger import Logger
from kivy.app import App
from kivy.core.window import Window
from kivy.utils import platform as PLATFORM
from scripts.screen_manager import ScreenManager
import threading

# Constants
MAX_WIDTH = 1280
MIN_WIDTH = 720
DEFAULT_SIZE = (1280, 720)

# Configuration
CONFIG = {
   'graphics': {
       'width': '1280',
       'height': '720',
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
        Logger.info('Running - build()')

        # Set the window size to 720p
        Config.set('graphics', 'width', CONFIG['graphics']['width'])
        Config.set('graphics', 'height', CONFIG['graphics']['height'])

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
       GAMEAPP = GameApp()
       GAMEAPP.run()
   except IOError as e:
       Logger.error(f"IO Error occurred: {e}")
   except AttributeError as e:
       Logger.error(f"Attribute Error occurred: {e}")
   except SystemExit:
       pass
   except Exception as e:
       Logger.error(f"An unexpected error occurred: {e}")
   finally:
       quit()