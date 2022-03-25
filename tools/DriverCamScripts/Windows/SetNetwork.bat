@echo off
set /p INTERFACE="Interface name:"
set /p IPADDR="IP address or dhcp:"
if "%IPADDR%" == "dhcp" (
	netsh interface ipv4 set address name="%INTERFACE%" dhcp
) else (
	netsh interface ipv4 set address name="%INTERFACE%" static %IPADDR% 255.0.0.0 10.49.15.1
)
pause
