""" This modules holds the main menu screen.

"""

import os

from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.button import Button



class MainMenu(Widget):
    """ This is the main menu Widget which holds the main menu.

    """
    def __init__(self):
        super(MainMenu, self).__init__()

        Window.bind(on_resize=self._on_resize)

        self._config_button = ConfigButton()
        self._config_button.text = "Commands"
        self.add_widget(self._config_button)

        self._exit_button = ExitButton()
        self._exit_button.text = "Exit"
        self.add_widget(self._exit_button)

        self._on_resize()

    def _on_resize(self, *ignore):
        self.size = Window.size

        self._config_button.height = Window.height/10
        self._config_button.width = Window.width/10
        self._config_button.font_size = self._config_button.width/7
        self._config_button.center = self.center

        self._exit_button.height = Window.height/10
        self._exit_button.width = Window.width/10
        self._exit_button.font_size = self._exit_button.width/7
        self._exit_button.center = (self.center_x,
                                    self.center_y-self._config_button.height)
        return ignore

class ConfigButton(Button):
    """ Class to define the config button.
            when pressed: this button should open configs/commands.json
    """
    def on_press(self):
        _command_file = os.getcwd()
        _command_file = _command_file.split('\\')
        _command_file.append('configs\\commands.json')
        _command_file = '\\'.join(_command_file)
        os.startfile(_command_file)

class ExitButton(Button):
    """ Class to define the exit button.
            when pressed: this button should kill the application.
    """

    def on_press(self):
        Window.close()
