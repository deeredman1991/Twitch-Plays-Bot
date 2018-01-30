""" The module containing the screen manager class

"""
import random
from functools import partial

from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.graphics import BorderImage
from kivy.uix.screenmanager import ScreenManager as KivyScreenManager
from kivy.uix.screenmanager import ShaderTransition, SlideTransition,\
                                   SwapTransition, FadeTransition,\
                                   WipeTransition, FallOutTransition,\
                                   RiseInTransition, NoTransition,\
                                   CardTransition

from scripts.logger import AutoLogger
from screens.main_menu.main_menu import MainMenu
from screens.session.session import Session
from scripts.screen import Screen

class ScreenManager(KivyScreenManager, AutoLogger):
    """ Screen Manager class is responsible for swapping between screens.

        #TODO: doctest here
    """
    def __init__(self, *args, **kwargs):
        super(ScreenManager, self).__init__(*args, **kwargs)

        #NOTE: This block is temporary while we decide which ones we like best.
        transition_list = [
            ShaderTransition,
            SlideTransition,
            SwapTransition,
            FadeTransition,
            WipeTransition,
            FallOutTransition,
            RiseInTransition,
            NoTransition,
            CardTransition]
        self.transition=transition_list[random.randrange(9)]()
        dirs = ['left', 'right', 'up', 'down']
        self.transition.direction = dirs[random.randrange(4)]
        modes = ['push', 'pop']
        self.transition.mode = modes[random.randrange(2)]

        self.add_widget(MainMenu(name='Main Menu'))
        self.add_widget(Session(name='Session'))

        self.current = 'Main Menu'

        self.canvas.before.add(self.current_screen.background)

        #NOTE: Displays the transition name...also temporary.
        self.get_screen(self.current).add_widget(
            Label(text=str(type(self.transition)),
                  pos_hint={'center_x': .5,
                            'y': 0},
                  size_hint=[.3, .05],
                  outline_width=3))
