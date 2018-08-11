  **Twitch-Plays-Bot-Re-Write**
  
  
 **what you need to install**
  
  [Python 3.5(64 bit)](https://www.python.org/ftp/python/3.5.0/python-3.5.0-amd64.exe)
  
  [Kivy](https://github.com/KeyWeeUsr/KivyInstaller)
  
  [psutil](https://pypi.org/project/psutil/)
  
  [vJoy](http://vjoystick.sourceforge.net/site/index.php/download-a-install/download)
 
 #Installation:
 ------
  1. Install Python, during the install. 
  2. Make sure the installer adds Python to the "System Path Environment Variable" it does not do this by default.
  3. Install vJoy.
  4. Download the Kivy.bat file from KeyWeeUsr's github, place it into your Python directory; and run it.
  5. Open a cli and run the command; "python -m pip install --upgrade pip"
  6. After that command finishes, run the coomand; "python -m pip install psutil"
  7. Configure your bot.

  **Pre alpha setup beta will run from a exe**

#Configuration:
------
1. Download the bot from this github page.

2. Go into configs then default then setup login with the username of the bot, the oauth of the bot, and the
*      streamer's chat that it should connect to.

3. Setup emulator_settings so that it knows what emu it needs to boot.

4. Open a cli and cd into the Twitch-Plays-Bot folder and then run python -B main.py and the bot will start.
*     (type 'cd "<path to bot>"' no single quotes, yes double quotes, into the cli)

5. Hit start session and the bot will run. You will know the bot has connected when it says: GO! in the chat.

6. If you set binding": 0 to 1 in the user_variables binding 1 waits for 2 seconds after recieveing a command before
*      executing it so that you can config the input keybinds from chat like up down and so on.

#Command Configuration:
------
 1. Command definitions are configured/created in "config\default\user_commands"

 2. A command definition consists of two properties; 
 *      an external command( that chat uses ) and an internal command( that the bot sees ) that
 *      use the following syntax "root arg1 arg2 arg3": "root arg1 arg2 arg3"
       
 3. Command definitions "link" the input of the external command to the input of the internal command useing
 *      "variables" and have the following syntax; "#(variable=default_value)" for external commands, located 
 *      (to the left of the ':') and "#(variable)" for internal commands (on the right of the ':')
 *      A variable inside an external command definition MUST include a default value. Instead of using a 
 *      variable; you may also pass a value directly into the internal command to limit the functionality 
 *      of that command.
       
 4. The internal commands are as follows;
 *      :mash buttonID times delay hold_for,
 *      :tilt axisID degree hold_for,
 *      :hat hatID degree times delay hold_for,
 *      :wait wait_time, and 
 *      :set internal_variable_key value
       
 5. The arguments for commands are as follows;
 *      buttonID = The ID of the button. Integer between 1 and 128
 *      axisID = The ID of the axis. Integer between 1 and 8
 *      hatID = The ID of the hat. Integer between 1 and 4
 *      times = How many times to run the internal command. Integer between 1 and 128
 *      delay = The delay between each time the internal command is run when specifying the "times" arguments. Decimal between 0.0 and infinity.
 *      hold_for = How long to hold the button/axis for in seconds. Decimal between 0.1 and infinity.
 *      degree = The degree at which an axis is tilted or a hat is pushed. For axes; Integer between -1 and 1, For hats; Integer between 0 (north) and 360. ( -1 is release )
 *      wait_time = The amount of time to wait in seconds. Decimal between 0.0 and infinity.
 *      internal_variable = Set an internal_variable, such as "pausing", or "binding" to a value. Any


#Aliasing Configuration:
------
  1. The bot only sees numbers and so, to combat this problem; we have created an "aliasing" system. There are;
  *      button aliases defined in the "button_aliases" file that are used by the internal ":mash" command, 
  *      axes aliases defined in the "axes_aliases" file that are used by the internal ":tilt" command,
  *      and degrees aliases definited in the "degrees_aliases" file that are used by both the ":tilt" command, and 
  *      the ":hat" command.
       
 2. An alias is definied as follows "key": "value" where "key" is a word without spaces and "value" is a
 *      number or decimal covered in sub-section 5 of the #Command Configuration section.
       
 3. Defined aliases can be used by chat and in the command definition.

#Internal Variables:
------
 1. Internal variables consist of a key and a value. Internal variables can have any combination of keys 
 *      and values but, at the moment, there are only 3 that are useful.
 *          - pausing; Pauses the emulator when buttons are not being pressed.; enabled = 1, disabled = 0.
 *          - smooth_movement; When tilting an axis it will continue to hold that axis between tilts so 
 *               that running back to back tilt commands feel more fluid.; enabled = 1, disabled = 0
 *          - binding; Creates a 2 second delay between recieving a command, and executing a command. This
 *               is useful for setting up keybindings by yourself.; enabled = 1, disabled = 0
