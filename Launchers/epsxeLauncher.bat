@echo off

:: TODO: Read paths from config file.
set ePSXePath="J:\Games\Emus+Roms\PSX\Emulators\ePSXe\epsxe.exe"
set biosPath="J:\Games\Emus+Roms\PSX\Emulators\ePSXe\bios\SCPH1001.bin"
set gamePath="J:\Games\Emus+Roms\PSX\Roms\Final Fantasy Origins (v1.2).bin"

start "" %ePSXePath% -nogui -nolog -bios %biosPath% -loadbin %gamePath%

exit 0