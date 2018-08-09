import os
import sys
import time
import subprocess
from ctypes import cdll, c_byte, c_long, wintypes, Structure

VJOYPATH = 'scripts' + os.sep + 'vJoy' + os.sep + 'vJoy' + os.sep
VJOYPATH2 = 'vJoy' + os.sep

DLLPATH = VJOYPATH + "vJoyInterface.dll"
DLLPATH2 = VJOYPATH2 + "vJoyInterface.dll"

try:
    vJoy = cdll.LoadLibrary(DLLPATH)
except OSError as o:
    try:
        vJoy = cdll.LoadLibrary(DLLPATH2)
        VJOYPATH = VJOYPATH2
    except OSError as e:
        print(o)
        print(e)
        sys.exit("Unable to load vJoy SDK DLL.  Ensure that vJoyInterface.dll is present")

'''
vJoyConfig Dn [-f][-l][-aAi [Ai+1 …]] [-bn] {[-pm] | [-sj]} [-e [{all | Ei ...}]]
Create a joystick device

D n The index of the target joystick device in the range of 1-16

-f Force creation even if device exists. This will delete the current device before creating a new one.

-l Defer creation of device until the next operation that enables the driver. See Notes.

-a  Ai Define axes (one or more).
Possible values are (Case insensitive): x, y, z, rx, ry, rz, sl0, sl1
In the absence of this flag the default will be used (Default = all axes)

-b  n Set the number of buttons (Possible values are 0 to 128; Default = 8 buttons)

-p  m Set the number of analog POV Switches (Possible values are 0 to 4; Default = 0)

-s j Set the number of discrete POV Switches (Possible values are 0 to 4; Default = 0)

-e Ei Define the required FFB Effect. Possible Effect Values are (Case Insensitive):

Const 	Constant Force
Ramp	Ramp Force
Sq	    Square Wave Force
Sine	Sine Wave Force
Tr	    Triangular Wave Force
StUp	Sawtooth (Up) Wave Force
StDn	Sawtooth (Down) Wave Force
Spr	    Spring
Dm	    Damper
Inr	    Inertia
Fric	Friction
All	    All above FFB effects
'''

class vJoyConfigError(Exception):
    ''' Custom exception for the vJoy module '''
    pass

def _get_vJoy_path():
    global VJOYPATH

    #TODO: Make sure vJoyConfig.exe is actually there...

    vJoyConfigPath = os.path.abspath( VJOYPATH )
    if vJoyConfigPath[-1] != os.sep:
        vJoyConfigPath += os.sep
    vJoyConfig = vJoyConfigPath + 'vJoyConfig.exe'

    if not os.path.isfile(vJoyConfig):
        raise vJoyConfigError('Failed to find vJoyConfig.exe are you sure '\
                              'this is the correct path? %s' % vJoyConfig)

    return '"{}"'.format(vJoyConfig)

def vJoyConfig_Get_Config(rID=0):
    if int(rID) < 0 or int(rID) > 16:
        raise vJoyConfigError( 'rID must be between 0 and 16' )

    vJoyConfig = _get_vJoy_path()

    command_string = ' '.join([vJoyConfig, '-t', '-c', str(rID)])

    #TODO: parse result and return it as a list
    result = subprocess.Popen( command_string, stdout = subprocess.PIPE ).communicate( )

    return result

def vJoyConfig_Disable():
    vJoyConfig = _get_vJoy_path()
    result = subprocess.run( '%s Enable off' % vJoyConfig )
    #command_string = vJoyConfig + ' Enable off'
    
    #os.system(vJoyConfig + ' enable off')
    
    #result = subprocess.Popen( [vJoyConfig, 'enable', 'off'], shell=True )
    #result.communicate()
    print('vJoy: Disable returncode: {}'.format(result.returncode))
    if result.returncode != 0:
        raise vJoyConfigError('Failed to disable vJoy. Is your vJoy config '\
                              'path correct? %s' % vJoyConfig)

