# EXE 
as of today march 2017 the bot runs from a exe that you can  download from the releases tab
# V2 bot work no more Python 
V2 of are bot is in the works at https://github.com/plusrep/TWP

A twitch plays bot for twitch to send cmds to games for chat to play.
This is bot is based on and uses code from https://github.com/sunshinekitty/TwitchPlaysPokemon


### Prerequisities

You will need the following to run this bot.

Python 2.7 https://www.python.org/download/releases/2.7/

Pywin32 for Python 2.7 https://sourceforge.net/projects/pywin32/files/pywin32/Build%20220/

psutil for Python 2.7 https://pypi.python.org/pypi?:action=display&name=psutil#downloads




### Installing

You are now ready to start the bot. Now it will ask you a bunch of questions to help generate a settings file. The answers to those questions are outside the scope of this readme however knowing how to setup sunshinekitty's bot will help a LOT with knowing how to configure my bot as my bot uses sunshinekitty's code as a base.

Don't worry all of these settings can be changed later in the "settings.txt" file and as a bonus the "BUTTON_DELAY" setting can even be changed while the bot is running for on the fly fine tuning. (This is the only setting that can be adjusted without restarting 

### configuring


Please configure your emulator so that when the command is typed in chat the correct key on the emulator will be pressed.

For example; When a user types "up" or "u" in chat the bot will press "i" the emulator needs to know that "i" is the key for "D-Pad Up"

DPad Up: Key Pressed = i Chat Commands: 'up', 'u'

DPad Right: Key Pressed = l Chat Commands: 'right', 'r'

DPad Down: Key Pressed = k Chat Commands: 'down', 'd'

DPad Left: Key Pressed = j Chat Commands: 'left', 'l'

X: Key Pressed = z Chat Commands: 'x', 'cross'

A: Key Pressed = a Chat Commands: 'a'

O or B: Key Pressed = x Chat Commands: 'b', 'o', 'circle'

Square or Z: Key Pressed = s Chat Commands: 's', 'square', 'z'

Triangle or Y: Key Pressed = d Chat Commands: 't', 'triangle', 'y'

L1 or Lb: Key Pressed = q Chat Commands: 'l1', 'lb'

L2: Key Pressed = w Chat Commands: 'l2'

L3: Key Pressed = n Chat Commands: 'l3'

R1 or Rb: Key Pressed = e Chat Commands: 'r1', 'rb'

R2: Key Pressed = r Chat Commands: 'r2'

R3: Key Pressed = m Chat Commands: 'r3'

Start: Key Pressed = v Chat Commands: 'start' Select: Key Pressed = c Chat Commands: 'select'

Left Stick Up: Key Pressed = t Chat Commands: 'lsup', 'lsu', 'lup', 'lu', 'su', 'stickup'

Left Stick Right: Key Pressed = h Chat Commands: 'lsright', 'lsr', 'lright', 'lr', 'sr', 'stickright'

Left Stick Down: Key Pressed = g Chat Commands: 'lsdown', 'lsd', 'ldown', 'ld', 'sd', 'stickdown'

Left Stick Left: Key Pressed = f Chat Commands: 'lsleft', 'lsl', 'lleft', 'll', 'sl', 'stickleft'

Right Stick Up or C Up: Key Pressed = 7 Chat Commands: 'rsup', 'rsu', 'rup', 'ru', 'cup', 'cu'

Right Stick Right or C Right: Key Pressed = u Chat Commands: 'rsright', 'rsr', 'rright', 'rr' 'cright', 'cr'

Right Stick Down or C Down: Key Pressed = y Chat Commands: 'rsdown', 'rsd', 'rdown', 'rd' 'cdown', 'cd'

Right Stick Left or C Left: Key Pressed = 6 Chat Commands: 'rsleft', 'rsl', 'rleft', 'rl' 'cleft', 'cl'

Other Commands: Chat Commands:

	'cl' Other Commands: 	Chat Commands: 
	 		'!pausingon', '!pon', #Turns pausing on between key presses 
		 		'!pausingoff', '!poff', #Turns pausing off between key presses 
		 		Anarchy Only Commands: 
		 			'!smoothon', '!son', #Turns Smooth Movement on (i.e. Instead of pressing a button multiple times the bot will hold the button down.) 
			 			'!smoothoff', '!soff', #Turns Smooth Movement off (i.e. Instead of holding a button down the bot will press the button multiple times.) 
			 			'!autosmoothon', '!ason', #Auto smoothing will smooth or unsmooth a button automatically based on the "auto_smooth_settings" config file. 
			 			'!autosmoothoff', '!asoff', #Turns auto smoothing off. 
			 			'!hold <button>', '!h <button>' #Holds a button until the "release" command is pressed.
 			 			'!release <button>', '!r <button>', #Releases a button if it is currently being held down. 
			 			'!r all', #Releases all buttons currently being held down.






