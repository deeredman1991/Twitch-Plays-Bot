from threading import Lock, Thread
import time
import numbers
import json
import io

import scripts.vigem as j


class Joystick(object):
    def __init__(self, *args, rID=1, configs={}, configs_filepath='', **kwargs):
        self.rID = rID
    
        self.last_tilted_axis = None
        self.last_tilted_axis_smoothness = 0
        self.last_tilted_axis_hold_for = 0
        self.last_tilted_axis_lock = Lock()
        
        self.configs_filepath = configs_filepath

        self.user_variables = configs['user_variables']
        self.user_variables_lock = Lock()
        
    #Writes a new value to the user_variable list and then updates the .json with the new values.
    def set_user_variable(self, key, value):
        self.check_last_smooth_axis()

        def write_json( dict, jsn ):
            with io.open( self.configs_filepath + jsn + '.json', 'w', encoding='utf-8' ) as outfile:
                json.dump( dict, outfile, ensure_ascii=False )

        with self.user_variables_lock:
            print("[JoyStick: {}]: Setting {} to {}".format(self.rID, key, value))
            self.user_variables[key] = value
            write_json( self.user_variables, 'user_variables' )
            print("[JoyStick: {}]: {} was set to {}".format(self.rID, key, self.user_variables[key]))
            
    #Updates the user_variables from configs.
    def update_configs(self, configs={}):
        if 'user_variables' in configs:
            with self.user_variables_lock:
                self.user_variables = configs['user_variables']

    # Presses a Button.
    def mash(self, button, hold_for):
        #a hold_for of -1 will hold indefinately
        #a hold_for of  0 will release.
        
        if type(button) != type(1):
            print( '!!!ERROR!!! : ' \
                'Mash command told to mash button '\
                '{} which is of type {}. Mash command can only '\
                'mash buttons of type integer'.format(button, type(button)) )
            return
        if not isinstance(hold_for, numbers.Number):
            print( '!!!ERROR!!! : ' \
                'Mash command told to mash button {} for {} seconds.'\
                ' Expected hold_for to be a number got {}'.format( 
                                                            button, 
                                                            hold_for, 
                                                            type(hold_for) ) )
            return

        #Make sure that we have the joystick and copy the "user_variables" list 
        #   in case it changes while the command is running.
        j.vJoy.AcquireVJD(self.rID)
        user_variables = self.user_variables.copy()

        #Helps the user make keybinds in the game.
        if user_variables['binding']:
            time.sleep(2)

        # Checks to see if the last axis was smooth, if it was; resets it to a neutral position.
        self.check_last_smooth_axis()
            
        if hold_for != 0:
            print('[JoyStick: {}]: Pressing Button {}'.format(self.rID, button))
            j.vJoy.SetBtn( 1, self.rID, button )
        if hold_for >= 0:
            time.sleep( hold_for )
            j.vJoy.SetBtn( 0, self.rID, button )
            print('[JoyStick: {}]: Releasing Button {}'.format(self.rID, button))
            
    # Presses a Hat Switch.
    def hat(self, hat, degree, hold_for):
        
        #---Degree Table---
        #  0       : North
        # 45       : N/E
        # 90       : East
        #135       : S/E
        #180       : South
        #225       : S/W
        #270       : West
        #315       : N/W
        #360 or -1 : Neutral

        if type(hat) != type(1):
            print( '!!!ERROR!!! : ' \
                'Hat command told to use hat '\
                '{} which is of type {}. Hat\'s '\
                'are supposed to be of type integer'.format(hat, type(hat)) )
            return
        if not isinstance(degree, numbers.Number):
            print( '!!!ERROR!!! : ' \
                'Hat command told to set hat {} to {} degrees.'\
                ' Expected degrees to be a number got {}'.format( 
                                                            hat, 
                                                            degree, 
                                                            type(degree) ) )
            return
        if not isinstance(hold_for, numbers.Number):
            print( '!!!ERROR!!! : ' \
                'Hat command told to use hat {} for {} seconds.'\
                ' Expected hold_for to be a number got {}'.format( 
                                                            hat, 
                                                            hold_for, 
                                                            type(hold_for) ) )
            return

        #Make sure that we have the joystick and copy the "user_variables" list 
        #   in case it changes while the command is running.
        j.vJoy.AcquireVJD(self.rID)
        user_variables = self.user_variables.copy()
        
        #Helps the user make keybinds in the game.
        if user_variables['binding']:
            time.sleep(2)

        # Checks to see if the last axis was smooth, if it was; resets it to a neutral position.
        self.check_last_smooth_axis()
            
        # A hold_for of 0 will release but not push.
        if hold_for != 0:
            print('[JoyStick: {}]: Setting Hat #{} to {} degrees for {} seconds'.format(
                        self.rID, hat, degree, hold_for))

            #We range from 0-360 while vJoy ranges from 0 to 36000 so
            #   We have to multiply our degree value by 100 to convert for
            #   vJoy.
            degree = degree*100
            # Push Hat Switch.
            j.vJoy.SetContPov(degree, self.rID, hat)

        # A hold_for of -1 (or any negative value) will push, but not release.
        if hold_for >= 0:
            time.sleep( hold_for )
            # Release Hat Switch.
            j.vJoy.SetContPov(-1, self.rID, hat)
            print('[JoyStick: {}]: Releasing Hat #{}'.format(
                            self.rID, hat))

    # Checks to see if the last axis was smooth, if it was; resets it to a neutral position.
    def check_last_smooth_axis(self, current_axis=None):
        #If smooth_movement is on and the axis being tilted is not the last axis that was tilted; 
        #   release the last axis that was tilted.
        if current_axis != self.last_tilted_axis and self.last_tilted_axis_smoothness and self.last_tilted_axis_hold_for > -1:
            print(self.last_tilted_axis_hold_for)
            j.vJoy.SetAxis( 0x4000, self.rID, self.last_tilted_axis )
            print('[JoyStick: {}]: Setting axis {} to 0 degrees'.format(self.rID, self.last_tilted_axis-0x2F))

    # Tilts an axis.
    def tilt(self, axis, degree, hold_for, smoothness):
        #degree between -1 and 1
        
        if type(axis) != type(1):
            print( '!!!ERROR!!! : ' \
                'Tilt command told to tilt axis '\
                '{} which is of type {}. axes '\
                'are supposed to be of type integer'.format(axis, type(axis)) )
            return
        if not isinstance(degree, numbers.Number):
            print( '!!!ERROR!!! : ' \
                'Tilt command told to tilt axis {} to {} degrees.'\
                ' Expected degree to be a number got {}'.format( 
                                                            axis, 
                                                            degree, 
                                                            type(degree) ) )
            return
        if not isinstance(hold_for, numbers.Number):
            print( '!!!ERROR!!! : ' \
                'Axis command told to tilt axis {} for {} seconds.'\
                ' Expected hold_for to be a number got {}'.format( 
                                                            axis, 
                                                            hold_for, 
                                                            type(hold_for) ) )
            return
        
        #Make sure that we have the joystick and copy the "user_variables" list 
        #   in case it changes while the command is running.
        j.vJoy.AcquireVJD(self.rID)
        user_variables = self.user_variables.copy()

        #Helps the user make keybinds in the game.
        if user_variables['binding']:
            time.sleep(2)

        # Checks to see if the last axis was smooth, if it was; resets it to a neutral position.
        self.check_last_smooth_axis(current_axis=axis)

        original_axis = axis
        vjoy_axis = axis + 0x2F

        #A hold_for of 0 will release but not tilt.
        if hold_for != 0:
            print( '[JoyStick: {}]: Setting axis {} to {} degrees for {} seconds'.format(self.rID, axis, degree, hold_for) )

            # For some reason vJoy inverts the y axis so that -1 is forwards while 1 is backwards.
            # So if we are dealing with the y axis (aka axis number 48 / 0x31) we have to invert our degrees.
            if vjoy_axis == 0x31:
                degree = -degree

            #degree can be -1, 0, or 1. In order to work with vJoy we need to convert our numbers to 
            #   non-negative values ranging from 0x0 to 0x8000.
            #We add 1 so that -1.0 becomes 0.0, 0.0 becomes 1.0, and 1.0 becomes 2.0.
            #   this way we can multiply by 0x4000 to convert our -1:1 degree system to their
            #   0x0:0x8000 degree system.
            degree = int((degree+1)*0x4000)

            #Tilt Axis
            j.vJoy.SetAxis( degree, self.rID, vjoy_axis )

            #Store the current axis as the last_tilted_axis
            #   for smooth_movement.
            self.last_tilted_axis = vjoy_axis
            self.last_tilted_axis_hold_for = hold_for
            self.last_tilted_axis_smoothness = smoothness

        # A hold_for of -1 (or any negative value) will tilt, but not release.
        if hold_for >= 0:
            # Wait between press and release.
            time.sleep( hold_for )
            # Only release if smooth_movement is not active.
            if not user_variables['pausing'] or not smoothness:
                # Tilt Axis.
                j.vJoy.SetAxis( 0x4000, self.rID, vjoy_axis )
                print('[JoyStick: {}]: Setting axis {} to 0 degrees'.format(self.rID, original_axis))