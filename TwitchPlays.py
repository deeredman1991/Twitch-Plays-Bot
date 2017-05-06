#!/usr/bin/env python3

# Launch.py
# Copyright (C) 2014 : Alex Edwards
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#

import ConfigParser
import os
import string
import time
import socket
import threading
import win32com.client
import win32api
iport win32con
import psutil
import math
import sys

settings = []
SMOOTH_MOVEMENT = False
AUTOSMOOTHING = True
assettings = []
assettingsdict = {}

commands = []
readbuffer = ""
GAME = os.listdir('game')[0]

if GAME == '.sav':
	GAME = os.listdir('game')[1]

shell = win32com.client.Dispatch("WScript.Shell")
EMUPROCESSSTATUS = 'running'
EMUPROCESSID = 'No Process ID'
EMUPROCESS = 'No Process'
consoleLock = threading.Lock()
PAUSELASTADJUSTED = time.time()
HOLDING = {}
lastButton = None
#HOLDINGTHREADS = {}

VK_CODE = {'backspace':0x08,
					'tab':0x09,
					'clear':0x0C,
					'enter':0x0D,
					'shift':0x10,
					'ctrl':0x11,
					'alt':0x12,
					'pause':0x13,
					'caps_lock':0x14,
					'esc':0x1B,
					'spacebar':0x20,
					'page_up':0x21,
					'page_down':0x22,
					'end':0x23,
					'home':0x24,
					'left_arrow':0x25,
					'up_arrow':0x26,
					'right_arrow':0x27,
					'down_arrow':0x28,
					'select':0x29,
					'print':0x2A,
					'execute':0x2B,
					'print_screen':0x2C,
					'ins':0x2D,
					'del':0x2E,
					'help':0x2F,
					'0':0x30,
					'1':0x31,
					'2':0x32,
					'3':0x33,
					'4':0x34,
					'5':0x35,
					'6':0x36,
					'7':0x37,
					'8':0x38,
					'9':0x39,
					'a':0x41,
					'b':0x42,
					'c':0x43,
					'd':0x44,
					'e':0x45,
					'f':0x46,
					'g':0x47,
					'h':0x48,
					'i':0x49,
					'j':0x4A,
					'k':0x4B,
					'l':0x4C,
					'm':0x4D,
					'n':0x4E,
					'o':0x4F,
					'p':0x50,
					'q':0x51,
					'r':0x52,
					's':0x53,
					't':0x54,
					'u':0x55,
					'v':0x56,
					'w':0x57,
					'x':0x58,
					'y':0x59,
					'z':0x5A,
					'numpad_0':0x60,
					'numpad_1':0x61,
					'numpad_2':0x62,
					'numpad_3':0x63,
					'numpad_4':0x64,
					'numpad_5':0x65,
					'numpad_6':0x66,
					'numpad_7':0x67,
					'numpad_8':0x68,
					'numpad_9':0x69,
					'multiply_key':0x6A,
					'add_key':0x6B,
					'separator_key':0x6C,
					'subtract_key':0x6D,
					'decimal_key':0x6E,
					'divide_key':0x6F,
					'F1':0x70,
					'F2':0x71,
					'F3':0x72,
					'F4':0x73,
					'F5':0x74,
					'F6':0x75,
					'F7':0x76,
					'F8':0x77,
					'F9':0x78,
					'F10':0x79,
					'F11':0x7A,
					'F12':0x7B,
					'F13':0x7C,
					'F14':0x7D,
					'F15':0x7E,
					'F16':0x7F,
					'F17':0x80,
					'F18':0x81,
					'F19':0x82,
					'F20':0x83,
					'F21':0x84,
					'F22':0x85,
					'F23':0x86,
					'F24':0x87,
					'num_lock':0x90,
					'scroll_lock':0x91,
					'left_shift':0xA0,
					'right_shift ':0xA1,
					'left_control':0xA2,
					'right_control':0xA3,
					'left_menu':0xA4,
					'right_menu':0xA5,
					'browser_back':0xA6,
					'browser_forward':0xA7,
					'browser_refresh':0xA8,
					'browser_stop':0xA9,
					'browser_search':0xAA,
					'browser_favorites':0xAB,
					'browser_start_and_home':0xAC,
					'volume_mute':0xAD,
					'volume_Down':0xAE,
					'volume_up':0xAF,
					'next_track':0xB0,
					'previous_track':0xB1,
					'stop_media':0xB2,
					'play/pause_media':0xB3,
					'start_mail':0xB4,
					'select_media':0xB5,
					'start_application_1':0xB6,
					'start_application_2':0xB7,
					'attn_key':0xF6,
					'crsel_key':0xF7,
					'exsel_key':0xF8,
					'play_key':0xFA,
					'zoom_key':0xFB,
					'clear_key':0xFE,
					'+':0xBB,
					',':0xBC,
					'-':0xBD,
					'.':0xBE,
					'/':0xBF,
					'`':0xC0,
					';':0xBA,
					'[':0xDB,
					'\\':0xDC,
					']':0xDD,
					"'":0xDE,
					'`':0xC0}
				
def holdThread(button):
	win32api.keybd_event(VK_CODE[button], 0, 0, 0)
	while HOLDING[button] == True:
		time.sleep(.1)
	win32api.keybd_event(VK_CODE[button], 0, win32con.KEYEVENTF_KEYUP ,0)
	return
				
def isFloatOrDigit(x):
	try:
		float(x)
		return True
	except:
		return False
				
