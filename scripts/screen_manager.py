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
        LOGGER.info('%s: Running - %s.__init__(%s, %s))',
                    __file__, self, args, kwargs)

        LOGGER.debug(
            '%s: In: %s.__init__() | Calling - '\
            'super(ScreenManager, self).__init__(%s, %s)',
            __file__, self, args, kwargs)
        super(ScreenManager, self).__init__(*args, **kwargs)

        main_menu = MainMenu()
        LOGGER.debug('%s: In: %s.__init__() | Declared - main_menu = %s',
                     __file__, self, main_menu)

        LOGGER.debug(
            '%s: In: %s.__init() | Calling - '\
            'self.switch_to(%s)',
            __file__, self, main_menu)
        self.switch_to(main_menu)

    def switch_to(self, screen, *args, **kwargs):
        """ The switch_to() method takes a screen as an input and
            displays that screen while hiding the previous screen.

            #TODO: doctest here
        """
        LOGGER.info('%s: Running - %s.switch_to(%s(%s), %s, %s',
                    __file__, self, type(screen), screen, args, kwargs)

        LOGGER.info('%s: In %s.switch_to() | Returning - '\
                    'super(ScreenManager, self).switch_to(%s, %s, %s)',
                    __file__, self, screen, args, kwargs)
        return super(ScreenManager, self).switch_to(screen, *args, **kwargs)
