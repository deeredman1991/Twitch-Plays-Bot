
from threading import Lock, Thread
import time
import numbers
import json
import io

#from scripts.vJoy import vJoyNew, vJoy
import scripts.vJoy.__init__ as j


class JoystickError(Exception):
    pass

#class Joystick(object):
#    def __init__(self, *args, **kwargs):
#        j.vJoyNew(rID=1)
    
#'''
class Joystick(object):
    def __init__(self, *args, rID=1, configs={}, configs_filepath='', **kwargs):
        self.rID = rID

        #This is causing the "Please restart" prompt to appear... It only needs to 
        #   be called once and/or if we can't get ahold of a controller.
        #For now; Just quick and dirtily; hit "restart later".
        #j.vJoyConfig_Delete( self.rID )
        #j.vJoyConfig_Create( self.rID, force=True, buttons=25, analog_hat_switches=4 )
        #j.vJoy.vJoyEnabled()
        
        #j.vJoyConfig_Delete(self.rID)
        #j.vJoyConfig_Create(self.rID, force=True, buttons=57, analog_hat_switches=4)
        #j.vJoy.vJoyEnabled()
        #j.vJoy.AcquireVJD(self.rID)

        #j.vJoyNew(rID=self.rID)
        #tj = Thread( target=j.vJoyNew, kwargs={'rID':self.rID} )
        
        #tj.start()
        
        #tj.join()
        
        #print( j.vJoyConfig_Get_Config() )
    
        self.last_tilted_axis = None
        self.last_tilted_axis_lock = Lock()

        self.is_paused = False
        
        self.configs_filepath = configs_filepath

        self.user_variables = configs['user_variables']
        self.user_variables_lock = Lock()

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

        """
        {
            'smooth_movement': True, #If 1 and pausing; when an axis is tilted;
                                     #    Do not reset axis until a button is
                                     #    pushed or axis is tilted that is not
                                     #    the last axis to be tilted.
            'pausing': False, #if 1; pause emulator process between commands.
            'binding': False }
        """
        
        #self._user_variable_locks = {}
        #for key, _ in self.user_variables.items():
        #    self._user_variable_locks[key] = Lock()
        #self._user_variables_on_change = {
        #    'smooth_movement': lambda: [self.release(axis) for axis in
        #                                self.axes],
        #    'pausing': lambda: self.release()}
        
        
    def set_user_variable(self, key, value):
        def write_json( dict, jsn ):
            with io.open( self.configs_filepath + jsn + '.json', 'w', encoding='utf-8' ) as outfile:
                json.dump( dict, outfile, ensure_ascii=False )

        with self.user_variables_lock:
            self.user_variables[key] = value
            write_json( self.user_variables, 'user_variables' )
            
    def update_configs(self, configs={}):
        if 'user_variables' in configs:
            with self.user_variables_lock:
                self.user_variables = configs['user_variables']
            

    #TODO: remove print statements and replace them with vJoy calls.
    def hold(self, button_or_axis, degree=None):
        j.vJoy.AcquireVJD(self.rID)
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
        j.vJoy.AcquireVJD(self.rID)
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
        j.vJoy.AcquireVJD(self.rID)
        user_variables = self.user_variables.copy()

        if user_variables['binding']:
            time.sleep(2)
        
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
        #if user_variables['pausing'] and self.is_paused:
        #    print('unpausing emulator process')

        print('[JoyStick: {}] Pressing Button{}'.format(self.rID, button))
        j.vJoy.SetBtn(1, self.rID, button)
        time.sleep( hold_for )
        j.vJoy.SetBtn(0, self.rID, button)
        print('[JoyStick: {}] Releasing Button{}'.format(self.rID, button))

        #FIXME: Not going to work...need to figure out how to
        #       re-pause the emulator after it's mashed all
        #       it's buttons.
        #       I think this should go in CommandManager
        #if user_variables['pausing'] and not self.is_paused:
        #    print('pausing emulator process')
            
    def hat(self, hat, degree, hold_for):
        j.vJoy.AcquireVJD(self.rID)
        user_variables = self.user_variables.copy()
        
        if user_variables['binding']:
            time.sleep(2)
        print('[JoyStick: {}] Setting Hat #{} to {} degrees for {} seconds'.format(
                        self.rID, hat, degree, hold_for))

        #    0       : North
        # 4500       : N/E
        # 9000       : East
        #13500       : S/E
        #18000       : South
        #22500       : S/W
        #27000       : West
        #31500       : N/W
        #36000 or -1 : Neutral

        #We range from 0-360 while vJoy ranges from 0 to 36000 so
        #   We have to multiply our degree value by 100 to convert for
        #   vJoy.
        degree = degree*100

        j.vJoy.SetContPov(degree, self.rID, hat)
        time.sleep( hold_for )
        j.vJoy.SetContPov(-1, self.rID, hat)
        print('[JoyStick: {}] Releasing Hat #{}'.format(
                        self.rID, hat))

    def tilt(self, axis, degree, hold_for):
        j.vJoy.AcquireVJD(self.rID)
        user_variables = self.user_variables.copy()
        
        if user_variables['binding']:
            time.sleep(2)
        
        last_tilted_axis = self.last_tilted_axis
        #degree between -1 and 1

        #TODO: if axis != last_tilted_axis and last_tilted_axis.degrees != 0:
        #          print('Setting last tilted axis to 0 degrees.')

        print( '[JoyStick: {}] Setting axis {} to {} degrees for {} seconds'.format(self.rID, axis, degree, hold_for) )

        # For some reason the axis in vJoy range from 48 or 0x30 to 54.
        #   We use a 1, 2, 3, 4, ... system. where x = 1, y = 2, etc... etc..
        #   So we have to add 0x2F or 47 to convert our system to the vJoy system.
        axis = axis+0x2F

        # For some reason vJoy inverts the y axis so that -1 is forwards while 1 is backwards.
        # So if we are dealing with the y axis (i.e. axis number 48 or 0.31) we have to invert our degrees.
        if axis == 0x31:
            degree = -degree

        #degree can be -1, 0, or 1. In order to work with vJoy we need to convert our numbers to 
        #   non-negative values ranging from 0x0 to 0x8000.
        #We add 1 so that -1.0 becomes 0.0, 0.0 becomes 1.0, and 1.0 becomes 2.0.
        #   this way we can multiply by 0x4000 to convert our -1:1 degree system to their
        #   0x0:0x8000 degree system.
        degree = int((degree+1)*0x4000)

        j.vJoy.SetAxis( degree, self.rID, axis )
        self.last_tilted_axis = axis
        time.sleep( hold_for )

        if not user_variables['pausing'] or \
                    not user_variables['smooth_movement']:
            j.vJoy.SetAxis( 0x4000, self.rID, axis )
            print('[JoyStick: {}] Setting axis {} to 0 degrees'.format(self.rID, axis-0x2F))
#'''