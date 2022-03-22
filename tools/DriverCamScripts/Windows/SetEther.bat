@echo off
if "%1" == "dhcp" (
	netsh interface ipv4 set address name="Ethernet" dhcp
	netsh interface ipv4 set dnsservers name="Ethernet" dhcp validate=no
) else (
	netsh interface ipv4 set address name="Ethernet" static 10.49.15.20 255.0.0.0 10.49.15.1
	netsh interface ipv4 set dns name="Ethernet" static 10.49.15.1 validate=no
)
pause
