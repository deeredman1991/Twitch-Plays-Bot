""" The main class where everything begins

"""
import os
import random

from kivy.app import App
from kivy.core.window import Window
from kivy.config import Config
import kivy.logger as logging

from scripts.main_menu import MainMenu


#os.environ['KIVY_DATA_DIR'] = '{}/kivy/data'.format(os.getcwd())
#os.environ['KIVY_MODULES_DIR'] = '{}/kivy/modules'.format(os.getcwd())
os.environ['KIVY_HOME'] = os.getcwd()


Config.read('kivy_config.ini')
LOGGER = logging.Logger
LOGGER.level = logging.LOG_LEVELS['debug']

class GameApp(App):
    """The GameApp class which contains the game.

    """
    def build(self):
        LOGGER.info('Main: Running - %s.build()', self)

        _x, _y = random.randint(500, 1000), random.randint(500, 1000)
        LOGGER.debug(
            'Main: In: %s.build() | Declared - _x, _y = %s(%d), %s(%d)',
            self, type(_x), _x, type(_y), _y)

        LOGGER.debug(
            'Main: In: %s.build() | Setting - %s(%s).size = %s(%d), %s(%d)', \
            self, type(Window), Window, type(_x), _x, type(_y), _y)
        Window.size = (random.randint(500, 1000), random.randint(500, 1000))
        #Window.size = (300, 500)

        self.title = 'Twitch Plays Bot'
        LOGGER.debug(
            'Main: In: %(self)s.build() | Setting - ' \
            '%(self)s.title=%(title_type)s(%(title)s)',
            {
                'self': self,
                'title_type': type(self.title),
                'title': self.title
            })

        #self.icon = 'images/icon.png'

        _r = MainMenu()
        LOGGER.info('Main: In: %s.build() | Returning - %s(%s)',
                    self,
                    type(_r),
                    _r)
        return _r

if __name__ == "__main__":
    GAMEAPP = GameApp()
    LOGGER.debug('Main: In: __main__ | Declared - GAMEAPP = %s', GAMEAPP)

    LOGGER.info('Main: In: __main__ | Calling - %s.run().', GAMEAPP)
    GAMEAPP.run()

    LOGGER.info('Main: In: __main__ | Calling - quit().')
    quit()
