# 2019 FRC Vision Challenge

<!-- TOC depthFrom:2 -->

- [Deliverables](#deliverables)
    - [A fast video feed for drivers](#a-fast-video-feed-for-drivers)
    - [Vision analysis for automatic driver assist](#vision-analysis-for-automatic-driver-assist)
- [Open questions](#open-questions)
- [Delivery schedule](#delivery-schedule)
    - [Week 3](#week-3)
    - [Week 4](#week-4)
    - [Week 5](#week-5)
    - [Week 6](#week-6)
- [Configuring](#configuring)
- [The field elements](#the-field-elements)
    - [On Field Retro-Reflective Tape](#on-field-retro-reflective-tape)
    - [On Ground Gaffers Tape](#on-ground-gaffers-tape)
- [Resources](#resources)

<!-- /TOC -->

## Deliverables

### A fast video feed for drivers

- _how many?_
- _what is fast?_
- _required software + hardware_
- _where to mount for optimum driver experience?_

### Vision analysis for automatic driver assist

- _choose one or more deliverables_
  1. target relative heading (yaw)
  1. target x,y (in _field_ or _robot_ coordinates?)
  1. target x,y + perpendicular
  1. target/track floor lines?
  1. something else?

- _required software + hardware_
  1. raspis? camera?
  1. leds? infrared?
  1. power requirements?
  1. python, opencv, opencv modules?

- _choose techniques_
  1. distance:  area vs height
  1. color-range + LED/infrared
  1. angle of target markers to disambiguate adjacent targets?

- _specify protocols_
  1. driver-control of camera view
  1. driver-control over vision target and LEDs

## Open questions

The answers to some of these questions will allow us to fill in sections
above.

- how many cameras, how many raspis?  
  - 4? (front+back,vision+driver)
  - 2? (shared vision)
  - _conflict between vision and driver requirements?_
  - _is a dual-cam raspi viable?_

- what vision lighting solution? (overlaps with how many cameras)
  - LEDs?
  - infra-red

- if distance detection is required, how will we compute it? How
  will the chosen technique constrain camera positioning?
  - target against a known height
  - target area against a known area
  - other range sensor?

- how best to manage vision latency?
  - convert to robot-relative coordinates at start of path?
  - work in continuous robot-relative coordinates?
  - broadcast IMU heading from robot to vision?

- how will the targeting data be used by robot code?
  - can we operate in robot-relative mode?
  - use path planner?  
  - lower-level access to spline and motion-profiles?
  - custom wanted-states with limelight-like control?
  - custom gyro-based pid-loop to rapidly acquire heading?

- how does operator specify target? enter targeting mode?

- can we do vision on the driver station? What are the tradeoffs
  with this option?

- should we worry about field lines/gaffer tape? What is their
  relative priority and return on investment?

## Delivery schedule

### Week 3
 - Work on geometry math
 - End of week three:
    - Spend time working through required trig math to calculate perpindicular bisector
    - Given data(rectangle points) input, have full trig operations completed with correct outputs

### Week 4
 - Receive light test system from Riyadth
 - Spend time working on rectangle extraction from frame input
 - End of week four:
    - Isolate  a rectangle from a frame input
    - Deliver theta, dx, and dy of the perpindicular point between the two rectangles over networktables

### Week 5
  - Test 3d printed / plastic mount of raspicam on test chassis 
  - End of week five:
    - Be able to drive to perpindicular bisector point on test chassis
    - Get robot at end of week 5

### Week 6 (Length of 1.5 weeks)
  - In event of dead time (highly likely):
    - Spend time analyzing other team's code
    - Documentation
  - Integration with final robot chassis
  - Plug in correct offset values for final camera placement
  - End of week six:
    - Be able to drive to perpindicular bisector between targets on main chassis

## Configuring

- [Raspi Build Notes](../BuildRaspi.md)
- how to setup/install uv4l
  - choice of framerate, codec, bitrate, port, etc.
- how to setup/install custom vision scripts
  - recipe for uploading scripts from where, which port
    are services operating on, how to test/validate networktables.
  
## The field elements

[2019VisionImages.zip](https://github.com/wpilibsuite/allwpilib/releases/download/v2019.1.1/2019VisionImages.zip)

### On Field Retro-Reflective Tape

- sizes and position of targets, area?

### On Ground Gaffers Tape

- length, positioning, 
- _how close to target before we can acquire line?_
- _what sensors would we need?_

## Resources

- [DeepSpace Vision Target Video](https://www.youtube.com/watch?v=BSihm6xzbWA)
- [Jaci's vision video](https://youtu.be/d9WSAfzA6fc)
  - [discussion of latency & gyro](https://youtu.be/d9WSAfzA6fc?t=2835)
- [ChickenVision](https://github.com/team3997/ChickenVision/blob/master/ChickenVision.py)
- [picamera docs](https://picamera.readthedocs.io)
- [opencv docs](https://docs.opencv.org/3.4.5)
- [frc distance to known object](https://wpilib.screenstepslive.com/s/currentCS/m/vision/l/682952-2017-vision-examples)
  - does this work for off-axis views? Consider: known height of object/shape
    doesn't suffer as much from off-axis since robot is stuck on the ground.
  ``` java
    distance = targetHeight * YRes / (2*PixelHeight*tan(viewAngle of camera))
  ```
- [pyimagesearch distance to known object](https://www.pyimagesearch.com/2015/01/19/find-distance-camera-objectmarker-using-python-opencv/)
  - some formulations use arctan... how does this one avoid that?
- [camera calibration](https://hackaday.io/project/12384-autofan-automated-control-of-air-flow/log/41862-correcting-for-lens-distortions)
