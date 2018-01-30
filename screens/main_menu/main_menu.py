""" This module holds the main menu screen.
"""

#pylint: disable=locally-disabled, too-many-ancestors

from screens.main_menu.buttons.session_button import SessionButton
from screens.main_menu.buttons.user_commands_button import UserCommandsButton
from screens.main_menu.buttons.exit_button import ExitButton
from scripts.screen import Screen


class MainMenu(Screen):
    """ This is the main menu Screen which holds the main menu.

        #TODO: doctest here.
    """
    def __init__(self, *args, **kwargs):
        """ Method gets called when class in instantiated.
        """

        super(MainMenu, self).__init__(*args, **kwargs)

        #TODO: Move these out to a BoxLayout. So they can be centered
        #       Easier.
        #Creates the Start Session button and sets it as a child of self.
        self._session_button = SessionButton()
        self._session_button.text = "Start Session"
        self.add_widget(self._session_button)

        #Creates the Command Button and sets it as a child of self.
        self._user_commands_button = UserCommandsButton()
        self._user_commands_button.text = "Commands"
        self.add_widget(self._user_commands_button)

        #Creates the Exit Button and sets it as a child of self.
        self._exit_button = ExitButton()
        self._exit_button.text = "Exit"
        self.add_widget(self._exit_button)
