""" This module holds the Session screen class. This is where the streamer
    will go to start a TP session.
"""
#pylint: disable=locally-disabled, too-many-ancestors

import os

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

from scripts.screen import Screen

from scripts.commands_manager import CommandsManager

class Session(Screen):
    """ This is the Sessions screen which holds the session

        #TODO: doctest here
    """
    def __init__(self, *args, **kwargs):
        """ Method gets called when class is instantiated.
        """
        super(Session, self).__init__(*args, **kwargs)
        self.created = False

        bx = self.make_box(self)

        top_spacer = self.make_box(bx, sy=0.3)

        mid = self.make_box(bx, o='horizontal', sy=0.4)

        left_mid_spacer = self.make_box(mid, sx=0.4)

        button_holder = self.make_box(mid, sx=0.6)

        self.reset_manager_button = self.make_button( button_holder, 'Reset', self.reset_manager_button_on_press )

        self.back_button = self.make_button( button_holder, 'Back', self.back_button_on_press)

        right_mid_spacer = self.make_box(mid, sx=0.4)

        bottom_spacer = self.make_box(bx, sy=0.3)
        
    def on_enter(self):
        if not self.created:
            self.make_manager()
            self.created = True
            
    def make_manager(self):
        self.commands_manager = CommandsManager( self.parent.cfg_path + self.parent.profile )
        
    def reset_manager_button_on_press(self):
        self.commands_manager.kill()
        self.make_manager()
        
    def back_button_on_press(self):
        screen_manager = self.parent
        screen_manager.current = 'Main Menu'
