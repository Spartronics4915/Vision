### make sure you have a raspi 3 with picam
* [https://www.amazon.com/gp/product/B01CD5VC92](pi3)
* [https://www.amazon.com/gp/product/B00FGKYHXA](camera)

### build microSD card (minimum 8GB)
* download latest debian-stretch image
* use etcher or similar to format/build the microSD card

#### on first boot (requires network)
* `sudo raspi-config`
    * enable camera
    * enable ssh
    * set timezone and keyboard
    * configure to not autologin and not start window system (faster startup)
* `sudo apt get update`
* `sudo apt get install`

#### setup network
* dynamic ip for wlan0
    * /etc/wpa_supplicant/wpa_supplicant.conf (NB: we must disable wlan for competetion)

* static ip for eth0
    * /etc/dhcpd.conf (has example static):  we want 10.49.15.10/24 for vision
    * `ifconfig`
    * when in dev mode, we may have two interfaces (eth0, wlan0), this may
      result in two default routes and result in unreachable host messages.
     `sudo route del default` 

#### build opencv with extensions
* [https://www.pyimagesearch.com/2017/09/04/raspbian-stretch-install-opencv-3-python-on-your-raspberry-pi](opencv-3 build)

#### install python extensions
* `python -m pip install pynetworktables`
* `python -m pip install pynetworktables2js`
* `python -m pip install daemon`

#### validate video
* `raspivid -p "0,0,640,480"`
* to use picam as opencv videostream (ie: without picamera module):
 `sudo modprobe bcm2835-v4l2`


#### pull git repository
* `mkdir -p src/spartronics`
* `cd src/spartronics`
* `git clone https://github.com/Spartronics4915/Vision`


#### misc
##### mount usb thumbdrive
* `sudo mkdir -p /mnt/usb`  (once)
* `sudo mount -o uid=pi,gid=pi -t vfat /dev/sda1 /mnt/usb`

### Prepare for competition

* read-only-raspberry-pi
    * (https://learn.adafruit.com/read-only-raspberry-pi)
* install init scripts

#### duplicate working microSD card