def press(button, holdTime='1'):
	global EMUPROCESS, shell, MAX_CONSECUTIVE_INPUTS, EMUPROCESSSTATUS, HOLDING, s, out, lastButton#, HOLDINGTHREADS
		
	if isFloatOrDigit(str(holdTime)):
		holdTime = float(holdTime)
		if holdTime > MAX_CONSECUTIVE_INPUTS:
			holdTime = float(MAX_CONSECUTIVE_INPUTS)
		elif holdTime < 0:
			return
				
	with consoleLock:
		print " "
		print "---EXECUTING COMMAND---"
		if SMOOTH_MOVEMENT == True:
			print "Command = Hold " + str(button) + ' for ' + str(holdTime) + ' second(s)'
		else:
			print "Command = Press " + str(button) + ' ' + str(holdTime) + ' time(s)'
	if PAUSING == True and APP.lower() != 'pcsx2':
		with consoleLock:
			print "Resuming Process"
			print "Process Status is " + str( EMUPROCESS.status() )
		EMUPROCESS.resume()
		time.sleep(0.1)
		while EMUPROCESS.status() != 'running':
			EMUPROCESS.resume()
			time.sleep(0.1)
			with consoleLock:
				print "Process Status is " + str( EMUPROCESS.status() )
		EMUPROCESSSTATUS = 'running'
	elif PAUSING == True and APP.lower() == 'pcsx2':
		if EMUPROCESSSTATUS == 'suspended':
			with consoleLock:
				print "Resuming Process"
			getEmuProcessID()
			EMUPROCESS.resume()
			EMUPROCESSSTATUS = 'running'
			time.sleep(0.05)
	
	if button != lastButton or PAUSING == False:
		if lastButton:
			win32api.keybd_event(VK_CODE[lastButton], 0, win32con.KEYEVENTF_KEYUP ,0)
			lastButton = None
		
	if APP.lower() != 'pcsx2':
		with consoleLock:
				print "Setting Emulator as Active Window!"
		shell.SendKeys("%")
		shell.AppActivate(EMUPROCESSID)
		
	if button == '!wait':
		if lastButton:
			win32api.keybd_event(VK_CODE[lastButton], 0, win32con.KEYEVENTF_KEYUP ,0)
			lastButton = None
		if ( holdTime == '!hold' or holdTime == '!h' ) or ( holdTime == '!release' or holdTime == '!r' ):
			s.send(bytes("PRIVMSG #%s :Hold/Release and Wait are not compatible holding for 1 second!\r\n" % (CHAT_CHANNEL) ))
			holdTime = 1
		time.sleep(holdTime)
		button = None
		
	if str(holdTime).lower() == '!hold' or str(holdTime).lower() == '!h': #Consider making !hold and !release NOT unpause the emulator when pausing is on if possible
		if button:
			win32api.keybd_event(VK_CODE[button], 0, 0, 0)
			HOLDING[button] = True
			s.send(bytes("PRIVMSG #%s :Holding %s!\r\n" % (CHAT_CHANNEL, out.lower()) ))
		
		'''
		HOLDING.update( { button.lower(): True } )
		HOLDINGTHREADS.update({ button.lower(): threading.Thread(target = holdThread, args = (button.lower())) })
		HOLDINGTHREADS[button.lower()].start()
		'''
	elif str(holdTime).lower() == '!release' or str(holdTime).lower() == '!r':
		if out.lower() == 'all':
			s.send(bytes("PRIVMSG #%s :Releasing all buttons!\r\n" % (CHAT_CHANNEL) ))
			for k, v in HOLDING.iteritems():
				if v == True:
					win32api.keybd_event(VK_CODE[k], 0, win32con.KEYEVENTF_KEYUP ,0)
					HOLDING[k] = False
		elif button:
			win32api.keybd_event(VK_CODE[button], 0, win32con.KEYEVENTF_KEYUP ,0)
			HOLDING[button] = False
			s.send(bytes("PRIVMSG #%s :Releasing %s!\r\n" % (CHAT_CHANNEL, out.lower()) ))
				
		'''
		if HOLDING[button.lower()]:
			HOLDING.update( { button.lower(): False } )
			if HOLDINGTHREADS[button.lower()]:
				HOLDINGTHREADS[button.lower()].join()
		'''
	
	with consoleLock:
		print "Pressing Buttons!"
	try:
		HOLDING[button]
	except:
		HOLDING[button] = False
	if button and ( isFloatOrDigit(str(holdTime)) and HOLDING[button] != True ):
		if SMOOTH_MOVEMENT == True:
			if PAUSING == True:
				if button == lastButton:
					time.sleep(BUTTON_DELAY*holdTime)
				else:
					if lastButton:
						win32api.keybd_event(VK_CODE[lastButton], 0, win32con.KEYEVENTF_KEYUP ,0)
						lastButton = None
					win32api.keybd_event(VK_CODE[button], 0, 0, 0)
					time.sleep(BUTTON_DELAY*holdTime)
				with consoleLock:
					print "Held " + str(button) + " for " + str(holdTime) + " iteration(s)."
				lastButton = button
			else:
				if lastButton:
					win32api.keybd_event(VK_CODE[lastButton], 0, win32con.KEYEVENTF_KEYUP ,0)
					lastButton = None
				win32api.keybd_event(VK_CODE[button], 0, 0, 0)
				time.sleep(BUTTON_DELAY*holdTime)
				win32api.keybd_event(VK_CODE[button], 0, win32con.KEYEVENTF_KEYUP ,0)
		else:
			if lastButton:
				win32api.keybd_event(VK_CODE[lastButton], 0, win32con.KEYEVENTF_KEYUP ,0)
				lastButton = None
			for i in range( int( round( holdTime ) ) ):
				win32api.keybd_event(VK_CODE[button], 0, 0, 0)
				time.sleep(BUTTON_DELAY)
				win32api.keybd_event(VK_CODE[button],0 ,win32con.KEYEVENTF_KEYUP ,0)
				with consoleLock:
					print "Pressed " + str(button) + " " + str(i+1) + " time(s)."
				time.sleep(0.2)
	with consoleLock:
		print "Done Pressing Buttons!"
		
	if PAUSING == True and APP.lower() != 'pcsx2':
		with consoleLock:
			print "Suspending Process"
			print "Process Status is " + str( EMUPROCESS.status() )
		EMUPROCESS.suspend()
		time.sleep(0.5)
		while EMUPROCESS.status() != 'stopped':
			EMUPROCESS.suspend()
			time.sleep(0.5)
			with consoleLock:
				print "Process Status is " + str( EMUPROCESS.status() )
		EMUPROCESSSTATUS = 'suspended'
	elif PAUSING == True and APP.lower() == 'pcsx2':
		if EMUPROCESSSTATUS == 'running':
			with consoleLock:
				print "Suspending Process"
			getEmuProcessID()
			EMUPROCESS.suspend()
			EMUPROCESSSTATUS = 'suspended'
			time.sleep(0.5)
			
	if mode.lower() != "democracy":
		addtofile()
			
def updateButtonDelay():
	if os.path.isfile("settings.txt"):
		config = ConfigParser.ConfigParser()
		config.read("settings.txt")
		BUTTON_DELAY = config.getfloat('Settings', 'BUTTON_DELAY')
		return BUTTON_DELAY
	else:
		with consoleLock:
			print "[CRITICAL SUPER IMPORTANT ERROR!!!] there is no 'settings.txt' file! Setting button delay to 0.15 (you should seriously fix this though.)"
		return 0.15
	
def addtofile():
	if len(commands) >= command_length:
		del commands[0]
	if mode.lower() == 'anarchy':
		commands.extend([user[1:] + out.lower() + " " + str(repeatTimes)])
		
	else:
		commands.extend([user[1:] + out.lower()])
		
	# Write to file for stream view
	with open("commands.txt", "w") as f:
		for item in commands:
			f.write(item + '\n')

