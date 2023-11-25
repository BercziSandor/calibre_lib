@echo off
cd %~dp0

set SOURCE=%USERPROFILE%\Documents\Calibre\libs
set DEST=%USERPROFILE%\My Drive\Documents\eBook\_calibre\libs

set cd_fix=%CD:c:=C:%
if "%cd_fix%" NEQ "%SOURCE%" (
	echo Please run this file only in %SOURCE%.
	TIMEOUT /T 5
	exit /B 3
)

echo Mirror this directory to Google Drive?
pause

rem /E :: copy subdirectories, including Empty ones.
rem /PURGE :: delete dest files/dirs that no longer exist in source.
rem /TIMFIX :: FIX file TIMes on all files, even skipped files.
rem /DCOPY:copyflag[s] :: what to COPY for directories (default is /DCOPY:DA).
rem     (copyflags : D=Data, A=Attributes, T=Timestamps, E=EAs, X=Skip alt data streams).
RoboCopy.exe  "%SOURCE%" "%DEST%" /XD .git /E /PURGE /TIMFIX /DCOPY:DAT
pause