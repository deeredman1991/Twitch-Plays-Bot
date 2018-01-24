""" The module containing the screen manager class

"""

from kivy.uix.screenmanager import ScreenManager

from scripts.main_menu import MainMenu


class ScreenManager(ScreenManager):
    def __init__(self, *args, **kwargs):
        super(ScreenManager, self).__init__(*args, **kwargs)

        self.switch_to(MainMenu())