def startEmulator():
	with consoleLock:
		print("Starting %s" % GAME)
	emulator_thread = threading.Thread(target = runEmulator, args = ())
	emulator_thread.start()
	
	with consoleLock:
		raw_input("Press Enter to Start!")
		print 'Starting in...'
		print '~*3*~'
		time.sleep(0.5)
		print ' *2* '
		time.sleep(0.5)
		print ' *1* '
		time.sleep(0.5)
		print ' GO! '
		time.sleep(0.1)
	
	getEmuProcessID()

def runEmulator():
	if os.path.splitext(os.listdir('game')[0])[1] != ".sav":
		os.system('"%s\game\%s"' % (os.getcwd(), GAME))
	
def getEmuProcessID():
	global EMUPROCESSID, EMUPROCESS
	while EMUPROCESSID == 'No Process ID':
		for proc in psutil.process_iter():
			try:
				pinfo = proc.as_dict(attrs=['pid', 'name'])
				#print str(pinfo['name']) + ' ~:~ ' + str(pinfo['pid'])
				if pinfo['name'] == 'ePSXe.exe' and APP.lower() == 'epsxe':
					with consoleLock:
						print 'Found process ePSXe.exe! PID: ' + str(pinfo['pid'])
					EMUPROCESSID = pinfo['pid']
					EMUPROCESS = psutil.Process(EMUPROCESSID)
				elif 'pcsx2' in pinfo['name'] and '.exe' in pinfo['name'] and APP.lower() == 'pcsx2':
					with consoleLock:
						print 'Found process ' + pinfo['name'] + ' PID: ' + str(pinfo['pid'])
					EMUPROCESSID = pinfo['pid']
					EMUPROCESS = psutil.Process(EMUPROCESSID)
				elif pinfo['name'] == 'VisualBoyAdvance.exe' and APP.lower() == 'vba':
					with consoleLock:
						print 'Found process VisualBoyAdvance.exe! PID: ' + str(pinfo['pid'])
					EMUPROCESSID = pinfo['pid']
					EMUPROCESS = psutil.Process(EMUPROCESSID)
				elif pinfo['name'] == "Dolphin.exe" and APP.lower() == 'dolphin':
					with consoleLock:
						print 'Found process Dolphin.exe! PID: ' + str(pinfo['pid'])
					EMUPROCESSID = pinfo['pid']
					EMUPROCESS = psutil.Process(EMUPROCESSID)
				elif pinfo['name'] == "ggpofba-ng.exe" and APP.lower() == 'fightcade':
					with consoleLock:
						print 'Found process Fightcade.exe! PID: ' + str(pinfo['pid'])
					EMUPROCESSID = pinfo['pid']
					EMUPROCESS = psutil.Process(EMUPROCESSID)
			except psutil.NoSuchProcess:
				pass
	
