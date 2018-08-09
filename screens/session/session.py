""" This module holds the Session screen class. This is where the streamer
    will go to start a TP session.
"""
#pylint: disable=locally-disabled, too-many-ancestors

import os

from screens.session.buttons.back_button import BackButton
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
        
        #TODO: Move buttons out to a BoxLayout to be consistent with
        #       MainMenu.
        #Creates the Back Button and sets it as a child of self.
        self._back_button = BackButton()
        self._back_button.text = "Back"
        self.add_widget(self._back_button)
        
    def on_enter(self):
        self.commands_manager = CommandsManager( os.getcwd() + os.sep + 'configs' + os.sep + 'default' )
