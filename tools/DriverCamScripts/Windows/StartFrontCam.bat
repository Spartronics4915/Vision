@echo off
:: Get the IP address of the wlan0 interface (in 10.49.15.x)
for /f "usebackq tokens=*" %%a in (`py -3 c:\Users\rando\find_IP.py`) do set MYIP=%%a

:: Start the Raspberry Pi GStreamer
ssh pi@10.49.15.12 "./gstreamit.sh %MYIP% 5805 > /dev/null 2>&1 &
