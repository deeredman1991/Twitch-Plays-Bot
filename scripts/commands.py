
from threading import Lock
import time

class CommandError(Exception):
    pass
    
def send(_, args):
    cmds_mngr = args.pop(0)
    cmds_issuer = args.pop(0)
    msg = ' '.join(args)
    cmds_mngr.interface.say(msg)

def mash(joystick, args):
    args = args_to_nums(args)
    #:mash command usage: :mash button, [times, delay, hold_for]
    if len(args) < 1 or len(args) > 4:
        raise CommandError(
            'mash command takes between 1 and 3 argument, got %s; %s' %
            len(args), args)

    button = int( args[0] )          # Which button to press.
    times = int( args[1] )      # How many times to press it.
    #TODO: Get defaults from config file for delay and hold_for.
    delay = args[2]   # How long to wait between each button press.
    hold_for = args[3] # How long to hold each button for.

    for _ in range(times):
        #TODO: Don't forget to make the joystick create a copy of it's user
        #       variables instead of using the list directly.
        joystick.mash(button, hold_for)
        time.sleep( delay )
        
def hat(joystick, args):
    args = args_to_nums(args)
    
    hat = args[0]
    degree = args[1]
    times = args[2]
    delay = args[3]
    hold_for = args[4]
    
    if isinstance(times, int):
        for _ in range(times):
            joystick.hat(hat, degree, hold_for)
            time.sleep( delay )
    
def tilt(joystick, args):
    args = args_to_nums(args)
    #:tilt command usage: :tilt axis, degree, [hold_for]
    if len(args) != 4:
        raise CommandError(
            'tilt command takes between 4 arguments, got %s; %s' %
            len(args), args)
            
    axis = args[0]             # Which axis to tilt
    degree = args[1]    # How far(and which direction) to tilt it.
    hold_for = args[2]  # How long to tilt axis.
    smoothness = args[3] #Do smooth movement?
    
    #TODO: Don't forget to make the joystick create a copy of it's user
    #       variables instead of using the list directly.
    joystick.tilt(axis, degree, hold_for, smoothness)
    
def args_to_nums(args):
    new_args = []
    for arg in args:
        new_args.append( float(arg) if '.' in arg else int(arg) )
    return new_args
    
def wait(_, args):
    args = args_to_nums(args)
    wait_time = args[0]
    print( 'Waiting for {} seconds'.format(wait_time) )
    time.sleep(wait_time)
    
def op(_, args):
    cmds_mngr = args[0]
    issuer_username = args[1]
    target_username = args[2]
    to_level = args[3]

    operators = cmds_mngr.configs['operators']
    
    if target_username.lower() == "none" or not to_level.isdigit():
        return False
        
    to_level = int(to_level)
    
    if issuer_username in operators:
        if to_level > operators[issuer_username]:
            if target_username in operators:
                if operators[target_username] > operators[issuer_username]:
                    cmds_mngr.set_config('operators', target_username, to_level)
                    cmds_mngr.interface.say('{} has set {}\'s operator rank to {}.'.format(issuer_username,
                                                                                           target_username,
                                                                                           cmds_mngr.configs['operators'][target_username]))
                else:
                    cmds_mngr.interface.say('Cannot set permission level of equal or superior operator.')
            else:
                cmds_mngr.set_config('operators', target_username, to_level)
                cmds_mngr.interface.say('Congratulations! ' \
                    '{} has promoted {} to operator status.'.format(issuer_username,
                                                                    target_username))
        else:
            cmds_mngr.interface.say('Cannot promote someone to your own rank or above.')

def deop(_, args):
    cmds_mngr = args[0]
    issuer_username = args[1]
    target_username = args[2]

    operators = cmds_mngr.configs['operators']
    
    if target_username.lower() == "none":
        return False
    
    if issuer_username in operators:
        if target_username in operators:
            if operators[target_username] > operators[issuer_username]:
                cmds_mngr.set_config('operators', target_username, None)
                cmds_mngr.interface.say('{} has revoked {}\'s operator status.'.format(issuer_username,
                                                                                       target_username))
            else:
                cmds_mngr.interface.say('Cannot deop equal or superior operator.')
        else:
            cmds_mngr.interface.say('Cannot deop. {} is not an operator. '.format(target_username))

def set_var(joystick, args):
    print(args)
    #:set command usage: :set var value
    if len(args) < 4 or len(args) > 5:
        #print(len(args))
        print(args)
        #print( 'Set command takes between 2 and 3 argument, got {}; {}'.format( len(args), (args) ) )
        raise CommandError()

    cmds_mngr = args[0]
    issuer_username = [1]
    key = args[2]           # Which variable to set
    val = int( args[3] )           # What to set it to.

    joystick.set_user_variable(key, val)

    cmds_mngr.interface.say( '{} user variable has been set to {}.'.format(key, joystick.user_variables[key]) )
