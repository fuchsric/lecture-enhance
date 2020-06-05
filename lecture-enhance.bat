@echo off
cd /D %~dp0%
:start
IF (%1) == () GOTO end
python lecture-enhance.py input "%~1" output "%~dpn1 fixed.mp4"
SHIFT
GOTO start
:end
pause
