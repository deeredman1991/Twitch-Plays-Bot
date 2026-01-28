""" This module contains the Commands Manager class that is responsible for
    processing any and all incoming commands.
"""

#NOTE: Ideally a user_command will look like: "definition": "command_string"
#       parameters with an '=' sign are optional and the value after the = are
#       their defaults.
#      "!go #(seconds=1)": ":set smooth_movement 1; :tilt x 1.0 #(seconds); :set smooth_movement 0"
#      "!a #(times=1) #(delay=1.5)": ":mash 1 #(times) #(delay) 1"
#TODO: implement CommandParser

#NOTE:      Ideally a twitch_command_string would look like this:
#      "!go; !a; !b 1 3; !x; !y"

#NOTE: create a list of user defined button aliases.
#       this way a user can define a command such as;
#       "!push #(button)": ":mash #(button)"
#       then an alias to map button 1 to a in an alias config.
#       "a": 1
#       then a twitch user will be able to use;
#       !push a
#       and it will be the equivalent of !push 1


#The Lock goes away when user_variable_locks get moved to the joystick
from threading import Thread, Lock
from queue import Queue

import scripts.commands as commands

#NOTE: I need a TwitchCommandProcessor which would read Twitch Chat and
#      submit commands to a CommandManager...this way we can support
#      platforms other than Twitch.
#      CommandManager should create a "CommandsProcessor" object
#      for every twitch_command_string it gets from TwitchCommandProcessor
class CommandsProcessor(object):
    """ This is the CommandsManager class that processes all incoming commands
    """
    def __init__(self, joystick, cmd_mngr, issuer_username, command_string_delimiter, command_string, *args, **kwargs):
        #TODO: Move these out to the joystick...

        #TODO: bind to window.close()???; release joystick!
        self.joystick = joystick

        self._commands_list = {
            ':mash': commands.mash,       #For mashing buttons.
            ':tilt': commands.tilt,       #For tilting axies.
            ':hat': commands.hat,         #For using the dPad(s).
            ':set': commands.set_var,     #For setting user_variables.
            ':wait': commands.wait,       #For waiting a set period of time.
            ':op': commands.op,           #For promoting/demoting operators.
            ':deop': commands.deop,        #For removing operators.
            ':send': commands.send}       #For sending chat messages.
            
        #A call to a blocking command in a command string should; run all
        #   previous commands, in unison, run the blocking command, then run
        #   any additional commands(or atleast until the next
        #   blocking command) in unison.
        self._blocking_commands = [':set', ':wait']
        self._mngr_commands = [':op', ':deop', ':send', ':set']
        
        #NOTE: When processing commands: Split by ';' first then by spaces.
        #       This way the user can submit multiple commands with a ; delimiter
        #       load all commands listed this way into threads and then start them.
        command_string = command_string.split(command_string_delimiter)
        
        cmd_threads = []
        for cmd in command_string:
            cmd_args = cmd.split(' ')
            cmd_root = cmd_args.pop(0)

            #NOTE: This assertion shouldn't be needed after linter is working.
            assert cmd_root in self._commands_list,\
                "%s is not a valid command." % cmd_root[0]

            if cmd_root in self._mngr_commands:
                cmd_args.insert(0, issuer_username)
                cmd_args.insert(0, cmd_mngr)

            cmd_thread = Thread(target=self._commands_list[cmd_root],
                                args=(self.joystick, cmd_args))
            cmd_threads.append( cmd_thread )
            cmd_thread.start()
            if cmd_root in self._blocking_commands:
                cmd_thread.join()

        for cmdt in cmd_threads:
            cmdt.join()

        super(CommandsProcessor, self).__init__(*args, **kwargs)

    def lint_user_commands(self, commands_file):
        #TODO: The commands linter should make sure that the
        #   user commands file 1). is a valid .json and 2). only contains
        #   valid commands.
        pass
