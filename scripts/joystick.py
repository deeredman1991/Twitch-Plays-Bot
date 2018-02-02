
from threading import Lock
import time
import numbers

class JoystickError(Exception):
    pass

class Joystick(object):

    def __init__(self, *args, **kwargs):
        self.last_tilted_axis = None
        self.last_tilted_axis_lock = Lock()

        self.is_paused = False

        self.buttons = []
        self.axes = [
            'X',
            'Y',
            'Z',
            'Rx',
            'Ry',
            'Rz',
            'Sl0',
            'Sl1',
            'Wheel',
            'POV']

        self.user_variables = {
            'smooth_movement': 1, #If 1 and pausing; when an axis is tilted;
                                  #    Do not reset axis until a button is
                                  #    pushed or axis is tilted that is not
                                  #    the last axis to be tilted.
            'pausing': 0} #if 1; pause emulator process between commands.
        self._user_variable_locks = {}
        for key, _ in self.user_variables.items():
            self._user_variable_locks[key] = Lock()
        self._user_variables_on_change = {
            'smooth_movement': lambda: [self.release(axis) for axis in
                                        self.axes],
            'pausing': lambda: self.release()}

    #TODO: remove print statements and replace them with vJoy calls.
    def hold(self, button_or_axis, degree=None):
        if type(button_or_axis) == type(''):
            #TODO: replace with actual code.
            print('holding axis %s at %s degrees', button_or_axis, degree)
        else:
            if degree is not None:
                raise JoystickError(
                    'Hold command told to hold button #%s at %s degrees '\
                    '\'degrees\' only makes sense when applied to an axis.',
                    button_or_axis, degree)

            if type(button_or_axis) != type(1):
                raise JoystickError(
                    'Hold command told to hold button/axis '\
                    '%s which is of type %s. Hold command can only hold '\
                    'buttons/axes of type integer or string',\
                    button_or_axis, type(button_or_axis))

            #TODO: replace with actual code.
            print('holding button #%s', button_or_axis)

    def release(self, button_or_axis=None):
        if button_or_axis:
            if type(button_or_axis) == type(''):
                print('releasing axis %s', button_or_axis)
            else:
                if type(button_or_axis) != type(1):
                    raise JoystickError(
                        'Release command told to release button/axis '\
                        '%s which is of type %s. Release command can only '\
                        'release buttons/axes of type integer or string.',\
                        button_or_axis, type(button_or_axis))
                print('releasing button #%s', button_or_axis)
        else:
            print('releasing all buttons and axes')

    #TODO: multiple hat presses should average. i.e.
    #      :mash hat_up; :mash hat_right
    #      should be equialent to
    #      :mash hat_up_and_right
    #      can achieve most of this by averaging
    #      i.e. average(9000/east, 0/north) = 4500
    #      This doesn't work for north-west though.
    #      average of 27000 and 0 is not 31500.
    #      ???Maybe we can somehow get 0 to behave like
    #      35999(or 36000) if current value is > 18000?
    #      number on top of the hat_equator should mirror
    #      number on bottom in terms of left/right bias.
    #      then average those two numbers.
    def mash(self, button, hold_for):
        user_variables = self.user_variables[:]

        if type(button) != type(1):
            raise JoystickError(
                'Mash command told to mash button '\
                '%s which is of type %s. Mash command can only '\
                'mash buttons of type integer',\
                button, type(button))
        if not isinstance(hold_for, numbers.Number):
            raise JoystickError(
                'Mash command told to mash button '\
                '%s for %s seconds. Expected number got %s',
                button, hold_for, type(hold_for))

        #FIXME: This should also probably be moved out to
        #       CommandManager.
        if user_variables['pausing'] and self.is_paused:
            print('unpausing emulator process')

        print('pressing %s', button)
        time.sleep(hold_for*1000)
        print('releasing %s', button)

        #FIXME: Not going to work...need to figure out how to
        #       re-pause the emulator after it's mashed all
        #       it's buttons.
        #       I think this should go in CommandManager
        if user_variables['pausing'] and not self.is_paused:
            print('pausing emulator process')

    def tilt(self, axis, degree, hold_for):
        user_variables = self.user_variables[:]
        last_tilted_axis = self.last_tilted_axis
        #degree between -1 and 1

        #TODO: if axis != last_tilted_axis and last_tilted_axis.degrees != 0:
        #          print('Setting last tilted axis to 0 degrees.')

        print('Setting axis %s to %s degrees')
        time.sleep(hold_for*1000)

        if not user_variables['pausing'] or \
           not user_variables['smooth_movement']:
            print('Setting axis %s to 0 degrees')

