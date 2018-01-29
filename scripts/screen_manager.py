""" The module containing the screen manager class

"""

from kivy.uix.screenmanager import ScreenManager as KivyScreenManager
from kivy.uix.screenmanager import WipeTransition

from screens.main_menu.main_menu import MainMenu
from screens.session.session import Session


class ScreenManager(KivyScreenManager):
    """ Screen Manager class is responsible for swapping between screens.

        #TODO: doctest here
    """
    def __init__(self, *args, **kwargs):
        super(ScreenManager, self).__init__(*args, **kwargs)

        self.transition=WipeTransition()
        
        self.add_widget(MainMenu(name='Main Menu'))
        self.add_widget(Session(name='Session'))
        
        self.current = 'Main Menu'
