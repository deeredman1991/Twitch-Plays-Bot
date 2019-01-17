
import json
import os
import io
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
        print("[CommandsManager]: Initializing.")

        self.is_alive = True
    
        #'''
        self.file_list = ['aliases_axes',
                          'aliases_buttons',
                          'aliases_hats',
                          'emulator_settings',
                          'login',
                          'user_commands',
                          'user_variables',
                          'operators',
                          'operator_commands',
                          'dev_login']
        #'''
        
        #self.file_list = os.listdir('configs'+ os.sep + 'default')

        for index, jsn in enumerate( self.file_list ):
            self.file_list[index] = jsn.split('.')[0]
        
        self.joystick = None
        
        print("[CommandsManager]: Reading Configs.")
        self.config_locks = {}

        self.configs = {}

        for file in self.file_list:
            self.config_locks[file] = Lock()

        self.configs_filepath = configs_filepath

        self.read_configs()

        #Clock.schedule_interval(self.read_configs, 1)
        Thread(target=self.update_configs_thread, daemon=True).start()

        self.command_delimiter = self.configs['user_variables']['multi_command_delimiter']

        print("[CommandsManager]: Initializing Process Manager.")
        self.process_manager = ProcessManager( configs=self.configs ).start()

        print("[CommandsManager]: Initializing Joystick.")
        self.joystick = Joystick( configs=self.configs, 
                                  configs_filepath = self.configs_filepath,
                                  process_manager = self.process_manager)
        
        if 'dev_login' in self.configs:
            login = self.configs['dev_login']
        else:
            login = self.configs['login']

        if login['streamer_name'] not in self.configs['operators']:
            self.set_config('operators', login['streamer_name'], 0)
        
        print("[CommandsManager]: Connecting to Twitch.")
        self.interface = TwitchInterface(
                login['bot_oAuth'],
                login['bot_name'],
                login['streamer_name'])
        self.interface.start()
        self.interface.listen(on_recvd_callback=self.on_received)
        
        if self.joystick.user_variables['pausing'] == 1:
            self.process_manager.pause_emulator()

        super(CommandsManager, self).__init__(*args, **kwargs)

    def kill(self):
        print('[CommandsManager]: Terminating.')
        self.is_alive = False
        self.interface.kill()
        self.process_manager.kill()
        time.sleep(1)
        print('[CommandsManager]: Terminated.')
        return
        
    def set_config(self, file, key, value):
        def write_json( dict, jsn ):
            with io.open( self.configs_filepath + jsn + '.json', 'w', encoding='utf-8' ) as outfile:
                json.dump( dict, outfile, ensure_ascii=False )
                print('[CommandsManager]: Dumping configs json.')

        with self.config_locks[file]:
            if value is not None:
                self.configs[file][key] = value
                print("[CommandsManager]: {} in {} has been set to {}.".format(key, file, self.configs[file][key]))
            else:
                self.configs[file].pop(key)
                print("[CommandsManager]: {} has been removed from {}.".format(key, file))
            write_json( self.configs[file], file )
            
        
    def update_configs_thread(self):
        while self.is_alive:
            self.read_configs()
            time.sleep(1)
        print('[CommandsManager]: Config Updater Terminated.')

    def get_commands(self):
        self.interface.start()
        self.interface.listen(on_recvd_callback=self.on_received)

    def on_received(self, recvd):
        username, msg = recvd

        if self.validate_command(msg):
            self.process_command_string(msg, username)

    def validate_command(self, external_command_string):
        external_command_string = external_command_string.split(self.command_delimiter)
        rtv = False
        for external_command in external_command_string:
            external_root = self.get_root(external_command)

            for user_command_string, _ in self.configs['user_commands'].items():
                user_command_root = self.get_root(user_command_string)
                if external_root == user_command_root:
                    rtv = True
        return rtv

    def get_root(self, command):
        if len(command) > 0:
            while command[0] == ' ':
                command = command[1:]
            return command.split(' ')[0]
        else:
            return None

    def process_command_string(self, external_commands, command_issuer):
        external_commands = external_commands.split(self.command_delimiter)

        internal_commands_list = []
        for external_command in external_commands[0:self.configs['user_variables']['multi_command_limit']]: #command/command string comes from Twitch
            for external_command_definition, internal_command_definition in \
                                        self.configs['user_commands'].items():

                command_root = self.get_root(external_command)
                user_command_root = self.get_root(external_command_definition)
                if command_root == user_command_root:
                    for internal_command_slice in internal_command_definition.split(';'):
                        if command_root in self.configs['operator_commands']:
                            print('[CommandsManager]: {} issued operator command {} of permission level {}'.format(command_issuer,
                                                                                                                   command_root,
                                                                                                                   self.configs['operator_commands'][command_root]
                                                                                                                   ))
                            if command_issuer not in self.configs['operators']:
                                print('[CommandsManager]: Failed to execute {}. {} is not an operator.'.format(command_root,
                                                                                                               command_issuer))
                                continue
                            if self.configs['operators'][command_issuer] > self.configs['operator_commands'][command_root]:
                                print('[CommandsManager]: Failed to execute {}. '\
                                    'User {}[{}] does not have required permission level {}.'.format(command_root,
                                                                                                     command_issuer,
                                                                                                     self.configs['operators'][command_issuer],
                                                                                                     self.configs['operator_commands'][command_root]))
                                continue

                        internal_command = \
                                        self.dealias(external_command, 
                                                     external_command_definition, 
                                                     internal_command_slice)

                        if internal_command is not None:
                            internal_commands_list.append( internal_command )

        if internal_commands_list != []:
            if self.joystick.user_variables['pausing'] == 1 or self.process_manager.paused == True:
                self.process_manager.resume_emulator()
            CommandsProcessor( self.joystick, self, command_issuer, self.command_delimiter, self.command_delimiter.join( internal_commands_list ) )
            if self.joystick.user_variables['pausing'] == 1:
                self.process_manager.pause_emulator()

    def dealias(self, external_command, external_command_definition, internal_command_definition):
        #This method should convert an "External Command" into an
        #   into an "Internal Command" using the user defined "Command Definition"
            
        print ('[CommandsManager]: Detected External Command "{}"'.format( external_command ))
        
        external_command_definition = external_command_definition.split(' ') #Left side of user_commands.json.
        internal_command_definition = internal_command_definition.split(' ') #Right side of user_commands.json.
        external_command = external_command.split(' ')                       #Comes from twitch.
        
        for cmd in external_command[:]:
            if cmd == ' ' or cmd == '':
                external_command.pop( external_command.index(cmd) )
                
        for cmd in internal_command_definition[:]:
            if cmd == ' ' or cmd == '':
                internal_command_definition.pop( internal_command_definition.index(cmd) )

        internal_command = internal_command_definition #Created from the above 3 and becomes the eventual output of this method.
        internal_command_root = self.get_root( ' '.join(internal_command) )
                
        def strp(str):
            #Helper function for stripping the # and () from an argument.
            return str[2:-1]
                
        #Create internal_command.
        #TODO: This file is getting long, consider moving this out to another module during next refactoring pass.
        for external_command_def_arg_index, external_command_def_arg in enumerate(external_command_definition):
            if external_command_def_arg[0] == '#':
                external_command_def_arg = strp(external_command_def_arg)
                external_command_def_arg = external_command_def_arg.split('=')
                external_cmd_def_arg_key = external_command_def_arg[0]
                external_cmd_def_arg_default_values = external_command_def_arg[1]
                external_cmd_def_max_value = None
                external_cmd_def_min_value = None
                if ':' in external_cmd_def_arg_default_values:
                    default_values = external_cmd_def_arg_default_values.split(':')
                    external_cmd_def_max_value = default_values.pop(-1)
                    if len(default_values) >= 2:
                        external_cmd_def_min_value = default_values.pop(-1)
                
                for internal_command_def_arg_index, internal_command_def_arg in enumerate(internal_command_definition):
                    if internal_command_def_arg[0] == '#':
                        new_internal_arg = strp(internal_command_def_arg)
                        if external_cmd_def_arg_key == new_internal_arg:
                            if len( external_command ) > external_command_def_arg_index:
                                if external_cmd_def_min_value:
                                    external_command[external_command_def_arg_index] = '{}:{}:{}'.format( 
                                            external_command[external_command_def_arg_index],
                                            external_cmd_def_min_value,
                                            external_cmd_def_max_value )
                                elif external_cmd_def_max_value:
                                    external_command[external_command_def_arg_index] = '{}:{}'.format( 
                                            external_command[external_command_def_arg_index], 
                                            external_cmd_def_max_value )
                                internal_command[internal_command_def_arg_index] = external_command[external_command_def_arg_index]
                            else:
                                internal_command[internal_command_def_arg_index] = external_cmd_def_arg_default_values
        
        #Get Aliases
        aliases = {}
        if internal_command_root == ":mash":
            aliases.update( self.configs['aliases_buttons'] )
        elif internal_command_root == ":tilt":
            aliases.update( self.configs['aliases_axes'] )
        elif internal_command_root == ":hat":
            aliases.update( self.configs['aliases_hats'] )

        validator_exceptions = [':set', ':op', ':deop', ':send']
            
        #Helper function to check if an argument of the internal command is valid
        #   so that an invalid argument doesn't get passed to the commands processor.
        def is_valid_argument(arg, internal_command):
            if arg != internal_command_root:
                if hasattr(arg, 'replace'):
                    if not arg.replace('.','').replace('-','').isdigit() and \
                       internal_command_root not in validator_exceptions:
                        return False
                else:
                    return False
            return True

        #Assign internal command values.
        for internal_command_arg_key, internal_command_arg_value in enumerate(internal_command[:]):
            internal_command_arg_max_value = None
            internal_command_arg_min_value = None
            
            if ':' in internal_command_arg_value and \
                internal_command_arg_value != internal_command_root and internal_command_root != ':send':
                    internal_command_arg_value = internal_command_arg_value.split(':')
                    internal_command_arg_max_value = str( internal_command_arg_value.pop(-1) )
                    if len( internal_command_arg_value ) > 1:
                        internal_command_arg_min_value = str( internal_command_arg_value.pop(-1) )
                        
                    internal_command_arg_value = ''.join( internal_command_arg_value )
                    
            #Dealias internal_command
            for alias, value in aliases.items():
                if internal_command_arg_value == alias:
                    internal_command_arg_value = str(value)

                if internal_command_arg_max_value == alias:
                    internal_command_arg_max_value == str(value)

            if not is_valid_argument( internal_command_arg_value, internal_command ) or \
               ( internal_command_arg_max_value and \
               not is_valid_argument( internal_command_arg_max_value, internal_command ) ):
                    return None
            
            if internal_command_root not in validator_exceptions:
                try:
                    if internal_command_arg_max_value and \
                        float( internal_command_arg_value ) > float( internal_command_arg_max_value ):
                            internal_command_arg_value = internal_command_arg_max_value
                    elif internal_command_arg_min_value and \
                        float( internal_command_arg_value ) < float( internal_command_arg_min_value ):
                            internal_command_arg_value = internal_command_arg_min_value
                except ValueError:
                    print("Invalid Command cannot convert {} to float".format(internal_command_arg_value))
                    return None
                
            internal_command[internal_command_arg_key] = internal_command_arg_value
                
        print ('[CommandsManager]: Sending Internal Command "{}"'.format(' '.join( internal_command )))
        return ' '.join( internal_command )

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
                