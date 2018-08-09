
from threading import Lock
import time

class CommandError(Exception):
    pass


def hold(joystick, args):
    #If degree == -2; button.
    #If degree == float; stick
    #If degree == int; hat
    args = args_to_nums(args)
    #:hold command usage: :hold button_or_axis [degree]
    if len(args) < 1 or len(args) > 2:
        raise CommandError(
            'hold command between 1 and 2 arguments, got %s; %s' %\
            len(args), args)
    button_or_axis = args[0]
    degree = args[1]
    joystick.hold(button_or_axis, degree)

def release(joystick, args):
    args = args_to_nums(args)
    #:release command usage: :release [button_or_axis]
    #       if button is not specified: release all held buttons and axes.
    if len(args) > 1:
        raise CommandError(
            'release command takes between 0 and 1 arguments, '\
            'got %s; %s' % len(args), args)
    button_or_axis = args[0] or None
    joystick.release(button_or_axis)

def mash(joystick, args):
    args = args_to_nums(args)
    #:mash command usage: :mash button, [times, delay, hold_for]
    if len(args) < 1 or len(args) > 4:
        raise CommandError(
            'mash command takes between 1 and 3 argument, got %s; %s' %
            len(args), args)

    button = args[0]          # Which button to press.
    times = args[1]      # How many times to press it.
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
    
    for _ in range(times):
        joystick.hat(hat, degree, hold_for)
        time.sleep( delay )
    
def tilt(joystick, args):
    args = args_to_nums(args)
    #:tilt command usage: :tilt axis, degree, [hold_for]
    if len(args) < 2 or len(args) > 3:
        raise CommandError(
            'tilt command takes between 2 and 3 arguments, got %s; %s' %
            len(args), args)
            
    axis = args[0]             # Which axis to tilt
    degree = args[1]    # How far(and which direction) to tilt it.
    hold_for = args[2]  # How long to tilt axis.
    
    #TODO: Don't forget to make the joystick create a copy of it's user
    #       variables instead of using the list directly.
    joystick.tilt(axis, degree, hold_for)
    
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

def set_var(joystick, args):
    print("setVar")
    #:set command usage: :set var value
    if len(args) < 2 or len(args) > 3:
        raise CommandError(
            'set command takes between 2 and 3 argument, got %s; %s' %
            len(args), args)

    #TODO: func is for mods...Create a mod that writes all
    #      commands processed to a file.
    key = args[0]           # Which variable to set
    val = int( args[1] )           # What to set it to.
    #func = args[2]  # Register on_change callback.

    #if func is not None:
    #    joystick.user_variables_on_change[key] = func
    #if callable(joystick.user_variables_on_change[key]):
    #    joystick.user_variables_on_change[key]()
    joystick.set_user_variable(key, val)

    return joystick.user_variables[key]