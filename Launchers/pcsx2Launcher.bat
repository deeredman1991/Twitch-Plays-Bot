@echo off

:: TODO: Read paths from config file.
set pcsx2Path="C:\Program Files (x86)\PCSX2 1.2.1\pcsx2-r5875.exe"
set gamePath="J:\Games\Emus+Roms\PS2\Roms\Kingdom Hearts.iso"

start "" %pcsx2Path% %gamePath%
::--fullboot

exit 0