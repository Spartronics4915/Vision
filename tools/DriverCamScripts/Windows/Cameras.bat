@echo off
if [%1]==[] (
	echo "Usage: Cameras.bat driver|front|back|up|all start|stop|check"
	exit /b
)

Camera.py %1 %2
if "%2" == "check" (
	pause
)
