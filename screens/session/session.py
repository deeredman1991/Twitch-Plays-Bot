""" This module holds the Session screen class. This is where the streamer
    will go to start a TP session.
"""
#pylint: disable=locally-disabled, too-many-ancestors

from screens.session.buttons.back_button import BackButton
from scripts.screen import Screen


class Session(Screen):
    """ This is the Sessions screen which holds the session

        #TODO: doctest here
    """
    def __init__(self, *args, **kwargs):
        """ Method gets called when class is instantiated.
        """
        super(Session, self).__init__(*args, **kwargs)
        
        #Creates the Back Button and sets it as a child of self.
        self._back_button = BackButton()
        self._back_button.text = "Back"
        self.add_widget(self._back_button)
