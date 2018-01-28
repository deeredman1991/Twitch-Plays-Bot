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
        super(ScreenManager, self).__init__(*args, **kwargs)

        main_menu = MainMenu()

        self.switch_to(main_menu)
