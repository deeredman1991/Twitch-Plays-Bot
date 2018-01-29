""" Module containing the StartSession class.

"""
from scripts.button import Button

class SessionButton(Button):
    """ Class to define the start session button for the main menu.
        when pressed: should switch to the 'session'
        screen in screens/session.
    """

    def __init__(self, *args, **kwargs):
        """ Method gets called when class is instantiated.
        """

        #Calls inherited classes __init__() function(s) for consistency.
        super(SessionButton, self).__init__(*args, **kwargs)

        self.size_hint = [0.3, 0.1]

    def on_press(self):
        screen_manager = self.parent.parent
        #main_menu = screen_manager.get_screen('Main Menu')
        screen_manager.current = 'Session'
