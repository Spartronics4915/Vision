
# Building a Raspberry PI for FRC

## make sure you have a raspi 3 with picam
* [https://www.amazon.com/gp/product/B01CD5VC92](pi3)
* [https://www.amazon.com/gp/product/B00FGKYHXA](camera)

## build microSD card (minimum 8GB)
* download latest debian-stretch image
* use Etcher or similar to format/build the microSD card

## on first boot (connect to wifi via desktop)
* `sudo raspi-config`
    * change user password
    * configure to not autologin and not start window system (faster startup)
    * enable ssh
    * enable camera
    * set timezone and keyboard
    * (reboot)
* update and cleanup (recover diskspace)

    ```
    sudo apt-get update
    sudo apt-get upgrade
    sudo apt-get install
    sudo apt-get purge wolfram-engine
    sudo apt-get purge libreoffice*
    sudo apt-get install python3-pip
    sudo apt-get clean
    sudo apt-get autoremove
    ```

## install python extensions

```
sudo pip3 install pynetworktables pynetworktables2js daemon
```

## build opencv with extensions

* [optimized build](https://www.pyimagesearch.com/2017/10/09/optimizing-opencv-on-the-raspberry-pi) (skip steps on virtual envs)

> Note that building opencv on pi requires lots of time and disk space.  If
> you wish to build it on a thumbdrive, it needs to be formatted to support
> symbolic links (ie: FAT32 won't work, ext4 is fine).  If you have a 16GB
> microsd you should be fine.

## setup network

* static ip for eth0
    * /etc/dhcpd.conf (has example static): we want 10.49.15.10/24 for vision
    * `ifconfig`
    * when in dev mode, we may have two interfaces (eth0, wlan0), this may
      result in two default routes and result in unreachable host messages.
     `sudo route del default`

## validate video

* `raspivid -p "0,0,640,480"`
* to use picam as opencv videostream (ie: without picamera module):
 `sudo modprobe bcm2835-v4l2`

## optional - install uv4l (for streaming video via picamera)

The sub-$25 pi camera can operate at up to 90 fps and includes a
native H264 encoder.  This is far superior to most usb2 webcams
and offers a number of controls not usually present in a webcam.
In theory a raspi can support 2 pi cameras but we haven't tested 
that.

* follow instructions for _stretch_ [here](https://www.linux-projects.org/uv4l/installation)
* note: the instructions regarding TC358743 you can ignore.
* install demos
* install webrtc
* here are the packages required (note raspidisp not required)

    ```
    uv4l                                            install
    uv4l-decoder2                                   install
    uv4l-demos                                      install
    uv4l-encoder                                    install
    uv4l-raspicam                                   install
    uv4l-raspicam-extras                            install
    uv4l-raspidisp-extras                           remove
    uv4l-renderer                                   install
    uv4l-server                                     install
    uv4l-webrtc                                     install
    ```

* edit `/etc/uv4l/uv4l-raspicam.conf`

    ```
    # -------------------
    # there are a variety of raspicam driver settings
    driver = raspicam
    auto-video_nr = yes

    # -------------------
    # there are a number of camera exposure settings that can
    # be fiddled with
    # these depend on camera mount
    hflip = yes
    vflip = yes

    # auto-exposure might get in the way?
    exposure = auto

    # -------------------
    # FRC rules contrain the range of allowed ports
    server-option = --port=5080

    # -------------------
    # WebRTC options govern h264 streaming, we wish to obtain maximum
    # quality for minimum bandwidth.
    #  bitrate is the primary quality knob
    server-option = --enable-webrtc-audio=no
    server-option = --webrtc-receive-audio=no
    server-option = --webrtc-hw-vcodec-maxbitrate=3000
    ```

* restart service `sudo systemctl restart uv4l_raspicam.service`
* point Dashboard's layout file to the IP address+port.

## pull git repository
* `mkdir -p src/spartronics`
* `cd src/spartronics`
* `git clone https://github.com/Spartronics4915/Vision`

## misc
### mount usb thumbdrive
* for FAT32 thumbdrives, the desktop environment can be used to
  mount and eject.  In this case, the contents are found under
  `/media/pi`.
* if you have a ext4 thumbdrive, you may need to manually mount it:
   `sudo mount /dev/sda1 /mnt/usbdrive`. (you might need to mkdir)
* remember to eject/umount the thumbdrive!

## Prepare for competition

### read-only-raspberry-pi
* https://learn.adafruit.com/read-only-raspberry-pi

### install init scripts
(To Do)

### disable wireless (wifi and bluetooth)
* add to /etc/modprobe.d/raspi-blacklist.config (via [stackexchange](http://raspberrypi.stackexchange.com/questions/43720/disable-wifi-wlan0-on-pi-3))

```
 *blacklist brcmfmac*
 *blacklist brcmutil*
```

### duplicate working microSD card
* a properly duplicated (up-to-date!) microsd is essential issurance
  for a competition.  Here's a [link](https://thepihut.com/blogs/raspberry-pi-tutorials/17789160-backing-up-and-restoring-your-raspberry-pis-sd-card)
  to a variety of methods to accomplish this task.  The larger your microsd,
  the longer this process will take.