def vJoyConfig_Enable():
    vJoyConfig = _get_vJoy_path()
    #os.system( vJoyConfig + ' enable on' )
    #result = subprocess.Popen( [vJoyConfig, 'enable', 'on'] )
    #result.communicate()
    
    
    result = subprocess.run( '%s Enable on' % vJoyConfig )
    print('vJoy: Enable returncode: {}'.format(result.returncode))
    if result.returncode != 0:
        raise vJoyConfigError('Failed to disable vJoy. Is your vJoy config '\
                              'path correct? %s' % vJoyConfig)

def vJoyConfig_Reset():
    vJoyConfig = _get_vJoy_path()
    result = subprocess.run( '%s -r' % vJoyConfig )
    #os.system( vJoyConfig + ' -r' )
    #result = subprocess.call( [vJoyConfig, '-r'] )
    #result.communicate()
    print('vJoy: Reset returncode: {}'.format(result.returncode))
    if result.returncode != 0:
        raise vJoyConfigError('Failed to disable vJoy. Is your vJoy config '\
                              'path correct? %s' % vJoyConfig)

def vJoyConfig_Delete(rID, disable = True):
    if rID < 1 or rID > 16:
        raise vJoyConfigError('rID must be between 1 and 16')

    vJoyConfig = _get_vJoy_path()
    if disable:
        vJoyConfig_Disable()

    #os.system( vJoyConfig + ' -d ' + str(rID) )
    #result = subprocess.Popen( [vJoyConfig, '-d', str(rID)] )
    #result.communicate()
    result = subprocess.run( '{} -d {}'.format( vJoyConfig, str(rID) ) )
    print('vJoy: Delete returncode: {}'.format(result.returncode))
    if result.returncode != 0:
        raise vJoyConfigError('Failed to delete vJoy device')

def vJoyConfig_Create(# The index of the target joystick device in the range of 1-16.
                      rID,
                      # Force creation even if device exists. This will delete the current device before creating a new one.
                      force=False,
                      # Defer creation of device until the next operation that enables the driver.
                      defer=False,
                      # Define axes (one or more). Possible values are (Case insensitive).
                      axes=['x',
                            'y',
                            'z',
                            'rx',
                            'ry',
                            'rz',
                            'sl0',
                            'sl1'],
                   # Set the number of buttons (Possible values are 0 to 128).
                   buttons=8,
                   # Set the number of analog POV Switches (Possible values are 0 to 4).
                   analog_hat_switches=0,
                   # Set the number of discrete POV Switches (Possible values are 0 to 4).
                   discrete_hat_switches=0,
                   # Define the required FFB Effect. Possible Effect Values are (Case Insensitive).
                   force_feedback_effects=['const',
                                           'ramp',
                                           'sq',
                                           'sine',
                                           'tr',
                                           'stup',
                                           'stdn',
                                           'spr',
                                           'dm',
                                           'inr',
                                           'fric'],
                   # Whether or not to disable vJoy before configuring. Not doing so will require a restart.
                   disable = True,
                   # How long to wait after Configuring vJoy.
                   wait_for=2):

    if analog_hat_switches > 0 and discrete_hat_switches > 0:
        raise vJoyConfigError('Cannot have both analog and discrete hat switches')
 
    if rID < 0 or rID > 16:
        raise vJoyConfigError('rID must be between 1 and 16')
 
    if buttons < 0 or buttons > 128:
        raise vJoyConfigError('buttons must be between 0 and 128')
 
    if analog_hat_switches < 0 or analog_hat_switches > 4 or\
       discrete_hat_switches < 0 or discrete_hat_switches > 4:
       raise vJoyConfigError('Cannot have less than 0 or more than 4 hat switches')
 
    if not isinstance( axes, [].__class__ ):
        raise vJoyConfigError('axes must be of type list')
 
    if not isinstance( force_feedback_effects, [].__class__ ):
        raise vJoyConfigError('force_feedback_effects must be of type list')

    #TODO: Error check to make sure axes and force_feedback_effects is not only a list but a list of proper values.
    #      After doing that; I assume we will have a proper list of acceptable values kicking around and so we can.
    #      Default to emulating an XBox360 controller.
 
    vJoyConfig = _get_vJoy_path()

    if disable:
        vJoyConfig_Disable()

    #command_string = ' '.join( [vJoyConfig,
    #                            str(rID),
    #                            '-f' if force else '',
    #                            '-l' if defer else '',
    #                            '-a ' + ' '.join(axes),
    #                            '-b ' + str(buttons),
    #                            '-p ' + str(analog_hat_switches),
    #                            '-s ' + str(discrete_hat_switches),
    #                            '-e ' + ' '.join(force_feedback_effects)] )

    #print('~~~~~~~')
    #print(command_string)
    #result = subprocess.run(command_string)
    #print('Create returncode: {}'.format(result))
    
    cr_list = ['-a ' + ' '.join(axes),
              '-b ' + str(buttons),
              '-p ' + str(analog_hat_switches),
              '-s ' + str(discrete_hat_switches),
              '-e ' + ' '.join(force_feedback_effects),
              vJoyConfig,
              str(rID)]
    
    if defer:
        cr_list.insert(0, '-l')
    if force:
        cr_list.insert(0, '-f')
    
    cr_list.insert( 0, cr_list.pop(-1) )
    cr_list.insert( 0, cr_list.pop(-1) )
    
    print(cr_list)
    
    #result = subprocess.Popen( cr_list )
    #result.communicate()
    
    #os.system( vJoyConfig + ' ' + ' '.join( cr_list ) )
    
    result = subprocess.run( ' '.join(cr_list) )
    
    print('vJoy: Create returncode: {}'.format(result.returncode))
    if result.returncode != 0:
        raise vJoyConfigError('Failed to create vJoy device.')

    time.sleep(wait_for)