def democracy():
	global s, EMUPROCESSSTATUS
	last_command = time.time()
	lsu_counter = 0
	lsr_counter = 0
	lsd_counter = 0
	lsl_counter = 0
	rsu_counter = 0
	rsr_counter = 0
	rsd_counter = 0
	rsl_counter = 0
	up_counter = 0
	right_counter = 0
	down_counter = 0
	left_counter = 0
	start_counter = 0
	select_counter = 0
	a_counter = 0
	b_counter = 0
	s_counter = 0
	t_counter = 0
	lb_counter = 0
	lt_counter = 0
	l3_counter = 0
	rb_counter = 0
	rt_counter = 0
	r3_counter = 0
	pausing_counter = 0
	unpausing_counter = 0
	
	selected_c = "None"
	
	while True:
		if time.time() > last_command + democracy_time:
			last_command = time.time()
			with votes_Lock:
				for user, vote in votes.iteritems():
					if vote == '!pausingon':
						pausing_counter = pausing_counter + 1
					elif vote == '!pausingoff':
						unpausing_counter = unpausing_counter + 1
					elif vote == 'lsup' or vote == 'lsu' or vote == 'lup' or vote == 'lu' or vote == 'su' or vote == 'stickup':
						lsu_counter = lsu_counter + 1
					elif vote == 'lsright' or vote == 'lsr' or vote == 'lright' or vote == 'lr' or vote == 'sr' or vote == 'stickright':
						lsr_counter = lsr_counter + 1
					elif vote == 'lsdown' or vote == 'lsd' or vote == 'ldown' or vote == 'ld' or vote == 'sd' or vote == 'stickdown':
						lsd_counter = lsd_counter + 1
					elif vote == 'lsleft' or vote == 'lsl' or vote == 'lleft' or vote == 'll' or vote == 'sl' or vote == 'stickleft':
						lsl_counter = lsl_counter + 1
					elif vote == 'rsup' or vote == 'rsu' or vote == 'rup' or vote == 'ru' or vote == 'cu' or vote == 'cup':
						rsu_counter = rsu_counter + 1
					elif vote == 'rsright' or vote == 'rsr' or vote == 'rright' or vote == 'rr' or vote == 'cr' or vote == 'cright':
						rsr_counter = rsr_counter + 1
					elif vote == 'rsdown' or vote == 'rsd' or vote == 'rdown' or vote == 'rd' or vote == 'cd' or vote == 'cdown':
						rsd_counter = rsd_counter + 1
					elif vote == 'rsleft' or vote == 'rsl' or vote == 'rleft' or vote == 'rl' or vote == 'cl' or vote == 'cleft':
						print "added to counter"
						rsl_counter = rsl_counter + 1
					elif vote == "up" or vote == "u":
						up_counter = up_counter + 1
					elif vote == "right" or vote == "r":
						right_counter = right_counter + 1
					elif vote == "down" or vote == "d":
						down_counter = down_counter + 1
					elif vote == "left" or vote == "l":
						left_counter = left_counter + 1
					elif vote == "a" or vote == "x" or vote == "cross":
						a_counter = a_counter + 1
					elif vote == "b" or vote == "o" or vote == "circle":
						b_counter = b_counter + 1
					elif vote == "s" or vote == "square" or vote == "z":
						s_counter = s_counter + 1
					elif vote == "t" or vote == "triangle":
						t_counter = t_counter + 1
					elif vote == "l1" or vote == "lb":
						lb_counter = lb_counter + 1
					elif vote == "l2":
						lt_counter = lt_counter + 1	
					elif vote == "l3":
						l3_counter = l3_counter + 1	
					elif vote == "r1" or vote == "rb":
						rb_counter = rb_counter + 1
					elif vote == "r2":
						rt_counter = rt_counter + 1
					elif vote == "r3":
						r3_counter = r3_counter + 1
					elif vote == "start":
						start_counter = start_counter + 1
					elif vote == "select":
						select_counter = select_counter + 1
						
			alloutputs = {'Up': up_counter, 'Right': right_counter, 'Down': down_counter, 'Left': left_counter, 
				'Start': start_counter, 'Select': select_counter, 'B': b_counter, 'A': a_counter, 'S': s_counter, 'T': t_counter, 
				'LB': lb_counter, 'L2': lt_counter, 'L3': l3_counter, 'RB': rb_counter, 'R2': rt_counter, 'R3': r3_counter,
				'Left Stick Up': lsu_counter, 'Left Stick Right': lsr_counter, 'Left Stick Down': lsd_counter, 'Left Stick Left': lsl_counter, 
				'Right Stick Up': rsu_counter, 'Right Stick Right': rsr_counter, 'Right Stick Down': rsd_counter, 'Right Stick Left': rsl_counter,
				'Pausing On': pausing_counter, 'Pausing Off': unpausing_counter
				}
			if(up_counter + right_counter + down_counter + left_counter + start_counter + select_counter + b_counter + a_counter + s_counter + t_counter + b_counter + lt_counter + rb_counter + rt_counter + lsu_counter + lsr_counter + lsd_counter + lsl_counter + rsu_counter + rsr_counter + rsd_counter + rsl_counter + pausing_counter + unpausing_counter + l3_counter + r3_counter == 0):
				selected_c = "None"
			else:
				selected_c = max(alloutputs, key = alloutputs.get)
				sendToChat = selected_c
				if APP.lower() == 'epsxe' or APP.lower() == 'pcsx2':
					if sendToChat.lower() == 'b':
						sendToChat = 'o'
					elif sendToChat.lower() == 's':
						sendToChat = 'square'
					elif sendToChat.lower() == 't':
						sendToChat = 'triangle'
					elif sendToChat.lower() == 'lb':
						sendToChat = 'l1'
					elif sendToChat.lower() == 'rb':
						sendToChat = 'l2'
				s.send(bytes( "PRIVMSG #%s : '%s' Won!\r\n" % (CHAT_CHANNEL, str(sendToChat.upper())) ))
				
			with open("lastsaid.txt", "w") as f:
				f.write("Selected %s\n" % selected_c)
				f.write("Time left: %s" % str(democracy_time)[0:1])
			with votes_Lock:
				votes.clear()
			BUTTON_DELAY = updateButtonDelay()
			
			if selected_c.lower() == 'pausing on':
				if EMUPROCESSSTATUS == 'running':
					EMUPROCESS.suspend()
					EMUPROCESSSTATUS = 'suspended'
				s.send(bytes("PRIVMSG #%s :Pausing is On!\r\n" % CHAT_CHANNEL))
			elif selected_c.lower() == 'pausing off':
				PAUSING = False
				if EMUPROCESSSTATUS == 'suspended':
					PAUSING = False
					EMUPROCESS.resume()
					EMUPROCESSSTATUS = 'running'
				s.send(bytes("PRIVMSG #%s :Pausing is Off!\r\n" % CHAT_CHANNEL))
			elif selected_c.lower() == 'left stick up':
				press('t')
			elif selected_c.lower() == 'left stick right':
				press('h')
			elif selected_c.lower() == 'left stick down':
				press('g')
			elif selected_c.lower() == 'left stick left':
				press('f')
			elif selected_c.lower() == 'right stick up':
				press('7')
			elif selected_c.lower() == 'right stick down':
				press('u')
			elif selected_c.lower() == 'right stick right':
				press('y')
			elif selected_c.lower() == 'right stick left':
				press('6')
			elif selected_c.lower() == 'up':
				press('i')
			elif selected_c.lower() == 'right':
				press('l')
			elif selected_c.lower() == 'down':
				press('k')
			elif selected_c.lower() == 'left':
				press('j')
			elif selected_c.lower() == 'a':
				press('z')
			elif selected_c.lower() == 'b':
				press('x')
			elif selected_c.lower() == 's':
				press('s')
			elif selected_c.lower() == 't':
				press('d')
			elif selected_c.lower() == 'lb':
				press('q')
			elif selected_c.lower() == 'l2':
				press('w')
			elif selected_c.lower() == 'l3':
				press('n')
			elif selected_c.lower() == 'rb':
				press('e')
			elif selected_c.lower() == 'r2':
				press('r')
			elif selected_c.lower() == 'r3':
				press('m')
			elif selected_c.lower() == 'start':
				press('v')
			elif selected_c.lower() == 'select':
				press('c')
					
			lsu_counter = 0
			lsr_counter = 0
			lsd_counter = 0
			lsl_counter = 0
			rsu_counter = 0
			rsr_counter = 0
			rsd_counter = 0
			rsl_counter = 0
			up_counter = 0
			right_counter = 0
			down_counter = 0
			left_counter = 0
			start_counter = 0
			select_counter = 0
			a_counter = 0
			b_counter = 0
			s_counter = 0
			t_counter = 0
			lb_counter = 0
			lt_counter = 0
			l3_counter = 0
			rb_counter = 0
			rt_counter = 0
			r3_counter = 0
			pausing_counter = 0
			unpausing_counter = 0
			
		else:
			with open("lastsaid.txt", "w") as f:
				f.write("Selected %s\n" % selected_c)
				f.write("Time left: %s" % str(1.0 + last_command + democracy_time - time.time())[0:1])
		time.sleep(1)
		
