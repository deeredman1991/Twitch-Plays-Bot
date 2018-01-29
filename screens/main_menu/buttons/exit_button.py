""" Module containing the CommandsButton class

"""

from kivy.core.window import Window

from scripts.button import Button


class ExitButton(Button):
    """ Class to define the exit button for the main menu.
        when pressed: this button should close the window.

        #TODO: doctest here
    """
    def __init__(self, *args, **kwargs):
        """ Method gets called when class is instantiated.
        """

        #Calls inherited classes __init__() function(s) for consistency.
        super(ExitButton, self).__init__(*args, **kwargs)

        self.size_hint = [0.3, 0.1]

    def on_press(self):
        """ Method gets called when the button gets pressed.

            #TODO: doctest here
        """
        Window.close()