def vJoyNew(rID=1):
    global vJoy
    #vJoyConfig_Disable()
    #vJoyConfig_Delete(rID)
    vJoyConfig_Create(rID, force=True, buttons=128, analog_hat_switches=4)
    vJoyConfig_Enable()
    vJoy.vJoyEnabled()
    vJoy.AcquireVJD(rID)
    
class JOYSTICK_POSITION_V2(Structure):
    _fields_ = [
    ('bDevice', c_byte), # Index of device. Range 1-16

    ('wThrottle', c_long), # Not Used. Reserved.
    ('wRudder', c_long),   # Not Used. Reserved.
    ('wAileron', c_long),  # Not Used. Reserved.

    ('wAxisX', c_long), # X-Axis | Valid value for Axis members are in range 0x0000 – 0x8000.
    ('wAxisY', c_long), # Y-Axis
    ('wAxisZ', c_long), # Z-Axis

    ('wAxisXRot', c_long), # Rx-Axis
    ('wAxisYRot', c_long), # Ry-Axis
    ('wAxisZRot', c_long), # Rz-Axis

    ('wSlider', c_long),   # sl0-Axis
    ('wDial', c_long),     # sl1-Axis

    ('wWheel', c_long), # Not Used. Reserved.

    ('wAxisVX', c_long), # Not Used. Reserved.
    ('wAxisVY', c_long), # Not Used. Reserved.
    ('wAxisVZ', c_long), # Not Used. Reserved.

    ('wAxisVBRX', c_long), # Not Used. Reserved.
    ('wAxisVRBY', c_long), # Not Used. Reserved.
    ('wAxisVRBZ', c_long), # Not Used. Reserved.

    ('lButtons', c_long), # Buttons 1-32 | Valid value for Button members are in range 0x00000000 to 0xFFFFFFFF
    ('bHats', wintypes.DWORD ), # POV Cont Hat Switch #1 or if Disc; every nibble represents a Hat Switch.
    #Valid value for POV Hat Switch member is either 0xFFFFFFFF (neutral) or in the range of 0 to 35999 .
 
    ('bHatsEx1', wintypes.DWORD ), # POV Cont Hat Switch #2 if Disc; not used.
    ('bHatsEx2', wintypes.DWORD ), # POV Cont Hat Switch #3 if Disc; not used.
    ('bHatsEx3', wintypes.DWORD ), # POV Cont Hat Switch #4 if Disc; not used.

    ('lButtonsEx1', c_long), # Buttons 33-64
    ('lButtonsEx2', c_long), # Buttons 65-96
    ('lButtonsEx3', c_long)] # Buttons 97-128
 
    def __init__(self, rID, *args, **kwargs):
        self.bDevice = c_byte(rID)

        # Reset as dirty way to initialize.
        self.reset()

        super(JOYSTICK_POSITION_V2, self).__init__(*args, **kwargs)

    @property
    def X(self):
        return self.wAxisX

    @X.setter
    def X(self, value):
        self.wAxisX = c_long(value)

    @property
    def Y(self):
        return self.wAxisY

    @Y.setter
    def Y(self, value):
        self.wAxisY = c_long(value)

    @property
    def Z(self):
        return self.wAxisZ

    @Z.setter
    def Z(self, value):
        self.wAxisZ = c_long(value)

    @property
    def Rx(self):
        return self.wAxisXRot

    @Rx.setter
    def Rx(self, value):
        self.wAxisXRot = c_long(value)

    @property
    def Ry(self):
        return self.wAxisYRot

    @Ry.setter
    def Ry(self, value):
        self.wAxisYRot = c_long(value)

    @property
    def Rz(self):
        return self.wAxisZRot

    @Rz.setter
    def Rz(self, value):
        self.wAxisZRot = c_long(value)

    @property
    def sl0(self):
        return self.wSlider

    @sl0.setter
    def sl0(self, value):
        self.wSlider = c_long(value)

    @property
    def sl1(self):
        return self.wDial

    @sl1.setter
    def sl1(self, value):
        self.wDial = c_long(value)

    def reset(self, update=True):
        self.reset_hats(update=False)
        self.reset_btns(update=False)
        self.reset_axes(update=False)

        if update:
            self.update()

    def reset_hats(self, update=True):
        self.bHats    = -1
        self.bHatsEx1 = -1
        self.bHatsEx2 = -1
        self.bHatsEx3 = -1

        if update:
            self.update()

    def reset_buttons(self, update=True):
        self.lButtons = 0x00000000
        self.lButtonsEx1 = 0x00000000
        self.lButtonsEx2 = 0x00000000
        self.lButtonsEx3 = 0x00000000

        if update:
            self.update()

    def reset_btns(self, update=True):
        self.reset_buttons(update=update)

    def reset_axes(self, update=True):
        self.reset_xy(update=update)
        self.reset_z(update=update)

        self.reset_rxy(update=update)
        self.reset_rz(update=update)

        self.reset_sl0(update=update)
        self.reset_sl1(update=update)

    def reset_axes_xy(self, update=True):
        self.reset_axis_x(update=update)
        self.reset_axis_y(update=update)

    def reset_xy(self, update=True):
        self.reset_axes_xy(update=update)

    def reset_axis_x(self, update=True):
        self.X = 0x4000
        if update:
            self.update()

    def reset_x(self, update=True):
        self.reset_axis_x(update=update)

    def reset_axis_y(self, update=True):
        self.Y = 0x4000
        if update:
            self.update()

    def reset_y(self, update=True):
        self.reset_axis_y(update=update)

    def reset_axis_z(self, update=True):
        self.Z = 0x4000
        if update:
            self.update()

    def reset_z(self, update=True):
        self.reset_axis_z(update=update)

    def reset_rot_axes_xy(self, update=True):
        self.reset_rot_axis_x(update=update)
        self.reset_rot_axis_y(update=update)

    def reset_rot_xy(self, update=True):
        self.reset_rot_axes_xy(update=update)

    def reset_rxy(self, update=True):
        self.reset_rot_axes_xy(update=update)

    def reset_rot_axis_x(self, update=True):
        self.Rx = 0x4000
        if update:
            self.update()

    def reset_rot_x(self, update=True):
        self.reset_rot_axis_x(update=update)

    def reset_rx(self, update=True):
        self.reset_rot_axis_x(update=update)

    def reset_rot_axis_y(self, update=True):
        self.Ry = 0x4000
        if update:
            self.update()

    def reset_rot_y(self, update=True):
        self.reset_rot_axis_y(update=update)

    def reset_ry(self, update=True):
        self.reset_rot_axis_y(update=update)

    def reset_rot_axis_z(self, update=True):
        self.Rz = 0x4000
        if update:
            self.update()

    def reset_rot_z(self, update=True):
        self.reset_rot_axis_z(update=update)

    def reset_rz(self, update=True):
        self.reset_rot_axis_z(update=update)

    def reset_slider(self, update=True):
        self.sl0 = 0x4000
        if update:
            self.update()

    def reset_sl0(self, update=True):
        self.reset_slider(update=update)

    def reset_dial(self, update=True):
        self.sl1 = 0x4000
        if update:
            self.update()

    def reset_sl1(self, update=True):
        self.reset_dial(update=update)

    def update(self):
        vJoy.UpdateVJD(self.bDevice, self)