# Generate a config file if one doesn't exist
while True:
	if os.path.isfile("settings.txt"):
		config = ConfigParser.ConfigParser()
		config.read("settings.txt")
		HOST = config.get('Settings', 'HOST')
		PORT = config.getint('Settings', 'PORT')
		AUTH = config.get('Settings', 'AUTH')
		NICK = config.get('Settings', 'USERNAME').lower()
		APP = config.get('Settings', 'APP')
		CHAT_CHANNEL = config.get('Settings', 'CHAT_CHANNEL').lower()
		command_length = config.getint('Settings', 'LENGTH')
		BUTTON_DELAY = config.getfloat('Settings', 'BUTTON_DELAY')
		PAUSING = config.getboolean('Settings', 'PAUSING')
		AUTOSMOOTHING = config.getboolean('Settings', 'AUTOSMOOTHING')
		MAX_CONSECUTIVE_INPUTS = config.getint('Settings', 'MAX_CONSECUTIVE_INPUTS')
		PAUSING_COOLDOWN = config.getint('Settings', 'PAUSING_COOLDOWN')
		break
	else:
		with consoleLock:
			print("Let's make you a config file")
		settings.append("; Settings for Twitch Plays bot")
		settings.append("; Thanks to RDJ, MZ, AP, Oriax & Dee\n")
		
		settings.append("[Settings]\n")
		
		settings.append("; Where you're connecting to, if it's Twitch leave it as is")
		with consoleLock:
			print("Where you're connecting to, if it's Twitch use irc.chat.twitch.tv")
			settings_host = raw_input("Hostname: ")
		settings.append("HOST = " + settings_host + "\n")
		
		settings.append("; Port number, probably should use 6667")
		with consoleLock:
			print("Port number, probably should use 6667")
			settings_port = raw_input("Port: ")
		settings.append("PORT = " + settings_port + "\n")
		
		settings.append("; Auth token, grab this from http://www.twitchapps.com/tmi")
		with consoleLock:
			print("Auth token, grab this from http://www.twitchapps.com/tmi")
			settings_auth = raw_input("Auth Token: ")
		settings.append("AUTH = " + settings_auth + "\n")
		
		settings.append("; Your Twitch Bot's Username")
		with consoleLock:
			print("Your Twitch Bot's Username")
			settings_bot = raw_input("Bot's Username: ")
		settings.append("USERNAME = " + settings_bot + "\n")
		
		settings.append("; Name of the application you run the file from")
		settings.append("; Currently Supported: vba, epsxe, and pcsx2 fightcade,")
		with consoleLock:
			print("Name of the application you run the file from.")
			print("Currently Supported: vba, epsxe, pcsx2 fightcade,")
			settings_app = raw_input("Application name: ")
		settings.append("APP = " + settings_app + "\n")
		
		settings.append("; Username of who's channel you're connecting to")
		with consoleLock:
			print("Username of who's channel you're connecting to")
			settings_chat = raw_input("Username: ")
		settings.append("CHAT_CHANNEL = " + settings_chat + "\n")
		
		settings.append("; The maximum number of lines in commands.txt (Useful for showing commands received in stream)")
		with consoleLock:
			print("The maximum number of lines in commands.txt (Useful for showing commands received in stream)")
			settings_length = raw_input("Length: ")
		settings.append("LENGTH = " + settings_length + "\n")
		
		settings.append("; The number of seconds to hold a button down for.")
		settings.append("; 0.15 Recommended for Final Fantasy Origins (epsxe)")
		settings.append("; 0.35 Recommended for Harvest Moon - Back to Nature (epsxe)")
		settings.append("; 0.28 Recommended for Harvest Moon - Friends of Mineral Town (vba)")
		with consoleLock:
			print("The number of seconds to hold a button down for.")
			print("0.15 Recommended for Final Fantasy Origins (epsxe)")
			print("0.35 Recommended for Harvest Moon - Back to Nature (epsxe)")
			print("0.28 Recommended for Harvest Moon - Friends of Mineral Town (vba)")
		
			settings_button_delay = raw_input("BUTTON DELAY: ")
		settings.append("BUTTON_DELAY = " + settings_button_delay + "\n")
		
		settings.append("; If PAUSING is true the game will pause between button presses.")
		settings.append("; This option is recommended for real time games but not for turn based games.")
		with consoleLock:
			print("If PAUSING is true the game will pause between button presses.")
			print("This option is recommended for real time games but not for turn based games.")
			settings_pausing = raw_input("PAUSING: ")
		settings.append("PAUSING = " + settings_pausing + "\n")
		
		settings.append("; If AUTOSMOOTHING is true characters will use automatic smoothing by default as set by the auto_smooth_settings.txt config file")
		settings.append("; smoothing holds a button instead of pressing it")
		with consoleLock:
			print("If AUTOSMOOTHING is true characters will use automatic smoothing by default as set by the auto_smooth_settings.txt config file")
			print("smoothing holds a button instead of pressing it")
			settings_smooth_movement = raw_input("AUTOSMOOTHING: ")
		settings.append("AUTOSMOOTHING = " + settings_smooth_movement + "\n")
		
		settings.append("; MAX_CONSECUTIVE_INPUTS is the maximum number of inputs a player is allowed to make in one command durring anarchy mode.")
		with consoleLock:
			print("MAX_CONSECUTIVE_INPUTS is the maximum number of inputs a player is allowed to make in one command durring anarchy mode.")
			settings_max_consecutive_inputs = raw_input("MAX_CONSECUTIVE_INPUTS: ")
		settings.append("MAX_CONSECUTIVE_INPUTS = " + settings_max_consecutive_inputs + "\n")
		
		settings.append("; PAUSING_COOLDOWN is the minimum amount of time a player must wait between pauses in anarchy mode.")
		with consoleLock:
			print("PAUSING_COOLDOWN is the minimum amount of time a player must wait between pauses in anarchy mode.")
			settings_pausing_cooldown = raw_input("PAUSING_COOLDOWN: ")
		settings.append("PAUSING_COOLDOWN = " + settings_pausing_cooldown + "\n")
		
		with open("settings.txt", "w") as f:
			for each_setting in settings:
				f.write(each_setting + '\n')
	
# Generate an autosmoothing config file if one doesn't exist
while True:
	if os.path.isfile("auto_smooth_settings.txt"):
		config = ConfigParser.ConfigParser()
		config.read("auto_smooth_settings.txt")
		
		assettingsdict["LeftStickUp"] = config.getboolean('Settings', 'LeftStickUp')
		assettingsdict["LeftStickRight"] = config.getboolean('Settings', 'LeftStickRight')
		assettingsdict["LeftStickDown"] = config.getboolean('Settings', 'LeftStickDown')
		assettingsdict["LeftStickLeft"] = config.getboolean('Settings', 'LeftStickLeft')
		
		assettingsdict["RightStickUp/CUp"] = config.getboolean('Settings', 'RightStickUp/CUp')
		assettingsdict["RightStickDown/CDown"] = config.getboolean('Settings', 'RightStickDown/CDown')
		assettingsdict["RightStickRight/CRight"] = config.getboolean('Settings', 'RightStickRight/CRight')
		assettingsdict["RightStickLeft/CLeft"] = config.getboolean('Settings', 'RightStickLeft/CLeft')
		
		assettingsdict["L2"] = config.getboolean('Settings', 'L2')
		assettingsdict["R2"] = config.getboolean('Settings', 'R2')
		
		assettingsdict["Up"] = config.getboolean('Settings', 'Up')
		assettingsdict["Right"] = config.getboolean('Settings', 'Right')
		assettingsdict["Down"] = config.getboolean('Settings', 'Down')
		assettingsdict["Left"] = config.getboolean('Settings', 'Left')
		
		assettingsdict["X"] = config.getboolean('Settings', 'X')
		assettingsdict["A"] = config.getboolean('Settings', 'A')
		assettingsdict["O/B"] = config.getboolean('Settings', 'O/B')
		assettingsdict["Triangle/Y"] = config.getboolean('Settings', 'Triangle/Y')
		assettingsdict["Square/Z"] = config.getboolean('Settings', 'Square/Z')
		
		assettingsdict["L1"] = config.getboolean('Settings', 'L1')
		assettingsdict["R1"] = config.getboolean('Settings', 'R1')
		assettingsdict["L3"] = config.getboolean('Settings', 'L3')
		assettingsdict["R3"] = config.getboolean('Settings', 'R3')
		
		assettingsdict["Start"] = config.getboolean('Settings', 'Start')
		assettingsdict["Select"] = config.getboolean('Settings', 'Select')
		break
	else:
		with consoleLock:
			print("Let's make you a config file")
		assettings.append("; Auto Smoothing Settings for Twitch Plays bot")
		assettings.append("; Settings are optimized for Kingdom Hearts")
		assettings.append("; Thanks to Dee\n")
		
		assettings.append("[Settings]\n")
		
		assettings.append("LeftStickUp = True")
		assettings.append("LeftStickRight = True")
		assettings.append("LeftStickDown = True")
		assettings.append("LeftStickLeft = True")
		
		assettings.append("RightStickUp/CUp = False")
		assettings.append("RightStickDown/CDown = False")
		assettings.append("RightStickRight/CRight = False")
		assettings.append("RightStickLeft/CLeft = False")
		
		assettings.append("L2 = True")
		assettings.append("R2 = True")
		
		assettings.append("Up = False")
		assettings.append("Right = False")
		assettings.append("Down = False")
		assettings.append("Left = False")
		
		assettings.append("X = False")
		assettings.append("A = False")
		assettings.append("O/B = False")
		assettings.append("Triangle/Y = False")
		assettings.append("Square/Z = False")
		
		assettings.append("L1 = False")
		assettings.append("R1 = False")
		assettings.append("L3 = False")
		assettings.append("R3 = False")
		
		assettings.append("Start = False")
		assettings.append("Select = False")
		
		with open("auto_smooth_settings.txt", "w") as f:
			for each_setting in assettings:
				f.write(each_setting + '\n')
	
