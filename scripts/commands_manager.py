
import json
import os
import time
from threading import Lock, Thread
from functools import partial

#from kivy.clock import Clock

from scripts.commands_processor import CommandsProcessor
from scripts.joystick import Joystick
from scripts.twitch_interface import TwitchInterface
from scripts.process_manager import ProcessManager

class CommandsManagerError(Exception):
    pass

class CommandsManager(object):
    def __init__(self, configs_filepath, *args, **kwargs):
        #'''
        self.file_list = ['aliases_axes',
                          'aliases_buttons',
                          'aliases_degrees',
                          'aliases_hats',
                          'emulator_settings',
                          'login',
                          'user_commands',
                          'user_variables',
                          'dev_login']
        #'''
        
        #self.file_list = os.listdir('configs'+ os.sep + 'default')

        for index, jsn in enumerate( self.file_list ):
            self.file_list[index] = jsn.split('.')[0]
        
        self.command_delimiter = ';'
        
        self.joystick = None
        
        print("Reading Configs")
        self.config_locks = {}

        self.configs = {}

        for file in self.file_list:
            self.config_locks[file] = Lock()

        self.configs_filepath = configs_filepath

        self.read_configs()

        #Clock.schedule_interval(self.read_configs, 1)
        Thread(target=self.update_configs_thread, daemon=True).start()
        
        
        print("Initializing Process Manager")
        self.process_manager = ProcessManager( configs=self.configs ).start()

        print("Initializing Joystick")
        self.joystick = Joystick( configs=self.configs, 
                                  configs_filepath = self.configs_filepath,
                                  process_manager = self.process_manager)
        
        if 'dev_login' in self.configs:
            login = self.configs['dev_login']
        else:
            login = self.configs['login']
        
        print("Connecting to Twitch")
        self.interface = TwitchInterface(
                login['bot_oAuth'],
                login['bot_name'],
                login['streamer_name'])
        self.interface.start()
        self.interface.listen(on_recvd_callback=self.on_received)

        super(CommandsManager, self).__init__(*args, **kwargs)

    def update_configs_thread(self):
        while True:
            self.read_configs()
            time.sleep(1)

    def get_commands(self):
        self.interface.start()
        self.interface.listen(on_recvd_callback=self.on_received)

    def on_received(self, recvd):
        username, msg = recvd

        if self.validate_command(msg):
            self.process_command_string(msg)

    def validate_command(self, external_command_string):
        external_command_string = external_command_string.split(';')
        rtv = False
        for external_command in external_command_string:
            external_root = self.get_root(external_command)

            for user_command_string, _ in self.configs['user_commands'].items():
                user_command_root = self.get_root(user_command_string)
                if external_root == user_command_root:
                    rtv = True
        return rtv

    def get_root(self, command):
        while command[0] == ' ':
            command = command[1:]
        return command.split(' ')[0]

    def process_command_string(self, command_string):
        command_string = command_string.split(self.command_delimiter)

        new_command_string = []
        for command in command_string: #command/command string comes from Twitch
            for user_command_string, internal_command_string in \
                                        self.configs['user_commands'].items():
                                        #This config file is a list formatted
                                        #   as; 
                                        #User Command Definitions: Internal Commands

                command_root = self.get_root(command)
                user_command_root = self.get_root(user_command_string)
                if command_root == user_command_root:
                    internal_command = \
                                    self.dealias(command, 
                                                 user_command_string, 
                                                 internal_command_string)
                    if internal_command is not None:
                        new_command_string.append( internal_command )

        #TODO: insert pausing stuff here
        if new_command_string != []:
            if self.joystick.user_variables['pausing'] == 1 or self.process_manager.paused == True:
                #print("unpausing")
                self.process_manager.resume_emulator()
            CommandsProcessor( self.joystick, self.command_delimiter.join( new_command_string ) )
            if self.joystick.user_variables['pausing'] == 1:
                #print("pausing")
                self.process_manager.pause_emulator()

    def dealias(self, external_command, user_command, internal_command_string):
        #      In a command definition there are; roots, variables, and values
        #      There are three types of commands:
        #           1. a User Command = a command defined by the host of the
        #              stream and used by the audiance.
        #           2. an Internal Command = a command defined by us that the 
        #              host of the stream can use to bind "User Commands" to.
        #           3. an External Command = a command issued by the Audicance.
        #"!root #(var1) #(var2=value1)": ":root value2 value3 #(var1) #(var2)"
        #      only values have aliases
        #This method should convert an "External Command" into an
        #   into an "Internal Command" using the user defined "User Command" 

        #external_command - Comes from twitch
        #user_command - Left side of user_commands.json
        #internal_command_string - Right side of user_commands.json

        def strp(str):
            #Helper function for stripping the # and () from an argument.
            return str[2:-1]
            
        user_command = user_command.split(' ')
        internal_command_string = internal_command_string.split(' ')
        external_command = external_command.split(' ')

        print(user_command)
        print(internal_command_string)
        print(external_command)
        
        aliased_internal_command_string = internal_command_string
        
        for cmd in external_command[:]:
            if cmd == ' ' or cmd == '':
                external_command.pop( external_command.index(cmd) )

        #Populate aliased_internal_command_string
        for user_arg_index, user_arg in enumerate(user_command):
            if user_arg[0] == '#':
                user_arg = strp(user_arg)
                user_arg = user_arg.split('=')
                user_arg_key = user_arg[0]
                user_arg_default_value = user_arg[1]

                for internal_arg_index, internal_arg in enumerate(internal_command_string):
                    if internal_arg[0] == '#':
                        new_internal_arg = strp(internal_arg)
                        if user_arg_key == new_internal_arg:
                            if len( external_command ) > user_arg_index:
                                aliased_internal_command_string[internal_arg_index] = external_command[user_arg_index]
                            else:
                                aliased_internal_command_string[internal_arg_index] = user_arg_default_value
                                
        #Dealias aliased_internal_command_string
        aliases = {}
        if self.get_root( ' '.join(internal_command_string) ) == ":mash":
            aliases.update( self.configs['aliases_buttons'] )
        elif self.get_root( ' '.join(internal_command_string) ) == ":tilt":
            aliases.update( self.configs['aliases_degrees'] )
            aliases.update( self.configs['aliases_axes'] )
        elif self.get_root( ' '.join(internal_command_string) ) == ":hat":
            aliases.update( self.configs['aliases_hats'] )

        internal_command_string = aliased_internal_command_string
        for aicKey, aicValue in enumerate(aliased_internal_command_string):
            for alias, value in aliases.items():
                if aicValue == alias:
                    internal_command_string[aicKey] = str(value)
                    
        test_command_string = internal_command_string[:]
        test_command_string.pop(0)

        for cmd in test_command_string:
            if not cmd.replace('.','').replace('-','').isdigit() and \
               self.get_root( ' '.join(internal_command_string) ) != ":set":
                return None
                
        print (' '.join( internal_command_string ))
        return ' '.join( internal_command_string )

    def read_configs(self):
        if self.configs_filepath[-1] != os.sep:
            self.configs_filepath = self.configs_filepath + os.sep

        for file in self.file_list:
            dict_key = file
            self.read_json(self.configs_filepath + file + '.json', dict_key)

    def read_json(self, json_file, dict_key):
        try:
            with open(json_file, 'r') as infile:
                try:
                    json_string = json.load( infile )
                except json.decoder.JSONDecodeError:
                    raise CommandsManagerError("\n\n-------\n\nPlease use a json lint utility to verify that {} is a valid .json file.".format(json_file))
            if dict_key not in self.configs or self.configs[dict_key] != json_string:
                with self.config_locks[dict_key]:
                    self.configs[dict_key] = json_string
                    if dict_key == 'user_variables' and self.joystick:
                        self.joystick.update_configs(configs=self.configs)
        except FileNotFoundError as e:
            if json_file.split(os.sep)[-1] != 'dev_login.json':
                raise FileNotFoundError(e)
                