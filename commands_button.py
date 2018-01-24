""" Module containing the CommandsButton class

"""
import os

from kivy.uix.button import Button

class CommandsButton(Button):
    """ Class to define the command button for the main menu..
        when pressed: this button should open 'configs/commands.json'
        """
    def on_press(self):
       # _command_file = os.getcwd()
       # _command_file = _command_file.split('\\')
       # _command_file.append('configs\\commands.json')
       # _command_file = '\\'.join(_command_file)

        _command_file = os.getcwd + '\\configs\\commands.json'

        os.startfile(_command_file)