if __name__ == '__main__':
    rID = 1

    vJoyNew(rID=rID)
    
    '''
    #vJoyConfig_Delete(rID)

    #vJoyConfig_Get_Config()

    #vJoyConfig_Reset

    #Hat Controls.
    #    -1 or 36000 = neutral
    #     0 = North
    #  4500 = North-East
    #  9000 = East
    # 13500 = South-East
    # 18000 = South
    # 22500 = South-West
    # 27000 = West
    # 31500 = North-West
    print("Running Hat Test")
    for x in range(4):
        for y in range(0, 36000, 4500):
            vJoy.SetContPov(y, rID, x+1)
            time.sleep(.3)
        vJoy.SetContPov(-1, rID, x+1)

    #Axis Controls.
    #Between 0x0 and 0x8000
    print("Running Axes Test")
    for i in range(0x30, 0x37+0x01, 0x01):
        vJoy.SetAxis(0x8000, rID, i)
        time.sleep(.1)
        vJoy.SetAxis(0x0, rID, i)
        time.sleep(.1)
        vJoy.SetAxis(0x4000, rID, i)

    #Button Controls.
    #Between 1 and 128
    print("Running Button Test")
    for i in range(128):
        """Sets the state of a vJoy Button to on or off.  SetBtn(state,rID,buttonID)"""
        vJoy.SetBtn(1, rID, i+1)
        time.sleep(0.05)
        vJoy.SetBtn(0, rID, i+1)

    #vJoy.ResetButtons()
    #vJoy.ResetPovs()
    """Reset all axes and buttons to default for specified vJoy Device"""
    #vJoy.ResetVJD()
    
    print("Running jspos Test")
    jspos = JOYSTICK_POSITION_V2(rID)

    #buttons: | 1 | 2 | 3 | 4 |  5 |  6 |  7 |  8  |  9  |  10  |
    #values : | 1 | 2 | 4 | 8 | 16 | 32 | 64 | 128 | 512 | 1024 |
    #jspos.lButtons = 32+64+128 #Turn on buttons 6, 7, and 8

    jspos.bHats    = 0
    jspos.bHatsEx1 = 18000
    jspos.bHatsEx2 = 0
    jspos.bHatsEx3 = 18000

    jspos.lButtons = 0xFFFFFFFF
    jspos.lButtonsEx1 = 0xFFFFFFFF
    jspos.lButtonsEx2 = 0xFFFFFFFF
    jspos.lButtonsEx3 = 0xFFFFFFFF

    jspos.wAxisX = 0x8000
    jspos.wAxisY = 0x0000
    jspos.wAxisZ = 0x8000

    jspos.wAxisXRot = 0x0000
    jspos.wAxisYRot = 0x8000
    jspos.wAxisZRot = 0x0000

    jspos.wSlider = 0x8000
    jspos.wDial = 0x0000

    jspos.update()
    time.sleep(1)

    jspos.reset()

    #The 'efficient' method as described in vJoy's docs - set multiple values at once
    #j.data

    #j.data.lButtons = 19 # buttons number 1,2 and 5 (1+2+16)
    #j.data.wAxisX = 0x2000
    #j.data.wAxisY = 0x7500

    #send data to vJoy device
    #vJoy.UpdateVJD()

    #inverts logic for backwards Y axis.
    #prc = .25
    #print( round( abs(0x8000 * -prc) ) )
    '''
