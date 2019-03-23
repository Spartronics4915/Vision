# Spartronics Cameras Checklist 2019

## Basic setup

### Dashboard

2 windows open, upper screen holds driver camera view.

#### Top screen  (driver cam)

* url: http://localhost:5080/index.html?shownav=0#tab8
* running two streams at once
* camera selected by network table key: `/SmartDashboard/Driver/VideoStream`
    * value should be one of `Test`, `Front`, `Back`
    * ip address bindings controlled by `layout2019.json`, camera cls property
        refers to a name in index.css which controls resolution. Currently
        videostream cls is set to `size1280`.
    * `index.css` can be used to change resolution (this is the where the
      in-browser zoom is controlled).
* Best practice:  make sure both feeds are running before the match begins.
   As long as there are no networking hiccups during the match you should
   have stable feeds for the duration.

#### Bottom screen (standard dashboard)

* url: http://localhost:5080/index.html
* this is where auto mode is selected and can be used to manually
  establish the videostream selection.  We expect the driving
  direction control on the joystick to be tied to the VideoStream network
  table key. When driver changes driving direction, the VideoStream should
  automatically change.

### Driver Cameras

There is a link in the dashboard to three different web servers running
on each raspbery pi (Camera Links on the gears page).  

* Pi status is the frc control panel and can be used to monitor bandwidth
  consumption and verify basic connectivity, etc. It can also be used to
  change the static IP address associated with a Pi. Doing so will require
  a reconnect.  If you have two raspberry pi's on the same network with the
  same ip address, you could end up in trouble, so tread very carefully.

## Known issues and remedies

* drivercams may show black if their window wasn't when the connection
 is initiated.  For single screen setups, the workaround is to have
 two windows in a split layout on the screen.

* video feeds behave better with chrome. Firefox appears flaky for h264 feeds.
  Also: make sure you have the latest chrome installed.

* refreshing a web-browser page while a video feed is a "big hammer"
  that results in the server killing the video feed process. The FRC
  supervisor will relaunch the h264player service via ~/runCamera.
  There is a default sleep of 4 seconds prior to the respawn, but 
  we suggest that this be set to 2 seconds.

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

<<<<<<< HEAD
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
      
  


=======
* depending on the robot mounting of the cameras you may need to flip the
  video feed. This is done via the Dashboard's layout file
  (www/layouts/layout2019.json).
>>>>>>> 03a16273111fb42ce044aa1b2ec7f31d11b0d820

    ```json
    "driverbackcamcmd": "raspivid -t 0 -b 1500000 -o - -w 640 -h 480 -fps 30 -pf baseline -vf -hf",
    "driverfrontcamcmd": "raspivid -t 0 -b 1500000 -o - -w 640 -h 480 -fps 30 -pf baseline -vf -hf"
    ```

  It is also advised to _tune_ the bitrate.  This choiced of 1.5Mb may make
  sense for a `multistream` configuration but could be raised if multistream is
  false.  Values up to 3500000 should be explored.

* if the default value for `multistream` (in layout file) is
  unwieldy/distracting for drivers, it can be set to true for faster switching
  on the backup driver station, the feeds were exceptionally dirty and
  adding more load (decoding two streams at once) is thought to be a __bad idea__. Again, if multistream is true, be sure to select apportion your
  bitrate as discussed above.
