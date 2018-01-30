""" Module containing the StartSession class.

"""
from scripts.button import Button

class BackButton(Button):
    """ Class to define the Back Button for the Session Screen.
        when pressed: should switch to the 'Main Menu'
        screen in screens/main_menu/__init__.
    """

    def __init__(self, *args, **kwargs):
        """ Method gets called when class is instantiated.
        """

        #Calls inherited classes __init__() function(s) for consistency.
        super(BackButton, self).__init__(*args, **kwargs)

        self.size_hint = [0.3, 0.1]

    def on_press(self):
        screen_manager = self.parent.parent
        screen_manager.current = 'Main Menu'