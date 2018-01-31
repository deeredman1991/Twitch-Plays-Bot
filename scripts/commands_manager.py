""" This module contains the Commands Manager class that is responsible for
    processing any and all incoming commands.
"""

#TODO: Ideally a user_command definition will look like this:
#      "!go": ":set smooth_movement 0; :tilt x 100 1; :set smooth_movement 1"
#      Ideally a twitch_command would look like this:
#      "!go; !a 4; !b 1 3; !x; !y"
from threading import Lock

class CommandError(Exception):
    pass

class CommandsManager(object):
    """ This is the CommandsManager class that processes all incoming commands
    """
    def __init__(self, joystick, *args, **kwargs):
        self.user_variables = {
            'smooth_movement': 1,
            'pausing': 0}

        self._user_variable_locks = {}
        for key, _ in self.user_variables.items():
            self._user_variable_locks[key] = Lock()

        #TODO: bind to window.close()???; release joystick!
        self.joystick = joystick

        self._commands_list = {
            ':mash': self._mash, #For mashing buttons.
            ':tilt': self._tilt, #For tilting axies.
            ':set': self._set}  #For setting user_variables.

        #A call to a blocking command in a command string should; run all
        #   previous commands, in unison, run the blocking command, then run
        #   any additional commands(or atleast until the next
        #   blocking command) in unison.
        self._blocking_commands = ['set']

        self._user_commands_file = 'config/user_commands.json'

        super(CommandsManager, self).__init__(*args, **kwargs)

    #NOTE: When processing commands: Split by ';' first then by spaces.
    #       This way the user can submit multiple commands with a ; delimiter
    #       load all commands listed this way into threads and then start them.
    def process_command_string(self, command_string):
        command_string = command_string.split(';')

        for cmd in command_string:
            cmd_args = cmd.split(' ')
            cmd_root = cmd.pop(0)
            #NOTE: This assertion shouldn't be needed after linter is working.
            assert cmd_root in self._commands_list,\
                "%s is not a valid command." % cmd_root[0]
            #:TODO: if cmd not in blocking_commands, queue command, else
            #   run and depop queue, run blocking command, continue queueing.
            #   finish up by running any commands left on the queue.
            self._commands_list[cmd_root](cmd_args)

    def lint_user_commands(self):
        #TODO: The commands linter should make sure that the
        #   user commands file 1). is a valid .json and 2). only contains
        #   valid commands.
        #TODO: CommandsManager is getting kinda big, move this out to another
        #      file
        pass

    def _mash(self, args):
        #:mash command usage: :mash button, [times, delay, hold_for]
        if len(args) < 1 or len(args) > 4:
            raise CommandError(
                'mash command takes between 1 and 3 argument, got %s; %s' %
                len(args), args)

        button = args[0] # Which button to press.
        times = args[1] # How many times to press it.
        delay = args[2] # How long to wait between each button press.
        hold_for = args[3] # How long to hold each button for.

        for _ in range(times):
            self.joystick.mash(button, delay, hold_for, self.user_variables[:])

    def _tilt(self, args):
        #:tilt command usage: :tilt axis, degree, [hold_for]
        if len(args) < 2 or len(args) > 3:
            raise CommandError(
                'tilt command takes between 2 and 3 arguments, got %s; %s' %
                len(args), args)

        axis = args[0] # Which axis to tilt
        degree = args[1] # How far(and which direction) to tilt it.
        hold_for = args[2] # How long to tilt axis.

        self.joystick.tilt(axis, degree, hold_for, self.user_variables[:])

    def _set(self, args):
        #:set command usage: :set var value
        if not len(args) == 2:
            raise CommandError(
                'set command takes 2 argument, got %s; %s' %
                len(args), args)

        key = args[0] # Which variable to set
        val = args[1] # What to set it to.

        if key not in self.user_variables:
            self._user_variable_locks[key] = Lock()

        with self._user_variable_locks[key]:
            self.user_variables[key] = val

        return self.user_variables[key]
