@echo off
if [%1]==[] (
	echo "Usage: Displays.bat front|back|up|all start|stop|check|find"
	exit /b
)

Display.py %1 %2
if "%2" == "check" (
    pause
)
