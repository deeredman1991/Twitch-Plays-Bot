""" Module containing the CommandsButton class

"""
import os

from scripts.buttons.button import Button


class CommandsButton(Button):
    """ Class to define the command button for the main menu..
        when pressed: this button should open 'configs/commands.json'

        #TODO: doctest here
    """
    def __init__(self, *args, **kwargs):
        """ Method gets called when class is instantiated.
        """

        #Calls inherited classes __init__() function(s) for consistency.
        super(CommandsButton, self).__init__(*args, **kwargs)

        #Sets the button's relative size.
        self.size_hint = [0.3, 0.1]

    def on_resize(self, sdl2_handle, width, height):
        """ Method gets called when parent's _on_resize() gets called.

            #TODO: doctest here
        """

        #Centers the button in the middle of the screen.
        #TODO: put buttons inside a widget and place buttons based on their
        #   index within the widget object.
        self.center = (width/2, height/2)

        #Returns function's inputs.
        return self, sdl2_handle, width, height

    def on_press(self):
        """ Method gets called when the button gets pressed.

            #TODO: doctest here
        """
        #Creates a string equal to %cd%/configs/commands.json
        _command_file = str(os.getcwd()) + '\\configs\\commands.json'

        #executes the string created earlier as a console command.
        os.startfile(_command_file)

        #returns itself
        return self
