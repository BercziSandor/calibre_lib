@echo off
REM Change the following Samba server path according to your setup
set "samba_server=\\192.168.1.1\data\shared"

REM Iterate through subdirectories under "..\libs"
for /d %%i in ("..\libs\*") do (
    call :syncFolder %%~nxi
)
pause

goto :eof

:syncFolder
REM Function to sync a folder to the Samba server
set folder=%1
if not "%folder:~0,1%"== "." (
    robocopy "..\libs\%folder%" "%samba_server%\www\ebooks\%folder%" /mir /fft /z /xa:sh
)

goto :eof
