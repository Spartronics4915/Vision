@echo off
if [%1]==[] (
	echo "Usage: Displays.bat driver|front|back|up|all start|stop|check|find|portrait|landscape|external"
	exit /b
)

Display.py %1 %2
if "%2" == "check" (
    pause
)
