### sudo raspi-config
* enable camera
* enable ssh
* set timezone and keyboard
* configure to not autologin and not start window system (faster startup)

### dynamic ip for wlan0
* /etc/wpa_supplicant/wpa_supplicant.conf

### static ip for eth0
* /etc/dhcpd.conf (has example static):  we want 10.49.15.10/24 for vision
* `ifconfig`
* when in dev mode, we may have two interfaces (eth0, wlan0), this may
  result in two default routes and result in unreachable host messages.
 `sudo route del default` 

### build opencv with extensions
* [https://www.pyimagesearch.com/2017/09/04/raspbian-stretch-install-opencv-3-python-on-your-raspberry-pi](opencv-3 build)

### mount usb thumbdrive
* `sudo mkdir -p /mnt/usb`  (once)
* `sudo mount -o uid=pi,gid=pi -t vfat /dev/sda1 /mnt/usb`

### video
* `raspivid -p "0,0,640,480"`
* to use picam as opencv videostream (ie: without picamera module):
 `sudo modprobe bcm2835-v4l2`

