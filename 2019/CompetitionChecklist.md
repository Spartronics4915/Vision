# Spartronics Cameras Checklist 2019

## Basic setup

### Dashboard 

2 windows open

#### Top screen  (driver cam)

* url: http://localhost:5080/?shownav=0#tab8
* running two streams at once
* camera selected by network table key: `/SmartDashboard/Driver/VideoStream`
    * value should be one of `Test`, `Front`, `Back`
    * ip address bindings controlled by `layout2019.json`, camera cls property
        refers to a name in index.css which controls resolution. Currently
        videostream cls is set to `size1280`.
    * `index.css` can be used to change resolution (this is the where the
      in-browser zoom is controlled).
    * for the cleanest shutdown, reset the VideoStream value to "_cleanup_" at 
      the end of a match.
* Best practice:  make sure both feeds are running before the match begins.
   As long as there are no networking hiccups during the match you should 
   have stable feeds for the duration.

#### Bottom screen (standard dashboard)

* url: http://localhost:5080  
* this is where auto mode is selected and can be used to manually
  establish the videostream selection.  We expect the driving
  direction control on the joystick to be tied to the VideoStream network
  table key. When driver changes driving direction, the VideoStream should 
  automatically change.

### Driver Cameras

There is a link in the dashboard to two different web servers running on
each raspbery pi (on the gears page).  So there are 4 different links for
driver cameras (plus one for the vision camera).

* Pi status is the frc control panel and can be used to monitor bandwidth
  consumption and verify basic connectivity, etc. It can also be used to
  change the static IP address associated with a Pi. Doing so will require
  a reconnect.  If you have two raspberry pi's on the same network with the
  same ip address, you could end up in trouble, so tread very carefully.
* UV4L is the service that produces h264 video streams.  UV4L status offers
  camera configuration overrides (to flip cameras, etc) but we usually prefer

The way that uv4l is started is controlled via frc control panel.  Here
is the contents of the script that we use.

```
uv4l -f \
 --driver raspicam \
 --auto-video_nr \
 --vflip=yes \
 --hflip=yes \
 --enable-server \
 --server-option '--enable-webrtc-audio=0' \
 --server-option '--webrtc-receive-audio=0' \
 --server-option '--webrtc-preferred-vcodec=3' \
 --server-option '--webrtc-hw-vcodec-maxbitrate=1500' \
 --server-option '--webrtc-enable-hw-codec'
```

If you modify this script be __absolutely certain__ that there are __no__
characters after the backslash on the end of most lines. Once modified, the
script can be re-uploaded via the frc control panel.  If you prefer
to `ssh` into the machine, note that the script `runCamera` is used
to launch the script `uploaded.py` and that the latter must be executable.
Also note that the the disk must be in Read-Write mode to make this change.

## Known issues and remedies

* refreshing a web-browser page while a video feed is running may cause
  problems.  So might closing the page.  The issue is that the feed 
  hasn't been properly shutdown and since only a single feed is available 
  at a time, this condition renders the pi useless for many minutes. This 
  condition can be identified by inspecting the bandwidth usage via the 
  frc control panel.  If bandwidth is high, the video stream is still "open".
  Even if the bandwidth isn't high, connection refusals are likely to be 
  caused by this condition. Using the restart button on the pi's control 
  panel is __not__ the best choice to fix the problem, since the open 
  stream can take many minutes to timeout.  The fastest remedy to this 
  problem is to remove power from the pi, then re-power it. The total 
  boot cycle is less than one minute. At the same time, it's likely to 
  be a good idea to restart Chrome as the timeouts can be on the "client side".

* video feeds behave better with chrome. Firefox appears flaky for h264 feeds.
  Also: make sure you have the latest chrome installed.

* if we burn out a microsd card we need to have backups on hand.  Remember
  that the each backup has an IP address and it may match the requirements
  for the pi that failed.  You'll need to carefully make the mods to 
  the IP, etc to ensure that the right camera has the right ip address.
  Remember that two raspis on the same network with the same IP address
  is a recipe for trouble.  As of this writing here are the standard IP 
  addresses:

    ```txt
    Vision:  10.49.15.10
    Back:    10.49.15.11
    Front:   10.49.15.12
    ```

  Also make sure that the uv4l service isn't running:  `sudo systemctl disable
  uv4l_raspicam`. And perhaps remove all video devices before rebooting: 
  `sudo rm /dev/video*` (only works if the drive is read-write).

## Vision Camera

### Tuning Processes and Benchmarks

* For each competition lighting enviroment, the camera needs to have certain 
  values modified in order to provide more accurate targets for that enviroment. 
  Tuning is seperated into two relems: HSV, and Camera configs

#### HSV

  * In opencv, the main way rectangles are identified from a frame lies in a HSV range.
    The range is built as an upper, and a lower array, and in principal says:
        "Every Pixel that has an HSV color NOT within this range, throw it out"
    This part of the tuning process is primarily responsible for the proper identification of green color

  * Which values should be changed under what conditions?
    * H
      * Stands for 'Hue'. On the HSV cake, this is arguably the most important value, 
        as it identifies the range of colors that we will initally begin to look at
      * Typically, the Hue value should not be changed much. Widening the Hue value starts to subtract
        from the main purpose of having a green LED ring vs a red one.
      * From the wikipedia article:
          * "...starting at the red primary at 0°, passing through the green primary at 120° and the 
          blue primary at 240°, and then wrapping back to red at 360"

    * S and V
      * S stands for 'Saturation', V for 'value'. Saturation and Value are harder to identify as humans, as these
        are values that are not uses in conventional representation of colors. Oversimplified, 
        saturation represents how much 'white' is added to the pure color. Typically, S and V are oppisates, where one
        value will be non 0, and the other value will be 0, because they represent oppisate shades.
      * The tuning for S and V will typically come about from very oversaturated frames, which will only happen if the camera settings are     confgured improperly. A majority of the time these values will not be touched at all, but it is important to understand
        their use.
      
  





