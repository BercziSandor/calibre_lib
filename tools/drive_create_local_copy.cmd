@echo off
cd %~dp0

set SOURCE=%USERPROFILE%\My Drive\Documents\eBook\_calibre\libs
set DEST=%USERPROFILE%\Documents\Calibre\libs

set cd_fix=%CD:c:=C:%
if "%cd_fix%" NEQ "%SOURCE%" (
	echo Please run this file only in %SOURCE%.
	echo You are in %cd_fix%.
	TIMEOUT /T 5
	exit /B 3
)

if exist %DEST% (
	echo %DEST% already exist.
	TIMEOUT /T 5
	exit /B 3

)

echo Mirror this directory to a local copy?
pause

rem /E :: copy subdirectories, including Empty ones.
rem /PURGE :: delete dest files/dirs that no longer exist in source.
rem /TIMFIX :: FIX file TIMes on all files, even skipped files.
rem /DCOPY:copyflag[s] :: what to COPY for directories (default is /DCOPY:DA).
rem     (copyflags : D=Data, A=Attributes, T=Timestamps, E=EAs, X=Skip alt data streams).
RoboCopy.exe  "%SOURCE%" "%DEST%" /E /PURGE /TIMFIX /DCOPY:DAT

cd %DEST%

git init

echo Git add...
git add .

echo Git commit...
git commit -am"Init"

pause