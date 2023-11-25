@echo off
cd %~dp0

set DRIVE_LETTER=l


if exist %DRIVE_LETTER%:\ (
	echo Unmounting drive...
	rem net use %DRIVE_LETTER%: /DELETE
	subst %DRIVE_LETTER%: /D
)

echo Mounting drive...
rem net use %DRIVE_LETTER%: \\192.168.1.1\shared /user:smb smb
subst %DRIVE_LETTER%: .

TIMEOUT /T 5