# Select game type    
while True:
	with consoleLock:
		print("Currently available: Anarchy, Democracy")
		mode = raw_input("Game type: ")
	if mode.lower() == "anarchy":
		break
	if mode.lower() == "democracy":
		with consoleLock:
			print("Takes most said command every X second(s): ")
		democracy_time = float(input("(must be integer) X="))
		break

# Anarchy Game Mode
if mode.lower() == "anarchy":
	with open("lastsaid.txt", "w") as f:
		f.write("")
	
	s=socket.socket( )
	s.connect((HOST, PORT))

	s.send(bytes("PASS %s\r\n" % AUTH))
	s.send(bytes("NICK %s\r\n" % NICK))
	s.send(bytes("USER %s %s bla :%s\r\n" % (NICK, HOST, NICK)))
	
	startEmulator()
	
	if APP.lower() != 'pcsx2':
		while EMUPROCESS.status() != 'stopped' and PAUSING == True:
			EMUPROCESS.suspend()
			EMUPROCESSSTATUS = 'suspended'
			with consoleLock:
				print "Suspending Process"
				print "Process Status is " + str( EMUPROCESS.status() )
	else:
		if PAUSING == True:
			getEmuProcessID()
			EMUPROCESS.suspend()
			EMUPROCESSSTATUS = 'suspended'
		
	s.send(bytes("JOIN #%s\r\n" % CHAT_CHANNEL));
	s.send(bytes("PRIVMSG #%s :GO!\r\n" % CHAT_CHANNEL))
	with consoleLock:
		print("Sent connected message to channel %s" % CHAT_CHANNEL)
	
	while 1:
		readbuffer = readbuffer+s.recv(1024).decode("UTF-8", errors="ignore")
		temp = str.split( str( readbuffer.encode("UTF-8", errors="ignore") ), "\n")
		readbuffer=temp.pop( )

		for line in temp:
			x = 0
			out = ""
			repeatTimes = 1
			line = str.rstrip(line)
			line = str.split(line)

			# for %Key%, %Value% in line
			for index, i in enumerate(line):
				if x == 0:
					user = line[index]
					user = user.split('!')[0]
					user = user[0:12] + ": "
				elif x == 3:
					out += line[index]
					out = out[1:]
				elif x == 4:
					repeatTimes = line[index]
					if repeatTimes.isdigit():
						repeatTimes = float(repeatTimes)
				elif x >= 5:
					out += " " + line[index]
				x = x + 1
			
			# Respond to ping, squelch useless feedback given by twitch, print output and read to list
			if user == "PING: ":
				s.send(bytes("PONG tmi.twitch.tv\r\n"))
			elif user == ":tmi.twitch.tv: ":
				pass
			elif user == ":tmi.twitch.: ":
				pass
			elif user == ":%s.tmi.twitch.tv: " % NICK:
				pass
			else:
				try:
					with consoleLock:
						print(user + out + ' ' + str(repeatTimes))
				except UnicodeEncodeError:
					with consoleLock:
						print(user)
				
			# Take in output
			if ( out.lower() == '!hold' or out.lower() == '!h' ) or ( out.lower() == '!release' or out.lower() == '!r' ) or out.lower() == 'all':
				tmp = repeatTimes
				repeatTimes = out
				out = str(tmp).lower()
			
			BUTTON_DELAY = updateButtonDelay()
			
			if out.lower() == '!smoothon' or out.lower() == '!son':
				SMOOTH_MOVEMENT = True
				s.send(bytes("PRIVMSG #%s :Smooth Movement On!\r\n" % CHAT_CHANNEL))
				
			elif out.lower() == '!smoothoff' or out.lower() == '!soff':
				SMOOTH_MOVEMENT = False
				s.send(bytes("PRIVMSG #%s :Smooth Movement Off!\r\n" % CHAT_CHANNEL))
			
			elif out.lower() == '!autosmoothon' or out.lower() == '!ason':
				AUTOSMOOTHING = True
				s.send(bytes("PRIVMSG #%s :Auto Smoothing On!\r\n" % CHAT_CHANNEL))
			
			elif out.lower() == '!autosmoothoff' or out.lower() == '!asoff':
				AUTOSMOOTHING = False
				SMOOTH_MOVEMENT = False
				s.send(bytes("PRIVMSG #%s :Auto Smoothing Off!\r\n" % CHAT_CHANNEL))
				s.send(bytes("PRIVMSG #%s :Smooth Movement Off!\r\n" % CHAT_CHANNEL))
				
			elif out.lower() == '!pausingon' or out.lower() == '!pon':
				if time.time() > PAUSELASTADJUSTED + PAUSING_COOLDOWN:
					PAUSING = True
					if EMUPROCESSSTATUS == 'running':
						getEmuProcessID()
						EMUPROCESS.suspend()
						EMUPROCESSSTATUS = 'suspended'
					s.send(bytes("PRIVMSG #%s :Pausing is On!\r\n" % CHAT_CHANNEL))
					PAUSELASTADJUSTED = time.time()
				else:
					s.send(bytes("PRIVMSG #%s :Pausing was recently adjusted!\r\n" % CHAT_CHANNEL))
					
			elif out.lower() == '!pausingoff' or out.lower() == '!poff':
				if time.time() > PAUSELASTADJUSTED + PAUSING_COOLDOWN:
					if EMUPROCESSSTATUS == 'suspended':
						PAUSING = False
						getEmuProcessID()
						EMUPROCESS.resume()
						EMUPROCESSSTATUS = 'running'
					time.sleep(0.1)
					if lastButton:
						win32api.keybd_event(VK_CODE[lastButton], 0, win32con.KEYEVENTF_KEYUP ,0)
						lastButton = None
					s.send(bytes("PRIVMSG #%s :Pausing is Off!\r\n" % CHAT_CHANNEL))
					PAUSELASTADJUSTED = time.time()
				else:
					s.send(bytes("PRIVMSG #%s :Pausing was recently adjusted!\r\n" % CHAT_CHANNEL))
			
			elif out.lower() == '!wait' or out.lower() == '!w':
				press( '!wait', holdTime=repeatTimes )
				
			elif out.lower() == 'all':
				if repeatTimes == '!r' or repeatTimes == '!repeat':
					press( 'all', holdTime=repeatTimes )
					
			elif out.lower() == 'lsup' or out.lower() == 'lsu' or out.lower() == 'lup' or out.lower() == 'lu' or out.lower() == 'su' or out.lower() == 'stickup':
				if AUTOSMOOTHING:
					if assettingsdict['LeftStickUp'] == True:
						SMOOTH_MOVEMENT = True
					else:
						SMOOTH_MOVEMENT = False
				press('t', holdTime=repeatTimes)
			elif out.lower() == 'lsright' or out.lower() == 'lsr' or out.lower() == 'lright' or out.lower() == 'lr' or out.lower() == 'sr' or out.lower() == 'stickright':
				if AUTOSMOOTHING:
					if assettingsdict['LeftStickRight'] == True:
						SMOOTH_MOVEMENT = True
					else:
						SMOOTH_MOVEMENT = False
				press('h', holdTime=repeatTimes)
			elif out.lower() == 'lsdown' or out.lower() == 'lsd' or out.lower() == 'ldown' or out.lower() == 'ld' or out.lower() == 'sd' or out.lower() == 'stickdown':
				if AUTOSMOOTHING:
					if assettingsdict['LeftStickDown'] == True:
						SMOOTH_MOVEMENT = True
					else:
						SMOOTH_MOVEMENT = False
				press('g', holdTime=repeatTimes)
			elif out.lower() == 'lsleft' or out.lower() == 'lsl' or out.lower() == 'lleft' or out.lower() == 'll' or out.lower() == 'sl' or out.lower() == 'stickleft':
				if AUTOSMOOTHING:
					if assettingsdict['LeftStickLeft'] == True:
						SMOOTH_MOVEMENT = True
					else:
						SMOOTH_MOVEMENT = False
				press('f', holdTime=repeatTimes)
			elif out.lower() == 'rsup' or out.lower() == 'rsu' or out.lower() == 'rup' or out.lower() == 'ru' or out.lower() == 'cup' or out.lower() == 'cu':
				if AUTOSMOOTHING:
					if assettingsdict['RightStickUp/CUp'] == True:
						SMOOTH_MOVEMENT = True
					else:
						SMOOTH_MOVEMENT = False
				press('7', holdTime=repeatTimes)
			elif out.lower() == 'rsright' or out.lower() == 'rsr' or out.lower() == 'rright' or out.lower() == 'rr' or out.lower() == 'cright' or out.lower() == 'cr':
				if AUTOSMOOTHING:
					if assettingsdict['RightStickRight/CRight'] == True:
						SMOOTH_MOVEMENT = True
					else:
						SMOOTH_MOVEMENT = False
				press('u', holdTime=repeatTimes)
			elif out.lower() == 'rsdown' or out.lower() == 'rsd' or out.lower() == 'rdown' or out.lower() == 'rd' or out.lower() == 'cdown' or out.lower() == 'cd':
				if AUTOSMOOTHING:
					if assettingsdict['RightStickDown/CDown'] == True:
						SMOOTH_MOVEMENT = True
					else:
						SMOOTH_MOVEMENT = False
				press('y', holdTime=repeatTimes)
			elif out.lower() == 'rsleft' or out.lower() == 'rsl' or out.lower() == 'rleft' or out.lower() == 'rl' or out.lower() == 'cleft' or out.lower() == 'cl':
				if AUTOSMOOTHING:
					if assettingsdict['RightStickLeft/CLeft'] == True:
						SMOOTH_MOVEMENT = True
					else:
						SMOOTH_MOVEMENT = False
				press('6', holdTime=repeatTimes)
			elif out.lower() == 'up' or out.lower() == 'u':
				if AUTOSMOOTHING:
					if assettingsdict['Up'] == True:
						SMOOTH_MOVEMENT = True
					else:
						SMOOTH_MOVEMENT = False
				press('i', holdTime=repeatTimes)
			elif out.lower() == 'right' or out.lower() == 'r':
				if AUTOSMOOTHING:
					if assettingsdict['Right'] == True:
						SMOOTH_MOVEMENT = True
					else:
						SMOOTH_MOVEMENT = False
				press('l', holdTime=repeatTimes)
			elif out.lower() == 'down' or out.lower() == 'd':
				if AUTOSMOOTHING:
					if assettingsdict['Down'] == True:
						SMOOTH_MOVEMENT = True
					else:
						SMOOTH_MOVEMENT = False
				press('k', holdTime=repeatTimes)
			elif out.lower() == 'left' or out.lower() == 'l':
				if AUTOSMOOTHING:
					if assettingsdict['Left'] == True:
						SMOOTH_MOVEMENT = True
					else:
						SMOOTH_MOVEMENT = False
				press('j', holdTime=repeatTimes)
			elif out.lower() == 'x' or out.lower() == 'cross':
				if AUTOSMOOTHING:
					if assettingsdict['X'] == True:
						SMOOTH_MOVEMENT = True
					else:
						SMOOTH_MOVEMENT = False
				press('z', holdTime=repeatTimes)
			elif out.lower() == 'a':
				if AUTOSMOOTHING:
					if assettingsdict['A'] == True:
						SMOOTH_MOVEMENT = True
					else:
						SMOOTH_MOVEMENT = False
				press('a', holdTime=repeatTimes)
			elif out.lower() == 'b' or out.lower() == 'o' or out.lower() == 'circle':
				if AUTOSMOOTHING:
					if assettingsdict['O/B'] == True:
						SMOOTH_MOVEMENT = True
					else:
						SMOOTH_MOVEMENT = False
				press('x', holdTime=repeatTimes)
			elif out.lower() == 's' or out.lower() == 'square' or out.lower() == 'z':
				if AUTOSMOOTHING:
					if assettingsdict['Square/Z'] == True:
						SMOOTH_MOVEMENT = True
					else:
						SMOOTH_MOVEMENT = False
				press('s', holdTime=repeatTimes)
			elif out.lower() == 't' or out.lower() == 'triangle':
				if AUTOSMOOTHING:
					if assettingsdict['Triangle/Y'] == True:
						SMOOTH_MOVEMENT = True
					else:
						SMOOTH_MOVEMENT = False
				press('d', holdTime=repeatTimes)
			elif out.lower() == 'l1' or out.lower() == 'lb':
				if AUTOSMOOTHING:
					if assettingsdict['L1'] == True:
						SMOOTH_MOVEMENT = True
					else:
						SMOOTH_MOVEMENT = False
				press('q', holdTime=repeatTimes)
			elif out.lower() == 'l2':
				if AUTOSMOOTHING:
					if assettingsdict['L2'] == True:
						SMOOTH_MOVEMENT = True
					else:
						SMOOTH_MOVEMENT = False
				press('w', holdTime=repeatTimes)
			elif out.lower() == 'l3':
				if AUTOSMOOTHING:
					if assettingsdict['L3'] == True:
						SMOOTH_MOVEMENT = True
					else:
						SMOOTH_MOVEMENT = False
				press('m', holdTime=repeatTimes)
			elif out.lower() == 'r1' or out.lower() == 'rb':
				if AUTOSMOOTHING:
					if assettingsdict['R1'] == True:
						SMOOTH_MOVEMENT = True
					else:
						SMOOTH_MOVEMENT = False
				press('e', holdTime=repeatTimes)
			elif out.lower() == 'r2':
				if AUTOSMOOTHING:
					if assettingsdict['R2'] == True:
						SMOOTH_MOVEMENT = True
					else:
						SMOOTH_MOVEMENT = False
				press('r', holdTime=repeatTimes)
			elif out.lower() == 'r3':
				if AUTOSMOOTHING:
					if assettingsdict['R3'] == True:
						SMOOTH_MOVEMENT = True
					else:
						SMOOTH_MOVEMENT = False
				press('n', holdTime=repeatTimes)
			elif out.lower() == 'start':
				if AUTOSMOOTHING:
					if assettingsdict['Start'] == True:
						SMOOTH_MOVEMENT = True
					else:
						SMOOTH_MOVEMENT = False
				press('v', holdTime=repeatTimes)
			elif out.lower() == 'select':
				if AUTOSMOOTHING:
					if assettingsdict['Select'] == True:
						SMOOTH_MOVEMENT = True
					else:
						SMOOTH_MOVEMENT = False
				press('c', holdTime=repeatTimes)
			
			out = 'None'
			
