# Building a Raspberry PI for FRC - using FRCVision-rPi

<!-- TOC depthFrom:2 orderedList:false -->

- [Building a Raspberry PI for FRC - using FRCVision-rPi](#building-a-raspberry-pi-for-frc---using-frcvision-rpi)
  - [Introduction](#introduction)
  - [Theory of operation](#theory-of-operation)
  - [Prepare for Competition](#prepare-for-competition)
    - [official pre-built pi image](#official-pre-built-pi-image)
    - [read-only-raspberry-pi](#read-only-raspberry-pi)
    - [disable wireless (wifi and bluetooth)](#disable-wireless-wifi-and-bluetooth)
    - [duplicate working microSD card](#duplicate-working-microsd-card)
  - [Config Details](#config-details)
    - [make sure you have a raspi 3 or 4 with picam](#make-sure-you-have-a-raspi-3-or-4-with-picam)
    - [build microSD card (minimum 8GB)](#build-microsd-card-minimum-8gb)
    - [on first boot](#on-first-boot)
    - [rename/renumber your raspi](#renamerenumber-your-raspi)
    - [install python extensions](#install-python-extensions)
    - [install node and extensions](#install-node-and-extensions)
    - [validate camera](#validate-camera)
    - [verify opencv/python and picamera](#verify-opencvpython-and-picamera)
    - [pull git repository](#pull-git-repository)
    - [optional - install support for h264 feed](#optional---install-support-for-h264-feed)
      - [install h264player](#install-h264player)
      - [install rpi-webrtc-streamer (deprecated)](#install-rpi-webrtc-streamer-deprecated)
      - [install uv4l (deprecated)](#install-uv4l-deprecated)
    - [optional - install window system](#optional---install-window-system)
    - [misc](#misc)
      - [mount usb thumbdrive](#mount-usb-thumbdrive)
      - [FRCVision-rPi services](#frcvision-rpi-services)
      - [OpenCV+python3 build details](#opencvpython3-build-details)
  - [Troubleshooting](#troubleshooting)
    - [no camera functionality](#no-camera-functionality)
    - [uv4l service is starting on reboot and we don't want it to](#uv4l-service-is-starting-on-reboot-and-we-dont-want-it-to)
    - [frcvision webpage doesn't appear at http://frcvision.local](#frcvision-webpage-doesnt-appear-at-httpfrcvisionlocal)
    - [webrtc isn't working](#webrtc-isnt-working)
    - [uv4l webpage doesn't appear](#uv4l-webpage-doesnt-appear)
    - [vision services aren't available](#vision-services-arent-available)
    - [vision services can't connect to robot](#vision-services-cant-connect-to-robot)

<!-- /TOC -->

## Introduction

The Raspberry Pi (raspi) is an inexpensive and entirely adequate processor
capable of both video capture and processing.  Outfitting a raspi to
integrate well with FRC network tables and competition requirements is
a non-trivial system-administration task and so the FRC folks have
kindly provided the community with a canned 
[raspi disk image](https://github.com/wpilibsuite/FRCVision-pi-gen/releases) 
that can be installed onto a raspi and get you running in under 20 minutes.

Among the built-in conveneniences offered by the FRCVision-rPi image:

* WPI libraries for network tables and FRC interop utilities.
* The opencv image processing library with bridges to java, c++ and python.
* A disk partitioning scheme that can be configured for read-only or
  read-write access.  During competition, the read-only mode reduces the
  chance that the disk will be corrupted by during robot start & stop.
* An easy-admin webapi that allows you to:
    * configure IP addressing (DHCP vs static IP)
    * configure team number
    * establish which camera script runs on the robot
    * configure camera ports and binding
    * toggle between read-write and read-only mode
    * to monitor the state of the raspi (cpu, network traffic, etc).
* A service architecture that ensures that your camera/vision server
  program is always running.
* Clutter-reduction:  elimination of a variety of utilities on the default
  raspi image that consume precious space or cycles including:
    * wolfram mathematica
    * x windows and associated desktop tools
* WIFI disabling: disallowed during FRC competition and disabled in
  FRCVision-rPi (this is an inconvenience at first).

## Theory of operation

Basic idea:  use the web FRCVision [dashboard](http://frcvision.local) to
control and monitor your raspi. If you change your raspi's name, this link
won't work, but you can either enter the new hostname or its static ip
address like [this](http://10.49.15.11).

If you need to configure/reset any persistent value, you must make the raspi
Read-Write.  After configuration is complete, make sure it's in Read-Only mode.
A reboot with cause filesystem to be reset to read-only mode.

Establishing the team number makes is possible for the raspi to connect to
the robot's network tables.  Robot connections are only possible if the
raspi and the robot are _on the same network_.  In other words
_in the 10.49.15.*_ address range.

Establishing a static IP address is one way to ensure that the raspi is
in the robot's address space. It's also a way for our DriverStation
dashboard to identify each raspi reliably.  The standard name,
`frcvision.local`, will __not__ work reliably when multiple raspis are
on the same network. You can also change the hostname of your raspi.
Now, a static IP would still be of potential use, but not absolutely
necessary to disambiguate multiple raspis.

You can upload your custom python "cameraService" via the web interface
via the Application tab.  This will persist across reboot and is the
preferred/suggested way of managing custom vision code.   The script,
`~/runCamera`, is used to launch your program. Each time you upload a
new vision script, `runCamera`  is automatically updated to point to
your new script.  Your script is uploaded to the file `~/uploaded.py` and
here's what runCamera looks like to make it happen:

``` bash
#!/bin/sh
### TYPE: upload-python
echo "Waiting 5 seconds..."
sleep 5
export PYTHONUNBUFFERED=1
exec ./uploaded.py

```

This form of `runCamera` requires that your python script be written to include
the [shebang](https://en.wikipedia.org/wiki/Shebang_(Unix)) to python3. In
other words, the first line of your script must be:

``` bash
#!/usr/bin/env python3
```

Here's a trivial example whose output can be view in the `Vision Status`
console when enabled.  Generally debugging output of vision scripts
should be **disabled** during competition to prevent unnecessary network
network traffic.

``` bash
#!/usr/bin/env python3
import time
while 1:
    time.sleep(5)
    print("tick");
    time.sleep(5)
    print("tock");
```

Here's a shell script (`startVision.sh`) to load a standard git-based 
Vision solution:

``` bash
#!/bin/bash
cd /home/pi/spartronics/Vision/2019
exec ./runPiCam.py --robot roborio --config greenled_dbcam8
```

Here's a shell script (`startH264player.sh`) to start the h264player:

``` bash
#!/bin/bash -f
cd /home/pi/spartronics/Vision/h264player
node appRaspi.js
```

A number of startSomething.sh scripts can be found in our repository
and it's quite simple to manually edit ~/runCamera to launch the desired
script. Here's an example with a few options commented out.

```bash
#!/bin/sh
### TYPE: upload-python
echo "Waiting 2 seconds..."
sleep 2
exec ./startVision.sh
#exec ./startH264player.sh
#export PYTHONUNBUFFERED=1
#python ./startSleeper.py
```

Note that if you _manually_ copy or create a file on the raspi for this
purpose that it must be _executable_.  You can make a file executable
via: `chmod +x yourfile`.  And verify that it is executable via
`ls -l yourfile`.  Here is a before and after:

```bash
# before
% ls -l yourfile
-rw-r--r-- 1 pi pi 17201 Feb  2 13:37 yourfile
# after
% ls -l yourfile
-rwxrwxr-x 1 pi pi 17201 Feb 2 13:37 yourfile
```

## Prepare for Competition

### official pre-built pi image

Once we've built-out _our variation_ of a standard raspberry pi (see 
[below](#on-first-boot)), we can create a disk image that should be used to 
build out new microsd cards. In order to minimize the time to duplicate the 
image, its best to work with an 8BG sdcard.  Our customizations could be made 
available in the release section of our Vision github following
[these instructions](https://stackoverflow.com/questions/47584988/how-to-upload-tar-gz-and-jar-files-as-github-assets-using-python-requests),
however there appears to be a limit on the size of such tarballs and
we have yet to complete this task.  To get around this limitation
FRC has elected to "zip" the image.  Interestingly, disk-duplication
utilities liek Etcher are able to handle .zip-ed images.

Note that any disk image will reflect a specific machine identity
([see here](#duplicate-working-microsd-card)) (ie: its static ip).  After
cloning this disk image, you'll need to boot your new raspi and reconfigure
its static ip.  The distinction between driver and vision cameras is
characterized by static ip __and__ the camera process that runs after each
reboot.  For driver camera, we use the uv4l script and for vision camera
we employ python plus `runPiCam.py`.
[This link](https://liudr.wordpress.com/2016/03/25/back-up-and-clone-raspberry-pi) 
shows how to squeeze a bigger partition onto a smaller disk (but it requires windows).
NB: the older version of the software is available from warez sites and seems
simpler than the more modern version.

### read-only-raspberry-pi

* use the FRCVision-rPi dashboard to ensure you're operating in Read-Only mode.
 You can use these commands to toggle between ro and rw:

``` bash
# make it read-only
ro
# make it read-write
rw
# ro is an alias for:
# sudo /bin/mount -o remount,ro / && sudo /bin/mount -o remount,ro /boot
# rw is an alias for:
# sudo /bin/mount -o remount,rw / && sudo /bin/mount -o remount,rw /boot
```

### disable wireless (wifi and bluetooth)

FRCVision-rPi disables both wifi and bluetooth via these contents of
    `/etc/modprobe.d/raspi-blacklist.config`.

```sh
#wifi
blacklist brcmfmac
blacklist brcmutil
#bt
blacklist btbcm
blacklist hci_uart
```

During debugging and provisioning of a raspi, you may find it useful
to enable the wifi.  If you do so, __make sure to disable it before competing__.

After commenting out the two wifi entries and rebooting verify that
the wifi is active:

```sh
% ifconfig wlan0
wlan0: flags=4099<UP,BROADCAST,MULTICAST>  mtu 1500
        ether b8:27:eb:47:2d:bd  txqueuelen 1000  (Ethernet)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 0  bytes 0 (0.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

Check which wifi networks are available:

```sh
% sudo iwlist wlan0 scan | grep ESSID
ESSID:"Tortellini"
ESSID:"WIFI"
ESSID:""
ESSID:"CenturyLink1238"
ESSID:""
ESSID:"xfinitywifi"
```

Add network password  to `/etc/wpa_supplicant/wpa_supplicant.conf`:

```txt
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="BISD-OPEN-WIFI"
    key_mgmt=NONE
    proto=RSN
    key_mgmt=WPA-PSK
    pairwise=CCMP
    auth_alg=OPEN
}
# if your network has a password replace key_mgmt with psk="YourPassword"
```

To reconfigure wifi network:

```sh
% wpa_cli -i wlan0 reconfigure
% ifconfig wlan0
```

If you have two routes to the internet you may need to look at the routes.

```sh
% ip route
default via 192.168.0.1 dev eth0 src 192.168.0.8 metric 202
default via 192.168.1.1 dev wlan0 src 192.168.1.74 metric 303
192.168.0.0/24 dev eth0 proto kernel scope link src 192.168.0.8 metric 202
192.168.1.0/24 dev wlan0 proto kernel scope link src 192.168.1.74 metric 303
```

Here, 192.168.1 and 192.168.0 are our two networks and each have a default
route.

More information on configuration wifi can be found [here](https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md).

### duplicate working microSD card

* a properly duplicated (up-to-date!) microsd is essential issurance
  for a competition.  Here's a [link](https://thepihut.com/blogs/raspberry-pi-tutorials/17789160-backing-up-and-restoring-your-raspberry-pis-sd-card)
  to a variety of methods to accomplish this task.  The larger your microsd,
  the longer this process will take.  On Linux and MacOS you can use this:

  ```sh
  sudo dd if=/dev/diskN of=~/Desktop/myRaspiImg bs=512;
  # where N is your microSD, you can findit either via:
  #  `mount` or `diskutil list`

  # to monitor its progress, you can periodically send it a signal
  # (either background the dd process or perform this in another shell)
  while true; do sudo killall -INFO dd; sleep 60; done # on linux use -USR1
  ```

Note well: if your "working disk" is much larger than your target disk, you can
reduce the time it takes to perform the duplication through the use of 
a piclone-like facility, like [this script](https://github.com/raspberrypi-ui/piclone/blob/master/src/backup), coupled with a usb-mounted target microsd card on
your master pi.

  ```bash
  backup /dev/sd01  # one parameter: target disk device /dev/sda[1-N]
  ```

  And to create a duplicate, reverse the process:

  ```sh
  # make sure the /dev/diskN is unmounted either via:
  #     `sudo diskutil unmountDisk /dev/diskN` or `sudo umount /dev/diskN`
  sudo dd if=~/Desktop/myRaspiImg of=/dev/diskN bs=512;
  ```

__Unfortunately__, this particular script wasn't able to successfully duplicate
an FRC vision system, perhaps because the number of mount points and file systems
is unusual.

## Config Details

Following are details on how to buy, provision and operate a raspi based
on the FRCVision-rPi image.  Additional customizations are offered to maximize
utility in the context of Spatronics4915. These are the steps needed to build
a raspi that can be used as a base-image. If you already have a base-image available,
use it skip these steps. In that case, remember to set the static IP and drive
script appropriate for the raspi's role on the robot.

### make sure you have a raspi 3 or 4 with picam

You can buy raspis and raspi cameras at a number of sites, here are
a few examples:

* [pi3](https://www.amazon.com/gp/product/B01CD5VC92)
* [pi4](https://www.amazon.com/gp/product/B07TD42S27)
* [camera](https://www.amazon.com/gp/product/B00FGKYHXA)
* [night-vision camera](https://www.amazon.com/dp/B06XYDCN5N)

### build microSD card (minimum 8GB)

* follow instructions [here](https://docs.wpilib.org/en/latest/docs/software/vision-processing/raspberry-pi/using-the-raspberry-pi-for-frc.html)

### on first boot

* verify that the built-in webserver is operational by pointing
  your browser to http://frcvision.local. Note that you must be
  on the same network for this to work.  Typically its best to
  plug your laptop and the pi into the same network access point
  (wifi hub/bridge). Note also that you may have problems with
  this if you have more than one raspi on the same network.
* notice the Read-Only | Writable selector at the top of the page.  If
  you need to make any changes, the disk must be writable.
* ssh into frcvision.local (user is 'pi', password is 'raspberry')
    * `sudo raspi-config`  (use Tab, Esc and Arrow keys to navigate)
        * `Localisation Options`
            * set keyboard locale (US-UTF8...)
            * time-zone (America/Los Angeles)
            * enable camera (interfaces))
            * set time manually if needed
            `sudo date --set 1998-11-02; sudo date --set 21:08:00`
        * `Interfacing Options`
            * Enable connection to Raspberry Pi Camera (pi3/2019)
            * Enable I2C (for camera switcher)
        * `Advanced`
            * Consider raising GPU memory to 256MB
    * `sudo raspi-config --expand-rootfs` - enlarge filesystem if your 
      microsd card is larger than 8GB. Before reboot, you must edit the
      file in /etc/init.d to ensure that the disk is in rw mode before
      the resize operation occurs. Here are the lines that need to
      be added:
      ```sh
      mount -o remount,rw / && 
      mount -o remount,rw /boot &&
      ```
* change user password 
    ```sh
    % passwd # respond to prompts, old was raspberry, new: teamname (spartronics)
    ```
* update and cleanup (recover diskspace)
    ```sh
    sudo apt-get update
    sudo apt-get upgrade
    sudo apt-get install python3-pip git vim tree lsof i2c-tools
    sudo apt-get clean
    sudo apt-get autoremove
    ```

See also: https://docs.wpilib.org/en/latest/docs/software/vision-processing/raspberry-pi/the-raspberry-pi-frc-console.html

### rename/renumber your raspi

You can establish DHCP addressing with a static IP fallback via the
[frcvision dashboard](http://frcvision.local).

To change your raspi name, you must log-in manually.  Note that using
the raspi-config tool is __insufficient__ for this task due to frc
conventions. Also note that this step may not be needed since we
generally prefer to rely on ip addresses (since we have multiple
raspis to manage).

```sh
# renaming your raspi may not be necessary
# first the usual step
sudo hostnamectl set-hostname drivecamfront

# next, the frc fixup:
# sudo edit /etc/hosts with nano or vi to look like this:

27.0.0.1       localhost
::1            localhost ip6-localhost ip6-loopback
ff02::1        ip6-allnodes
ff02::2        ip6-allrouters

127.0.1.1      drivecamfront

# after editing this file, reboot the machine and potentially the router
```

### install python extensions

``` bash
sudo python3 -m pip install picamera
# following may be present in frcvision, but shouldn't hurt
sudo python3 -m pip install numpy
sudo python3 -m pip install pynetworktables 
```

### install node and extensions

```bash
sudo apt-get install nodejs # version should be > 10.0
sudo apt-get install npm  # might be the wrong version (ie 5.8.0)
# to resolve npm install issue: UNABLE_TO_GET_ISSUER_CERT_LOCALLY
npm config set registry http://registry.npmjs.org/ 
sudo npm install
```

### validate camera

* `vcgencmd get_camera` should report this:

    ```sh
    supported=1 detected=1
    ```

* `raspistill -v -o test.jpg`. This will only work if you remove the picamera
  from the Connected Camera list on the Vision Settings tab. See
  [troubleshooting](#troubleshooting) if you have problems.
* (deprecated) to use picam as opencv videostream (ie: without picamera module):
 `sudo modprobe bcm2835-v4l2`

### verify opencv/python and picamera

``` python
% python3
>>> import cv2
>>> import picamera
>>> import networktables
```

### pull git repository

* `mkdir -p spartronics`
* `cd spartronics`
* `git clone https://github.com/Spartronics4915/Vision`

### optional - install support for h264 feed

The sub-$25 pi camera can operate at up to 90 fps and includes a
native H264 encoder.  This is far superior to most current usb2 webcams
and offers a number of controls not usually present in a webcam.
A raspi has two CSI connection points, but can apparently support
only a single picam connected at the point nearest the HDMI.

H264 is a very efficient video solution on raspberry pi due to
its GPU-based implementation.  The hard part is delivering
the resulting video stream to a web browser for integration with our
Dashboard.  We have explored three technologies for this and currently 
suggest that `h264player is the preferred solution`.

* `h264player` uses tcp-based websockets to deliver the
    raspivid stream to a browser. No fancy STUN negotiations
    take place, but to make the pixels visible in the browser
    we employ a javascript h264 decoder. Once the pixels
    are decoded, we rely on an opengl YUV canvas for their display.
    The more modern html5 video element and media streams aren't employed
    by this approach and so its major downside is that it consumes extra 
    load on the driver station. See [here](./h264player/README.md) for more.
* `webRTC` is the newest and shiniest of streaming techs.
    It resolved the biggest issue for broad-deployment of
    streaming through a complex routing negotiation system
    called ICE, which requires external STUN and/or TURN
    services. It was built to integrate well with web browsers
    using a native inbuilt h264 decoder.  But it failed for us
    in the context of the FRC Field Management System. Since we
    have very little time operating in that environment it is
    very difficult to diagnose and resolve the problem. Another difficulty
    we encountered related to the fragility of the disconnect/reconnect
    process.  In dual camera setup, we found it necessary to work around
    this difficulty (esp with uv4l) by keeping two streams open throughout
    the match.
* `rtsp` is an older tech for streaming that doesn't
    appear to "gel" with web browsers.  It does appear to have
    the same advantages (over webrtc) that h264player does in terms
    of traffic routing. An open source app, VLC,  has support for
    decoding and displaying an rtsp feed. On the raspi side, several
    rtsp options are available with gstreamer being the likely candidate.
    For our purposes, interacting with 3rd party app windows would
    present an awkward driverstation experience especially for multicamera
    switching based on network table events.

#### install h264player

Support for h264player is checked in to our Vision repository
[here](https://github.com/Spartronics4915/Vision/tree/master/h264player).
To install the support, you simply pull the Vision repository to your raspi
and wire it into the FRCVision application like so:

```bash
% mkdir ~/spartronics
% cd spartronics
% git clone https://github.com/Spartronics4915/Vision
% cd Vision/h264player
% cp startH264player.sh ~
```

Note that moving from one version of FRCVision to another, we may need
to update the node_modules associated with the h264player.  Here's how:

```bash
% cd ~/spartronics/Vision/h264player
% rm -rf node_modules
% npm install  # may produce version warnings which should be okay
# ./startH265player.sh  # may produce version errors, etc.  if so then:
% npm upgrade express 
# and try again (etc)
```

Here are the contents of startH264player.sh:

```bash
#!/bin/sh
echo "Starting h264player ---------------------"
cd /home/pi/spartronics/Vision/h264player
exec node appRaspi.js
```

Note that h264player requires `node` and the installation details are
found [here](#install-node-10x-and-extensions). Next, we edit `~/runCamera` 
to look like this:

```bash
#!/bin/sh
echo "runCamera waiting 2 seconds ----"
cat /proc/device-tree/model
echo "\n"
sleep 2
# source the file
. ./startH264player.sh
# Here's an python alternative, should you wish to debug restart mechanisms
# export PYTHONUNBUFFERED=1
# exec ./tickTock.py
```

Note that we'ver reduce the waiting time from 5 to 2 seconds. This was
done in order to increase the responsiveness of camera-switching triggered
by driver actions and is a consequence of the _big hammer_ approach for
clean shutdowns employed by our variant of `h264player/serverBase.js,serverRaspi.js`.
The startSleeper.py is commented out but offers a simple way to validate
the FRC application supervisor or to temporarily disable h264player.

#### install rpi-webrtc-streamer (deprecated)

We experimented with this tech and it failed us during competetions.
Please refer to file history for more details.

#### install uv4l (deprecated)

We experimented with this tech and it failed us during competetions.
Please refer to file history for more details.

### optional - install window system

Details [here](https://www.raspberrypi.org/forums/viewtopic.php?p=890408#p890408)

```bash
sudo apt-get install --no-install-recommends xserver-xorg
sudo apt-get install --no-install-recommends xinit
sudo apt-get install xfce4 xfce4-terminal
```

### misc

#### mount usb thumbdrive

* for FAT32 thumbdrives, the desktop environment can be used to
  mount and eject.  In this case, the contents are found under
  `/media/pi`. Via CLI: `sudo mount /dev/sda1 /media/usb -o umask=000`. You
  might need to `sudo mkdir /media/usb`.  It's possible that support for 
  "exfat" (large-file FAT) isn't present on the system. Install via: 
  `sudo apt-get install exfat-fuse exfat-utils`. Finally, remember that
  portable FAT doessn't have user permissions (or any security for that matter).
  Get used to all files being owned by root, etc.
* if you have a ext4 thumbdrive, you may need to manually mount it:
   `sudo mount /dev/sda1 /mnt/usbdrive`. (you might need to mkdir)
   If you don't know the device id: `lsblk`.
* remember to eject/umount the thumbdrive!

#### FRCVision-rPi services

`pi@frcvision(rw):~$ pstree`

``` text
systemd─┬─agetty
        ├─avahi-daemon───avahi-daemon
        ├─cron
        ├─dbus-daemon
        ├─dhcpcd
        ├─ntpd───{ntpd}
        ├─sshd─┬─sshd───sshd───bash
        │      └─sshd───sshd───bash───pstree
        ├─svscanboot─┬─readproctitle
        │            └─svscan─┬─supervise───multiCameraServ───3*[{multiCameraServ}]
        │                     ├─supervise───netconsoleTee
        │                     └─supervise───configServer───5*[{configServer}]
        ├─syslogd
        ├─systemd───(sd-pam)
        ├─systemd-journal
        ├─systemd-logind
        ├─systemd-udevd
        └─thd
```

Here's a subset of above with a custom python script (multiCameraServer
replaced by python3).


``` text
        ├─svscanboot─┬─readproctitle
        │            └─svscan─┬─supervise───python3
        │                     ├─supervise───netconsoleTee
        │                     └─supervise───configServer───5*[{configServer}]

```

The svscanboot process subtree is all about keeping your camera server process
running.  The default cameraServer detects the installed cameras and writes
a files to `/boot/frc.json`.  This file can be configured from the FRCVision
dashboard under `Vision Settings`. If you don't want the built-in
discoverable cameras (USB or raspicam) from being locked, you can remove
them from the list of enabled cameras.  You can also configure settings
like capture resolution, brightness and auto-exposure via this interface.
The results of your configuration activities trigger updates to /boot/frc.json
but you can also manually edit this file (using vi, of course).

Here's a list of services listing on the ports. The FRCVision dashboard
is listening on the standard http port.  Port 1740 is the network tables
service.  22 is ssh and 1181 is the mjpeg streaming port.

`netstat -n -a | grep LIST`

``` text
tcp        0      0 0.0.0.0:1740            0.0.0.0:*               LISTEN
tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN
tcp        0      0 0.0.0.0:1181            0.0.0.0:*               LISTEN
tcp6       0      0 :::22                   :::*                    LISTEN
```

#### OpenCV+python3 build details

``` text
>>> print(cv2.getBuildInformation())
General configuration for OpenCV 3.4.7 =====================================
  Version control:               v2020.1.1

  Platform:
    Timestamp:                   2019-12-31T20:55:19Z
    Host:                        Linux 4.15.0-1064-azure x86_64
    Target:                      Linux 1 arm
    CMake:                       3.13.4
    CMake generator:             Unix Makefiles
    CMake build tool:            make
    Configuration:               Release

  CPU/HW features:
    Baseline:                    VFPV3 NEON
      requested:                 DETECT
      required:                  VFPV3 NEON

  C/C++:
    Built as dynamic libs?:      YES
    C++11:                       YES
    C++ Compiler:                /__w/1/s/work/2019-12-31-FRCVision/raspbian10/bin/arm-raspbian10-linux-gnueabihf-g++  (ver 8.3.0)
    C++ flags (Release):         -isystem /__w/1/s/work/2019-12-31-FRCVision/stage3/rootfs/usr/include/arm-linux-gnueabihf  -Wno-psabi   -fsigned-char -W -Wall -Werror=return-type -Werror=non-virtual-dtor -Werror=address -Werror=sequence-point -Wformat -Werror=format-security -Wmissing-declarations -Wundef -Winit-self -Wpointer-arith -Wshadow -Wsign-promo -Wuninitialized -Winit-self -Wsuggest-override -Wno-delete-non-virtual-dtor -Wno-comment -Wimplicit-fallthrough=3 -Wno-strict-overflow -fdiagnostics-show-option -pthread -fomit-frame-pointer -ffunction-sections -fdata-sections  -mfpu=neon -fvisibility=hidden -fvisibility-inlines-hidden -O3 -DNDEBUG  -DNDEBUG
    C++ flags (Debug):           -isystem /__w/1/s/work/2019-12-31-FRCVision/stage3/rootfs/usr/include/arm-linux-gnueabihf  -Wno-psabi   -fsigned-char -W -Wall -Werror=return-type -Werror=non-virtual-dtor -Werror=address -Werror=sequence-point -Wformat -Werror=format-security -Wmissing-declarations -Wundef -Winit-self -Wpointer-arith -Wshadow -Wsign-promo -Wuninitialized -Winit-self -Wsuggest-override -Wno-delete-non-virtual-dtor -Wno-comment -Wimplicit-fallthrough=3 -Wno-strict-overflow -fdiagnostics-show-option -pthread -fomit-frame-pointer -ffunction-sections -fdata-sections  -mfpu=neon -fvisibility=hidden -fvisibility-inlines-hidden -g -Og -DDEBUG -D_DEBUG
    C Compiler:                  /__w/1/s/work/2019-12-31-FRCVision/raspbian10/bin/arm-raspbian10-linux-gnueabihf-gcc
    C flags (Release):           -isystem /__w/1/s/work/2019-12-31-FRCVision/stage3/rootfs/usr/include/arm-linux-gnueabihf  -Wno-psabi   -fsigned-char -W -Wall -Werror=return-type -Werror=non-virtual-dtor -Werror=address -Werror=sequence-point -Wformat -Werror=format-security -Wmissing-declarations -Wmissing-prototypes -Wstrict-prototypes -Wundef -Winit-self -Wpointer-arith -Wshadow -Wuninitialized -Winit-self -Wno-comment -Wimplicit-fallthrough=3 -Wno-strict-overflow -fdiagnostics-show-option -pthread -fomit-frame-pointer -ffunction-sections -fdata-sections  -mfpu=neon -fvisibility=hidden -O3 -DNDEBUG  -DNDEBUG
    C flags (Debug):             -isystem /__w/1/s/work/2019-12-31-FRCVision/stage3/rootfs/usr/include/arm-linux-gnueabihf  -Wno-psabi   -fsigned-char -W -Wall -Werror=return-type -Werror=non-virtual-dtor -Werror=address -Werror=sequence-point -Wformat -Werror=format-security -Wmissing-declarations -Wmissing-prototypes -Wstrict-prototypes -Wundef -Winit-self -Wpointer-arith -Wshadow -Wuninitialized -Winit-self -Wno-comment -Wimplicit-fallthrough=3 -Wno-strict-overflow -fdiagnostics-show-option -pthread -fomit-frame-pointer -ffunction-sections -fdata-sections  -mfpu=neon -fvisibility=hidden -g -Og -DDEBUG -D_DEBUG
    Linker flags (Release):      -Wl,-rpath -Wl,/__w/1/s/work/2019-12-31-FRCVision/stage3/rootfs/opt/vc/lib -rdynamic   -Wl,--gc-sections
    Linker flags (Debug):        -Wl,-rpath -Wl,/__w/1/s/work/2019-12-31-FRCVision/stage3/rootfs/opt/vc/lib -rdynamic   -Wl,--gc-sections
    ccache:                      NO
    Precompiled headers:         NO
    Extra dependencies:          dl m pthread rt
    3rdparty dependencies:

  OpenCV modules:
    To be built:                 calib3d core dnn features2d flann highgui imgcodecs imgproc java ml objdetect photo python3 shape stitching superres ts video videoio videostab
    Disabled:                    world
    Disabled by dependency:      -
    Unavailable:                 cudaarithm cudabgsegm cudacodec cudafeatures2d cudafilters cudaimgproc cudalegacy cudaobjdetect cudaoptflow cudastereo cudawarping cudev js python2 viz
    Applications:                perf_tests apps
    Documentation:               NO
    Non-free algorithms:         NO

  GUI:
    GTK+:                        YES (ver 3.24.5)
      GThread :                  YES (ver 2.58.3)
      GtkGlExt:                  NO

  Media I/O:
    ZLib:                        /__w/1/s/work/2019-12-31-FRCVision/stage3/rootfs/usr/lib/arm-linux-gnueabihf/libz.so (ver 1.2.11)
    JPEG:                        build-libjpeg-turbo (ver 2.0.2-62)
    WEBP:                        build (ver encoder: 0x020e)
    PNG:                         /__w/1/s/work/2019-12-31-FRCVision/stage3/rootfs/usr/lib/arm-linux-gnueabihf/libpng.so (ver 1.6.36)
    TIFF:                        build (ver 42 - 4.0.10)
    JPEG 2000:                   build (ver 1.900.1)
    HDR:                         YES
    SUNRASTER:                   YES
    PXM:                         YES

  Video I/O:
    DC1394:                      NO
    GStreamer:                   YES
      base:                      YES (ver 1.14.4)
      video:                     YES (ver 1.14.4)
      app:                       YES (ver 1.14.4)
      riff:                      YES (ver 1.14.4)
      pbutils:                   YES (ver 1.14.4)
    libv4l/libv4l2:              NO
    v4l/v4l2:                    linux/videodev2.h

  Parallel framework:            pthreads

  Trace:                         YES (with Intel ITT)

  Other third-party libraries:
    Lapack:                      YES (/__w/1/s/work/2019-12-31-FRCVision/stage3/rootfs/usr/lib/arm-linux-gnueabihf/libopenblas.so)
    Custom HAL:                  YES (carotene (ver 0.0.1))
    Protobuf:                    build (3.5.1)

  OpenCL:                        YES (no extra features)
    Include path:                /__w/1/s/work/2019-12-31-FRCVision/stage3/rootfs/usr/src/opencv-3.4.7/3rdparty/include/opencl/1.2
    Link libraries:              Dynamic load

  Python 3:
    Interpreter:                 /usr/bin/python3 (ver 3.7.3)
    Libraries:                   /__w/1/s/work/2019-12-31-FRCVision/stage3/rootfs/usr/lib/arm-linux-gnueabihf/libpython3.7m.so (ver 3.7.3)
    numpy:                       /__w/1/s/work/2019-12-31-FRCVision/stage3/rootfs/usr/include/python3.7m/numpy (ver undefined - cannot be probed because of the cross-compilation)
    install path:                lib/python3.7/dist-packages/cv2/python-3.7

  Python (for build):            /usr/bin/python3

  Java:
    ant:                         /usr/bin/ant (ver 1.10.5)
    JNI:                         /__w/1/s/work/2019-12-31-FRCVision/stage3/rootfs/usr/lib/jvm/jdk-11.0.1/include /__w/1/s/work/2019-12-31-FRCVision/stage3/rootfs/usr/lib/jvm/jdk-11.0.1/include/linux
    Java wrappers:               YES
    Java tests:                  NO

  Install to:                    /usr/local/frc
-----------------------------------------------------------------
```

## Troubleshooting

### no camera functionality

Test with `raspistill -p "0,0,640,480"`.

* did you enable the camera with `sudo raspi-config`?
* is `multiCameraServer` using it? Make sure that the camera is removed from
  the `Vision Settings`.  Save is only available if the system is `Writable`.
  If that fails to resolve the problem upload the tick-tock script above to
  fully disable multiCameraServer.
* is another program using it? uv4l? your python script?

  ```bash
    # this will show you if a uv4l process is running
    % ps -ef | fgrep uv4l

    # this will show you all the processes that are LISTENING on a port
    % netstat -an | grep LISTEN

    # this will show you which process is listening on port 8080 it
    # returns a process number (pid)
    % sudo fuser 8080/tcp

    # and this finds the program associated with a pid
    %  ps -ef | grep yourpid
  ```

* is there a problem with the video device?

    ```bash
    cd /dev
    ls -l | grep video  # look for devices owned by group video
    ```

    It should look like this:

    ```console
    crw-rw---- 1 root video    29,   0 Mar 12 20:34 fb0
    crw-rw---- 1 root video   245,   0 Mar 12 20:34 vchiq
    crw-rw---- 1 root video   249,   0 Mar 12 20:34 vcio
    crw-rw---- 1 root video   246,   0 Mar 12 20:34 vcsm
    crw-rw---- 1 root video    81,   0 Mar 12 20:34 video0
    ```

    If you see something else, try:

    ```bash
    % sudo rm /dev/video0
    % sudo reboot
    ```

### uv4l service is starting on reboot and we don't want it to

* make sure that the service is disabled (described above).
* look at the running services via:

    ```bash
    % systemctl list-units --type=service
    ```

### frcvision webpage doesn't appear at http://frcvision.local

* are there more than one raspis on the network?  Then you
    should be using static IP addresses and using the ip address
    as the URL.  Make sure only one is on the network, then
    try again.  You can configure static ip addressing via
    the Network Status page.  Here's a typical setup:

    ```bash
    #  Configure IPv4 Address
    Static
    # IPv4 Address
    10.49.15.XXX  # where XXX is in the range 10-20
    # Subnet Mask
    255.255.255.0
    # Gateway
    10.49.15.1
    # DNS Server
    8.8.8.8
    ```

* is configServer running?

    ```bash
    % ps -ef | grep configServer
    # should produce:
    root       294   288  0 Jan28 ?        00:00:00 supervise configServer
    root       299   294  0 Jan28 ?        00:29:24 /usr/local/sbin/configServer
    pi       15895 15900  0 10:46 pts/1    00:00:00 grep --color=auto configServer
    ```

* is someone listening on port 80?

    ```bash
    % netstat -an | grep :80
    # this shows that a process is listening on port 80
    tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN
    # and this shows someone connected to the port
    tcp        0      0 10.49.15.11:80          192.168.0.4:52793       ESTABLISHED
    ```

### webrtc isn't working

* is the correct server running?  Are there any indications of badness in
  the logs?
* can we `traceroute 10.49.15.5`  (ie to the driverstation)
* does stun protocol work?

    ```bash
    #start the stun-server on driverstation
    node-stun-server
    ```

    ```bash
    #contact the stun-server from the client
    node-stun-server -s 10.49.15.5 (ie driverstation)
    ```

### uv4l webpage doesn't appear

Test by pointing your browser to `http://frcvision.local:8080` (or static IP)

* is someone listening on port 8080?

   If not, try starting uv4l manually:

   ```bash
   % uv4l --driver raspicam --auto-video_nr  -- more parameters here --
   ```

    * if that fails have you installed all the correct uv4l components?
     Have you verified that the camera is working?
    * if a manual restart works, then it's an issue of getting it to
     start after every reboot.
* uv4l doesn't auto-launch after reboot

  There are two ways to auto-launch:
    1. via systemctl
    2. via `Application` tab of frcvision webapp.

  We currently recommend running it via `Application`
  to eliminate the chance of contention during boot.
  You can upload the uv4l shell script via the
  `Uploaded Python file` option even if it's not a
  python script. Consult the example above for syntax.

### vision services aren't available

Currently we recommend installing vision services through
the frcvision webapp's `Application` panel.  Your script may fail due to syntax errors or missing resources.  The
application manager will repeatedly attempt to relaunch
your script even in the error case. Best to debug the
script manually before installing it as the application.

### vision services can't connect to robot

* make sure to enter the correct team number into `Vision Settings`
* make sure robot is on the same network as raspi
* check the console output in the frcvision webapp
