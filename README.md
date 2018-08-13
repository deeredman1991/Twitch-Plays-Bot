 \***Twitch-Plays-Bot-Re-Write**\*
 ======
 
   #Dependencies: ( **what you need to install** )
   ------
  - [Python 3.5(64 bit)](https://www.python.org/ftp/python/3.5.0/python-3.5.0-amd64.exe)
  - [Kivy](https://github.com/KeyWeeUsr/KivyInstaller)
  - [psutil](https://pypi.org/project/psutil/)
  - [vJoy](http://vjoystick.sourceforge.net/site/index.php/download-a-install/download)
 
 #Installation: ( **Pre-alpha installation. Beta will run from an exe** )
 ------
  1. Install Python, during the install. 
  2. Make sure the installer adds Python to the "System Path Environment Variable" it does not do this by default.
  3. Install vJoy.
  4. Download the Kivy.bat file from KeyWeeUsr's github, place it into your Python directory; and run it.
  5. Open a cli and run the command; "python -m pip install --upgrade pip"
  6. After that command finishes, run the coomand; "python -m pip install psutil"
  7. Configure your bot.

#Configuration:
------
1. Download the bot from this github page.

2. Go into configs/default open login and enter the username of the bot, the oauth of the bot, and the streamer's chat that it should connect to.

3. Open emulator_settings and enter the path to the emulator, the process name, or the pid. This will allow the bot to get ahold of the emulator's process so that it can suspend and resume it for pausing and unpausing functionality. If you enter the emulator path, as an added convenience; the bot will start the emulator for you automatically. Only fill out one option. All other options should be set to 'false'.

4. Open a cli and cd into the Twitch-Plays-Bot folder and then run python -B main.py and the bot will start. 
*     Type ' cd "path/to/bot" ' no single quotes, yes double quotes, into the cli and press 'enter'.

5. Hit start session and the bot will run. You will know the bot has connected when it says "GO!" in the chat.

6. If you set "binding": 0 to 1 in the user_variables binding 1 waits for 2 seconds after recieveing a command before executing it so that you can config the keybindings by yourself by typing in a command and clicking on the keybind option in the program that you are using.

#Command Configuration:
------
 1. Command definitions are configured/created in "config\default\user_commands"

 2. A command definition has the following syntax ' "external_root arg1 arg2 arg3": "internal_root arg1 arg2 arg3" ' and consists of two properties; 
 *      an external command ( that chat uses )
 *      an internal command ( that the bot sees )
       
 3. Command definitions "link" the input of the external command to the input of the internal command useing "variables" and have the following syntax; "#(variable=default_value[:min_value][:max_value])" ( examples: #(var=1:0:10) or #(var=1:10) ) for external commands, located on the left of each command definition if only two values are specified; the bot will assume the second value is "max_value" and "#(variable)" for internal commands, located on the right of each command definition. A variable inside an external command definition MUST include a default value. Instead of using a variable; you may also pass a value directly into the internal command side of the command definition to limit the functionality of that command.
       
 4. The internal commands are as follows;
 *      :mash buttonID times delay hold_for,
 *      :tilt axisID degree hold_for smoothness,
 *      :hat hatID degree times delay hold_for,
 *      :wait wait_time, and 
 *      :set internal_variable_key value
       
 5. The arguments for commands are as follows;
 *      buttonID = The ID of the button. Integer between 1 and 128
 *      axisID = The ID of the axis. Integer between 1 and 8
 *      hatID = The ID of the hat. Integer between 1 and 4
 *      times = How many times to run the internal command. Integer between 1 and 128.
 *      delay = The delay between each time the internal command is run when the "times" argument is not 1. Decimal between 0.0 and infinity.
 *      hold_for = How long to hold the button/axis for in seconds. If hold_for is -1 the button/axis/hat will be held forever, if 0, the button will be released. Decimal between -1.0 and infinity.
 *      degree = The degree at which an axis is tilted or a hat is pushed. For axes; Integer between -1 and 1, For hats; Integer between -1 (north) and 360. ( -1 is release ).
 *      smoothness = Will smooth movement be applied to this axis? (If pausing is 1 and smoothness is 1; smooth movement only resets this axis if another command is sent that doesn't tilt this axis.). Integer either 0 or 1.
 *      wait_time = The amount of time to wait in seconds. Decimal between 0.0 and infinity.
 *      internal_variable = Set an internal_variable, such as "pausing", or "binding" to a value. Any.


#Aliasing Configuration:
------
  1. The bot only sees numbers and so, to combat this problem; we have created an "aliasing" system. There are; button aliases defined in the "button_aliases" file that are used by the internal ":mash" command, axes aliases defined in the "axes_aliases" file that are used by the internal ":tilt" command, and degrees aliases definited in the "degrees_aliases" file that are used by both the ":tilt" command, and the ":hat" command.
       
 2. An alias is definied as follows "key": "value" where "key" is a word without spaces and "value" is a number or decimal covered in sub-section 5 of the #Command Configuration section.
       
 3. Defined aliases can be used by chat and in the command definition.
 
#Multi-Commands:
------
 1. It is possible to enter two or more commands at the same time using a multi-command. By default the syntax is as follows:
 *     root1 arg arg; root arg arg; root arg arg
 
 2. It is also possible to specify a custom delimiter in the "user_variables.json" config file. For example; you may specify that the delimiter be "," and then the syntax of the above multi-command would change to the following:
 *     root1 arg arg, root arg arg, root arg arg

#Internal Variables:
------
 1. Internal variables consist of a key and a value. Internal variables can have any combination of keys and values but, at the moment, there are only 3 that are useful.
 *     pausing; Pauses the emulator when buttons are not being pressed.; enabled = 1, disabled = 0.
 *     binding; Creates a 2 second delay between recieving a command, and executing a command. This is useful for setting up keybindings by yourself.; enabled = 1, disabled = 0
 *     multi_command_limit; The maximum number of commands a user is allowed to specify in one line with a Multi-Command.
 *     multi_command_delimiter; The character to be used between separate commands in a Multi-Command.
