@echo off
if "%1" == "dhcp" (
	netsh interface ipv4 set address name="Wi-Fi" dhcp
	netsh interface ipv4 set dnsservers name="Wi-Fi" dhcp validate=no
) else (
	netsh interface ipv4 set address name="Wi-Fi" static 10.49.15.20 255.0.0.0 10.49.15.1
	netsh interface ipv4 set dns name="Wi-Fi" static 10.49.15.1 validate=no
)
pause
