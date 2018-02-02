
import json
import os
from threading import Lock
from functools import partial

from kivy.clock import Clock

from scripts.commands_processor import CommandsProcessor
from scripts.joystick import Joystick

class CommandsManager(object):
    def __init__(self, configs_filepath, *args, **kwargs):

        self.joystick = Joystick()

        self.file_list = ['aliases_axes',
                          'aliases_buttons',
                          'aliases_degrees',
                          'user_commands']

        self.config_locks = {}

        self.configs = {}

        for file in self.file_list:
            self.config_locks[file] = Lock()

        Clock.schedule_interval(partial(self.read_configs, configs_filepath), 1)

        super(CommandsManager, self).__init__(*args, **kwargs)


    def process_command_string(self, command_string):
        command_string = command_string.split(';')
        for command in command_string:
            for user_command, internal_command_string in \
                                        self.configs['user_commands'].items():
                if command == user_command:
                    internal_command_string = \
                                    self.dealias(internal_command_string)
                    CommandsProcessor(self.joystick, internal_command_string)

    def dealias(self, command_string):
        assert False, "Unfinished Function!!!"

    def read_configs(self, filepath):
        if filepath[-1] != os.sep:
            filepath = filepath + os.sep

        for file in self.file_list:
            dict_key = file
            self.read_json(filepath + file + '.json', dict_key)

    def read_json(self, json_file, dict_key):
        with open(json_file, 'r') as infile:
            json_string = json.load(infile)

        if self.configs[dict_key] != json_string:
            with self.config_locks[dict_key]:
                self.configs[dict_key] = json_string
