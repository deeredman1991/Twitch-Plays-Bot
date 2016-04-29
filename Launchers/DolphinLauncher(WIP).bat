@echo off

:: TODO: Read paths from config file.
set DolphinPath="J:\Games\Emus+Roms\GameCube\Emulators\Dolphin-x64\Dolphin"
set gamePath="J:\Games\Emus+Roms\GameCube\Roms\Mario Party 7.iso"

start "" %DolphinPath% -e %gamePath%

exit 0