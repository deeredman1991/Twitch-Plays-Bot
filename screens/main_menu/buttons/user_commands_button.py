""" Module containing the CommandsButton class

"""
import os

from scripts.button import Button


class UserCommandsButton(Button):
    """ Class to define the command button for the main menu..
        when pressed: this button should open 'configs/commands.json'

        #TODO: doctest here
    """
    def __init__(self, *args, **kwargs):
        """ Method gets called when class is instantiated.
        """

        #Calls inherited classes __init__() function(s) for consistency.
        super(UserCommandsButton, self).__init__(*args, **kwargs)

        #Sets the button's relative size.
        self.size_hint = [0.3, 0.1]

    def on_press(self):
        """ Method gets called when the button gets pressed.

            #TODO: doctest here
        """
        #Creates a string equal to %cd%/configs/commands.json
        _user_commands_file = str(os.getcwd()) + '/configs/user_commands.json'

        #executes the string created earlier as a console command.
        os.startfile(_user_commands_file)

        #returns itself
        return self