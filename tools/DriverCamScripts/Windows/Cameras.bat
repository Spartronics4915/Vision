@echo off
if [%1]==[] (
	echo "Usage: Cameras.bat front|back|up|all start|stop|check"
	exit /b
)

Camera.py %1 %2
if "%2" == "check" (
	set /p ent="Enter any key"
)
