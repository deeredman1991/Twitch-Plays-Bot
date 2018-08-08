""" This is the main module; where everything begins.
"""

import os

CURRENT_WORKING_DIRECTORY = os.getcwd()

#Sets kivy's home to the current worlding directory.
os.environ['KIVY_HOME'] = CURRENT_WORKING_DIRECTORY

from kivy.config import Config

from pathlib import Path
import random

from kivy.app import App
from kivy.core.window import Window
from kivy.config import Config
from kivy.utils import platform as PLATFORM
from kivy.logger import Logger

from scripts.screen_manager import ScreenManager

class GameApp(App):
    """The GameApp class which contains the game.

        #TODO: doctest here
    """
    def build(self):
        """ Method gets called by Python start, run() and before on_start()
                see https://kivy.org/docs/guide/basic.html

            #TODO: doctest here
        """
        Logger.info('Running - build()')

        #FIXME: Window.size gets set to a random size for debugging but
        #   before release the window should have a default size and
        #   should also save it's size on_resize() to a file and then
        #   load in those settings.
        _x, _y = random.randint(500, 1000), random.randint(500, 1000)
        Logger.debug('Declared - _x, _y = %s(%d), %s(%d)',
                     type(_x), _x, type(_y), _y)
        Logger.debug('Setting - %s(%s).size = %s(%d), %s(%d)',
                     type(Window), Window, type(_x), _x, type(_y), _y)
        Window.size = (random.randint(500, 1000), random.randint(500, 1000))
        #Window.size = (300, 500)

        #Sets the title of the application window.
        self.title = 'Twitch Plays Bot'
        Logger.debug('Setting - %s.title=%s(%s)',
                     self, type(self.title), self.title)

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
        Logger.debug('Declared - icons = %s(%s)', type(icons), icons)

        #Iterates over the icons list and logs each element seperately.
        for key, value in icons.items():
            Logger.debug('Iterating - icons[\'%4s\'] = %s(%s)',
                         key, type(value), value)

        #Trys to determine the size an icon should be based on the os.
        if  icons['256'].is_file() and PLATFORM == 'linux' or\
                                       PLATFORM == 'macosx':
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
        Logger.debug('Setting - %s.icon = %s(%s)',
                     self, type(self.icon), self.icon)

        #Creates a ScreenManager that will hold all our screens
        #   i.e. MainMenu(), TwitchPlaysSession(), etc..etc..
        _r = ScreenManager()
        Logger.info('Returning - %s(%s)', type(_r), _r)

        #Returns the ScreenManager mentioned earlier.
        return _r

if __name__ == "__main__":
    #TODO: Move these out to a config file.
    #Config.set('kivy', 'log_name', 'log_%y-%m-%d_%_.txt')
    #LOG_DIR = os.path.dirname(os.path.abspath(__file__)) + '\\logs'
    #Config.set('kivy', 'log_dir', LOG_DIR)

    #This function applies a monkey patch to the print statement so that it will never crash due to bad encoding.
    def monkey_patch_print_statement():
        # Store the real print function in another variable otherwise
        # it will be inaccessible after being modified.
        _print = print  

        # Actual implementation of the new print
        def custom_print(*args, **options):
            #_print(*args, **options)
            #add logging and monkey patch in dumping crash reports to the log file.
            try:
                Logger.info( 'PRINT: {}'.format( *args ) )
            except Exception as e:
                try:
                    Logger.warning( "ERROR: Something failed to log.\n> {}\n> {}".format( e, traceback.print_stack() ) )
                except Exception:
                    Logger.warning( "CRITICAL: Failed to log stack trace." )
                    
        # Change the print function globally
        import builtins
        builtins.print = custom_print
        
    monkey_patch_print_statement()

    #Prints the os's environment variables to the logfile.
    #Logger.debug('Check - os.environ = %s(%s)',
    #             type(os.environ), os.environ)

    #Creates a GameApp object defined above.
    GAMEAPP = GameApp()
    Logger.debug('Declared - GAMEAPP = %s', GAMEAPP)

    #Calls GAMEAPP's run method which calls GAMEAPP.build().
    Logger.info('Calling - %s.run().', GAMEAPP)
    GAMEAPP.run()

    #Gracefully exits python.
    Logger.info('Calling - quit()')
    quit()
