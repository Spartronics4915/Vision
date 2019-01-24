# Building a Raspberry PI for FRC - using FRCVision-rPi

<!-- TOC -->

- [Building a Raspberry PI for FRC - using FRCVision-rPi](#building-a-raspberry-pi-for-frc---using-frcvision-rpi)
    - [Introduction](#introduction)
    - [Theory of operation](#theory-of-operation)
    - [Prepare for Competition](#prepare-for-competition)
        - [read-only-raspberry-pi](#read-only-raspberry-pi)
        - [disable wireless (wifi and bluetooth)](#disable-wireless-wifi-and-bluetooth)
        - [duplicate working microSD card](#duplicate-working-microsd-card)
    - [Config Details](#config-details)
        - [make sure you have a raspi 3 with picam](#make-sure-you-have-a-raspi-3-with-picam)
        - [build microSD card (minimum 8GB)](#build-microsd-card-minimum-8gb)
        - [on first boot](#on-first-boot)
        - [install python extensions](#install-python-extensions)
        - [validate video](#validate-video)
        - [verify opencv/python and picamera](#verify-opencvpython-and-picamera)
        - [optional - install uv4l (for streaming video via picamera)](#optional---install-uv4l-for-streaming-video-via-picamera)
        - [pull git repository](#pull-git-repository)
        - [misc](#misc)
            - [mount usb thumbdrive](#mount-usb-thumbdrive)
            - [FRCVision-rPi services](#frcvision-rpi-services)
            - [OpenCV+python3 build details](#opencvpython3-build-details)

<!-- /TOC -->

## Introduction

The Raspberry Pi (raspi) is an inexpensive and entirely adequate processor
capable of both video capture and processing.  Outfitting a raspi to
integrate well with FRC network tables and competition requirements is
a non-trivial system-administration task and so the FRC folks have
kindly provided the community with a canned raspi _image_ that can be
installed onto a raspi and get you running in under 20 minutes.

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
* WIFI disabling:  disallowed during FRC competition and disabled in
  FRCVision-rPi (this is an inconvenience at first).

## Theory of operation

Basic idea:  use the web FRCVision dashboard to control and monitor your raspi.

If you need to configure/reset any persistent value, you must make the raspi
Read-Write.  After configuration is complete, make sure it's in Read-Only mode.
A reboot with cause filesystem to be reset to read-only mode.

Establishing the team number makes is possible for the raspi to connect to
the robot's network tables.  Robot connections are only possible if the
raspi and the robot are _on the same network_.  In other words
_in the 10.49.15.*_ address range.

Establishing a static IP address is one way to ensure that the raspi is
in the robot's address space. It's also a way for our DriverStation
dashboard to identify each raspi reliably.  The standard name, `frcvision.local`,
will not work reliably when multiple raspis are on the same network.

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

## Prepare for Competition

### read-only-raspberry-pi

* use the FRCVision-rPi dashboard to ensure you're operating in Read-Only mode.

### disable wireless (wifi and bluetooth)

* following isn't necessary for FRCVision-rPi but left here for reference.
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
  

## Config Details

Following are details on how to buy, provision and operate a raspi based
on the FRCVision-rPi image.  Additional customizations are offered to maximize
utility in the context of Spatronics4915.

### make sure you have a raspi 3 with picam

You can buy raspis and raspi cameras at a number of sites, here are
a few examples:

* [pi3](https://www.amazon.com/gp/product/B01CD5VC92)
* [camera](https://www.amazon.com/gp/product/B00FGKYHXA)
* [night-vision camera](https://www.amazon.com/dp/B06XYDCN5N)

### build microSD card (minimum 8GB)

* follow instructions [here](https://wpilib.screenstepslive.com/s/currentCS/m/85074/l/1027241-using-the-raspberry-pi-for-frc)

### on first boot

* verify that the built-in webserver is operational by pointing
  your browser to http://frcvision.local. Note that you must be
  on the same network for this to work.  Typically its best to
  plug your laptop into a network access point (wifi hub/bridge).
* notice the Read-Only | Writable selector at the top of the page.  If 
  you need to make any changes, the disk must be writable.
* ssh into frcvision.local (user is 'pi', password is 'raspberry')
    * `sudo raspi-config`  (use Tab, Esc and Arrow keys to navigate)
        * `Localisation Options`
            * set keyboard locale (US-UTF8...)
            * time-zone (America/Los Angeles)
            * enable camera (interfaces))
        * `Interfacing Options`
            * Enable connection to Raspberry Pi Camera
        * `Advanced`
            * Consider raising GPU memory to 256MB
* update and cleanup (recover diskspace)

    ```
    sudo apt-get update
    sudo apt-get upgrade
    sudo apt-get install
    sudo apt-get install python3-pip git
    sudo apt-get clean 
    sudo apt-get autoremove
    ```
* consider updating firmware (this may be prohibited by file permissions)

See also: https://wpilib.screenstepslive.com/s/currentCS/m/85074/l/1027798-the-raspberry-pi-frc-console

### install python extensions

```
sudo python3 -m pip install picamera python-daemon
```

(python-daemon may not be needed (tbd))

### validate video

* `raspivid -p "0,0,640,480"` (will only work if you remove the picamera
  from the Connected Camera list on the Vision Settings tab
* (deprecated) to use picam as opencv videostream (ie: without picamera module):
 `sudo modprobe bcm2835-v4l2`

### verify opencv/python and picamera

`% python3`

```
import cv2
import picamera
import daemon
```

### optional - install uv4l (for streaming video via picamera)

The sub-$25 pi camera can operate at up to 90 fps and includes a
native H264 encoder.  This is far superior to most usb2 webcams
and offers a number of controls not usually present in a webcam.
In theory a raspi can support 2 pi cameras but we haven't tested 
that.

* follow instructions for _stretch_ [here](https://www.linux-projects.org/uv4l/installation)
    * note: the instructions regarding TC358743 you can ignore.

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

### pull git repository
* `mkdir -p src/spartronics`
* `cd src/spartronics`
* `git clone https://github.com/Spartronics4915/Vision`

### misc

#### mount usb thumbdrive

* for FAT32 thumbdrives, the desktop environment can be used to
  mount and eject.  In this case, the contents are found under
  `/media/pi`.
* if you have a ext4 thumbdrive, you may need to manually mount it:
   `sudo mount /dev/sda1 /mnt/usbdrive`. (you might need to mkdir)
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

General configuration for OpenCV 3.4.4 =====================================
  Version control:               08163c0

  Platform:
    Timestamp:                   2019-01-14T05:26:19Z
    Host:                        Linux 4.15.0-1035-azure x86_64
    Target:                      Linux 1 arm
    CMake:                       3.7.2
    CMake generator:             Unix Makefiles
    CMake build tool:            make
    Configuration:               RelWithDebugInfo

  CPU/HW features:
    Baseline:                    VFPV3 NEON
      requested:                 DETECT
      required:                  VFPV3 NEON

  C/C++:
    Built as dynamic libs?:      YES
    C++11:                       YES
    C++ Compiler:                /__w/1/s/deps/02-extract/raspbian9/bin/arm-raspbian9-linux-gnueabihf-g++  (ver 6.3.0)
    C++ flags (Release):         -Wno-psabi   -fsigned-char -W -Wall -Werror=return-type -Werror=non-virtual-dtor -Werror=address -Werror=sequence-point -Wformat -Werror=format-security -Wmissing-declarations -Wundef -Winit-self -Wpointer-arith -Wshadow -Wsign-promo -Wuninitialized -Winit-self -Wsuggest-override -Wno-narrowing -Wno-delete-non-virtual-dtor -Wno-comment -fdiagnostics-show-option -pthread -fomit-frame-pointer -ffunction-sections -fdata-sections  -mfp16-format=ieee -fvisibility=hidden -fvisibility-inlines-hidden -O3 -DNDEBUG  -DNDEBUG
    C++ flags (Debug):           -Wno-psabi   -fsigned-char -W -Wall -Werror=return-type -Werror=non-virtual-dtor -Werror=address -Werror=sequence-point -Wformat -Werror=format-security -Wmissing-declarations -Wundef -Winit-self -Wpointer-arith -Wshadow -Wsign-promo -Wuninitialized -Winit-self -Wsuggest-override -Wno-narrowing -Wno-delete-non-virtual-dtor -Wno-comment -fdiagnostics-show-option -pthread -fomit-frame-pointer -ffunction-sections -fdata-sections  -mfp16-format=ieee -fvisibility=hidden -fvisibility-inlines-hidden -g -Og -DDEBUG -D_DEBUG
    C Compiler:                  /__w/1/s/deps/02-extract/raspbian9/bin/arm-raspbian9-linux-gnueabihf-gcc
    C flags (Release):           -Wno-psabi   -fsigned-char -W -Wall -Werror=return-type -Werror=non-virtual-dtor -Werror=address -Werror=sequence-point -Wformat -Werror=format-security -Wmissing-declarations -Wmissing-prototypes -Wstrict-prototypes -Wundef -Winit-self -Wpointer-arith -Wshadow -Wuninitialized -Winit-self -Wno-narrowing -Wno-comment -fdiagnostics-show-option -pthread -fomit-frame-pointer -ffunction-sections -fdata-sections  -mfp16-format=ieee -fvisibility=hidden -O3 -DNDEBUG  -DNDEBUG
    C flags (Debug):             -Wno-psabi   -fsigned-char -W -Wall -Werror=return-type -Werror=non-virtual-dtor -Werror=address -Werror=sequence-point -Wformat -Werror=format-security -Wmissing-declarations -Wmissing-prototypes -Wstrict-prototypes -Wundef -Winit-self -Wpointer-arith -Wshadow -Wuninitialized -Winit-self -Wno-narrowing -Wno-comment -fdiagnostics-show-option -pthread -fomit-frame-pointer -ffunction-sections -fdata-sections  -mfp16-format=ieee -fvisibility=hidden -g -Og -DDEBUG -D_DEBUG
    Linker flags (Release):      -rdynamic
    Linker flags (Debug):        -rdynamic
    ccache:                      NO
    Precompiled headers:         NO
    Extra dependencies:          dl m pthread rt
    3rdparty dependencies:

  OpenCV modules:
    To be built:                 calib3d core features2d flann highgui imgcodecs imgproc java java_bindings_generator ml objdetect photo python3 python_bindings_generator shape stitching superres ts video videoio videostab
    Disabled:                    world
    Disabled by dependency:      -
    Unavailable:                 cudaarithm cudabgsegm cudacodec cudafeatures2d cudafilters cudaimgproc cudalegacy cudaobjdetect cudaoptflow cudastereo cudawarping cudev dnn js python2 viz
    Applications:                perf_tests apps
    Documentation:               NO
    Non-free algorithms:         NO

  GUI:
    GTK+:                        NO

  Media I/O:
    ZLib:                        build (ver 1.2.11)
    JPEG:                        build-libjpeg-turbo (ver 1.5.3-62)
    PNG:                         build (ver 1.6.35)
    HDR:                         YES
    SUNRASTER:                   YES
    PXM:                         YES

  Video I/O:
    libv4l/libv4l2:              NO
    v4l/v4l2:                    linux/videodev2.h

  Parallel framework:            pthreads

  Trace:                         YES (built-in)

  Other third-party libraries:
    Custom HAL:                  YES (carotene (ver 0.0.1))

  Python 3:
    Interpreter:                 /usr/bin/python3 (ver 3.5.3)
    Libraries:
    numpy:                       /__w/1/s/deps/02-extract/raspbian9/arm-raspbian9-linux-gnueabihf/usr/include/python3.5m/numpy (ver undefined - cannot be probed because of the cross-compilation)
    packages path:               lib/python3.5/dist-packages

  Python (for build):            /usr/bin/python3

  Java:
    ant:                         /usr/bin/ant (ver 1.9.9)
    JNI:                         /__w/1/s/deps/02-extract/jdk/include /__w/1/s/deps/02-extract/jdk/include/linux
    Java wrappers:               YES
    Java tests:                  NO

  Install to:                    /__w/1/s/deps/03-build/opencv-build/install
```