# Democracy Game Mode
if mode.lower() == "democracy":
	with open("lastsaid.txt", "w") as f:
		f.write("")
	
	startEmulator()

	s=socket.socket( )
	s.connect((HOST, PORT))
	
	s.send(bytes("PASS %s\r\n" % AUTH))
	s.send(bytes("NICK %s\r\n" % NICK))
	s.send(bytes("USER %s %s bla :%s\r\n" % (NICK, HOST, NICK)))
		
	startEmulator()
		
	if APP.lower() != 'pcsx2':
		while EMUPROCESS.status() != 'stopped' and PAUSING == True:
			EMUPROCESS.suspend()
			EMUPROCESSSTATUS = 'suspended'
			with consoleLock:
				print "Suspending Process"
				print "Process Status is " + str( EMUPROCESS.status() )
	else:
		if PAUSING == True:
			getEmuProcessID()
			EMUPROCESS.suspend()
			EMUPROCESSSTATUS = 'suspended'
			
	votes = {}
	votes_Lock = threading.Lock()

	count_job = threading.Thread(target = democracy, args = ())
	count_job.start()
	
	s.send(bytes("JOIN #%s\r\n" % CHAT_CHANNEL));
	s.send(bytes("PRIVMSG #%s :Start Voting!\r\n" % CHAT_CHANNEL))
	with consoleLock:
		print("Sent Start Voting message to channel %s" % CHAT_CHANNEL)
	
	while 1:
		readbuffer = readbuffer+s.recv(1024).decode("UTF-8", errors="ignore")
		temp = str.split(str(readbuffer), "\n")
		readbuffer=temp.pop( )
				
		for line in temp:
			x = 0
			out = ""
			line = str.rstrip(line)
			line = str.split(line)

			for index, i in enumerate(line):
				if x == 0:
					user = line[index]
					user = user.split('!')[0]
					user = user[0:12] + ": "
				if x == 3:
					out += line[index]
					out = out[1:]
				if x >= 4:
					out += " " + line[index]
				x = x + 1
			
			# Respond to ping, squelch useless feedback given by twitch, print output and read to list
			if user == "PING: ":
				s.send(bytes("PONG tmi.twitch.tv\r\n"))
			elif user == ":tmi.twitch.tv: ":
				pass
			elif user == ":tmi.twitch.: ":
				pass
			elif user == ":%s.tmi.twitch.tv: " % NICK:
				pass
			else:
				try:
					with consoleLock:
						print(user + out)
				except UnicodeEncodeError:
					with consoleLock:
						print(user)
				
			# Take in output
			validInputs = [
			'up', 'u', 'right', 'r', 'down', 'd', 'left', 'l', 
			'a', 
			'x', 'cross',
			'b', 'o', 'circle', 
			's','square', 'z',
			't', 'triangle',
			'l1', 'lb', 'l2', 'l3', 'r1', 'rb', 'r2', 'r3', 
			'start', 'select',
			'lsup', 'lsu', 'lup', 'lu', 'su', 'stickup',
			'lsright', 'lsr', 'lright', 'lr', 'sr', 'stickright',
			'lsdown', 'lsd', 'ldown', 'ld', 'sd', 'stickdown',
			'lsleft', 'lsl', 'lleft', 'll', 'sl', 'stickleft',
			'rsup', 'rsu', 'rup', 'ru', 'cu', 'cup',
			'rsright', 'rsr', 'rright', 'rr', 'cr', 'cright',
			'rsdown', 'rsd', 'rdown', 'rd', 'cd', 'cdown',
			'rsleft', 'rsl', 'rleft', 'rl', 'cl', 'cleft',
			'!pausingon', '!pausingoff'
			]
			if out.lower() in validInputs:
				print str(out.lower()) + " is valid input!"
				with votes_Lock:
					votes[user] = out.lower()
					addtofile()
			out = 'None'
