""" The module containing the screen manager class

"""

from kivy.uix.screenmanager import ScreenManager

from scripts.main_menu import MainMenu
from scripts.logger import LOGGER

class ScreenManager(ScreenManager):
    """ Screen Manager class is responsible for swapping between screens.

        #TODO: doctest here
    """
    def __init__(self, *args, **kwargs):
        LOGGER.info('Running - %s.__init__(%s, %s))',
                    self, args, kwargs)

        LOGGER.debug('Calling - '\
            'super(ScreenManager, %s).__init__(%s, %s)', self, args, kwargs)
        super(ScreenManager, self).__init__(*args, **kwargs)

        main_menu = MainMenu()
        LOGGER.debug('Declared - main_menu = %s(%s)',
                     type(main_menu), main_menu)

        LOGGER.debug('Calling - %s.switch_to(%s)', self, main_menu)
        self.switch_to(main_menu)

    def switch_to(self, screen, *args, **kwargs):
        """ The switch_to() method takes a screen as an input and
            displays that screen while hiding the previous screen.

            #TODO: doctest here
        """
        LOGGER.info('Running - %s.switch_to(%s(%s), %s, %s',
                    self, type(screen), screen, args, kwargs)

        LOGGER.info('Returning - '\
                    'super(ScreenManager, %s).switch_to(%s(%s), %s, %s)',
                    self, type(screen), screen, args, kwargs)
        return super(ScreenManager, self).switch_to(screen, *args, **kwargs)
