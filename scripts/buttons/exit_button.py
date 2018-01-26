""" Module containing the CommandsButton class

"""

#TODO: impliment logging
from kivy.core.window import Window
from kivy.uix.button import Button


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

    def on_resize(self, sdl2_handle, width, height):
        """ Method gets called when parent's on_resize() gets called.
        """
            #TODO: doctest here

        #Centers the button in the middle of the screen and 1 button down.
        #TODO: put buttons inside a widget and place buttons based on their
        #   index within the widget object.
        self.center = (width/2, height/2-self.height)

        return self, sdl2_handle, width, height

    def on_press(self):
        """ Method gets called when the button gets pressed.

            #TODO: doctest here
        """
        Window.close()
