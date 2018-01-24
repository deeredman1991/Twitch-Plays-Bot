""" This is the main module; where everything begins.
"""

import os
from pathlib import Path
import random

from kivy.app import App
from kivy.core.window import Window
from kivy.config import Config
from kivy.utils import platform as PLATFORM

from scripts.screen_manager import ScreenManager
from scripts.logger import LOGGER

class GameApp(App):
    """The GameApp class which contains the game.

        #TODO: doctest here
    """
    def build(self):
        """ Method gets called by Python start, run() and before on_start()
                see https://kivy.org/docs/guide/basic.html

            #TODO: doctest here
        """
        LOGGER.info('%s: Running - %s.build()', __file__, self)

        #FIXME: Window.size gets set to a random size for debugging but
        #   before release the window should have a default size and
        #   should also save it's size on_resize() to a file and then
        #   load in those settings.
        _x, _y = random.randint(500, 1000), random.randint(500, 1000)
        LOGGER.debug(
            '%s: In: %s.build() | Declared - _x, _y = %s(%d), %s(%d)',
            __file__, self, type(_x), _x, type(_y), _y)
        LOGGER.debug(
            '%s: In: %s.build() | Setting - %s(%s).size = %s(%d), %s(%d)',
            __file__, self, type(Window), Window, type(_x), _x, type(_y), _y)
        Window.size = (random.randint(500, 1000), random.randint(500, 1000))
        #Window.size = (300, 500)

        #Sets the title of the application window.
        self.title = 'Twitch Plays Bot'
        LOGGER.debug(
            '%(file)s: In: %(self)s.build() | Setting - '\
            '%(self)s.title=%(title_type)s(%(title)s)',
            {
                'file': __file__,
                'self': self,
                'title_type': type(self.title),
                'title': self.title
            })

        #Declares a dictionary to hold icon file path objects.
        icons = {
            '16': Path('images/icons/icon-16.png'),
            '24': Path('images/icons/icon-24.png'),
            '32': Path('images/icons/icon-32.png'),
            '48': Path('images/icons/icon-48.png'),
            '64': Path('images/icons/icon-64.png'),
            '128': Path('images/icons/icon-128.png'),
            '256': Path('images/icons/icon-256.png'),
            '512': Path('images/icons/icon-256.png'),
        }
        LOGGER.debug(
            '%s: In: %s.build() | Declared - icons = %s', __file__, self, icons)

        #Iterates over the icons list and log each element seperately.
        for key, value in icons.items():
            LOGGER.debug(
                '%s: In: %s.build() | icons[\'%s\'] = %s(%s)',
                __file__, self, key, type(value), value)

        #Trys to determine the size an icon should be based on the os.
        if  icons['256'].is_file() and PLATFORM == 'linux' or PLATFORM == 'macosx':
            #Sets the icon for the window to the 256x256 version.
            self.icon = str(icons['256'])
        elif icons['32'].is_file():
            #Sets the icon for the window to the 32x32 version.
            self.icon = str(icons['32'])
        else:
            #Sets the icon for the window to the first available version.
            for icon in icons.items():
                if icon.is_file():
                    self.icon = str(icon)
        LOGGER.debug(
            '%(file)s: In: %(self)s.build() | Setting - %(self)s.icon = '\
            '%(icon_type)s(%(icon)s)',
            {
                'file': __file__,
                'self': self,
                'icon_type': type(self.icon),
                'icon': self.icon
            })

        #Creates a ScreenManager that will hold all our screens
        #   i.e. MainMenu(), TwitchPlaysSession(), etc..etc..
        _r = ScreenManager()
        LOGGER.info('%s: In: %s.build() | Returning - %s(%s)',
                    __file__,
                    self,
                    type(_r),
                    _r)

        #Returns the ScreenManager mentioned earlier.
        return _r

if __name__ == "__main__":
    #Sets the logdir #TODO: mode this action to the custom logger module.
    LOG_DIR = os.path.dirname(os.path.abspath(__file__)) + '\\logs'
    Config.set('kivy', 'log_dir', LOG_DIR)

    #Reads the kivy_config.ini file? #TODO: This might not work...find out.
    Config.read('kivy_config.ini')

    LOGGER.info('%s: In: __main__ | Finished Configuring - Starting Logging.',
                __file__)

    #Declares a variable to hold the current working directory.
    CURRENT_WORKING_DIRECTORY = os.getcwd()
    LOGGER.debug('%s: In: __main__ | Declared - CURRENT_WORKING_DIRECTORY ='\
                 ' %s', __file__, CURRENT_WORKING_DIRECTORY)

    #Sets kivy's home to the current worlding directory.
    os.environ['KIVY_HOME'] = CURRENT_WORKING_DIRECTORY
    LOGGER.debug('%s: In: __main__ | Setting - %s.environ[\'KIVY_HOME\'] = '\
                 '%s', __file__, os, CURRENT_WORKING_DIRECTORY)

    #Prints the os's environment variables to the logfile.
    LOGGER.debug('%s: In: __main__ | Check - os.environ = %s(%s)',
                 __file__, type(os.environ), os.environ)

    #Creates a GameApp object defined above.
    GAMEAPP = GameApp()
    LOGGER.debug('%s: In: __main__ | Declared - GAMEAPP = %s',
                 __file__, GAMEAPP)

    #Calls GAMEAPP's run method which calls GAMEAPP.build().
    LOGGER.info('%s: In: __main__ | Calling - %s.run().',
                __file__, GAMEAPP)
    GAMEAPP.run()

    #Gracefully exits python.
    LOGGER.info('%s: In: __main__ | Calling - quit().', __file__)
    quit()
