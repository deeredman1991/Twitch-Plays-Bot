""" This module contains the Commands Manager class that is responsible for
    processing any and all incoming commands.
"""


class CommandError(Exception): pass

class CommandsManager(object):
    """ This is the CommandsManager class that processes all incoming commands
    """


    def __init__(self, *args, **kwargs):
        self.user_variables = {
            'smooth_movement': 0,
            'pausing': 0 }

        self._commands_list = {
            'mash': self._mash,
            'set': self._set }

        self._user_commands_file = 'config/user_commands.json'

    #NOTE: When processing commands: Split by ';' first then by spaces.
    #       This way the user can submit multiple commands with a ; delimiter
    def process_command_string(self, cmds):
        cmds = cmds.split(';')

        for cmd_string in cmds:
            cmd_args = cmd_string.split(' ')
            cmd = cmd_string.pop(0)
            #NOTE: This assertion shouldn't be needed after linter is working.
            assert cmd in self._commands_list,\
                "%s is not a valid command." % cmd[0]
            self._commands_list[cmd](cmd_args)

    def lint_user_commands(self):
        #TODO: The commands linter should make sure that the
        #   user commands file 1). is a valid .json and 2). only contains
        #   valid commands.
        pass

    def _mash(self, args):
        if not len(args) == 1:
            raise CommandError(
                'mash command only takes 1 argument, got %s; %s' %
                len(args), args)

        #TODO: Impliment 'mash' functionality. In an ideal world; in a cross
        #       platform way that does not require the user to keep focus on
        #       the emulation window.

    def _set(self, args):
        if not len(args) == 2:
            raise CommandError(
                'set command only takes 2 argument, got %s; %s' %
                len(args), args)
        self.user_variables[args[0]] = args[1]
        return self.user_variables[args[0]]
