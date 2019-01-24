# 2019 FRC Vision Challenge

<!-- TOC -->

- [2019 FRC Vision Challenge](#2019-frc-vision-challenge)
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
        - [how to setup/install uv4l](#how-to-setupinstall-uv4l)
        - [how to setup/install custom vision scripts](#how-to-setupinstall-custom-vision-scripts)
        - [FAQ](#faq)
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
  1. something else?

- _required software + hardware_
  1. raspis?
  1. leds?
  1. power requirements? 
  1. python? opencv? opencv modules?

- _choose techniques_
  1. distance:  area vs height
  1. color-range + LED/infrared
  1. angle of target markers to disambiguate adjacent targets?

- _specify protocols_
  1. driver-control of camera view
  1. driver-control over vision target and LEDs

## Open questions

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

- can we do vision on the driver station?

## Delivery schedule

### Week 3

### Week 4

### Week 5

### Week 6

## Configuring

### how to setup/install uv4l

- choice of framerate, codec, bitrate, port, etc.

### how to setup/install custom vision scripts

- recipe for uploading scripts from where, which port
  are services operating on, how to test/validate networktables.
  
### FAQ

- can we run vision on the same raspi as driver-video?
  - plumbing issues?  (two consumers, one camera)
  - two cameras?
  - disagreement on camera positioning?

- can the lines on the field be used to assist?

## The field elements

### On Field Retro-Reflective Tape

- sizes and position of targets, area?

### On Ground Gaffers Tape

- length, positioning, 
- _how close to target before we can acquire line?_
- _what sensors would we need?_

## Resources

- [Jaci's vision video](https://youtu.be/d9WSAfzA6fc)
  - [discussion of latency & gyro](https://youtu.be/d9WSAfzA6fc?t=2835)
- [ChickenVision](https://github.com/team3997/ChickenVision/blob/master/ChickenVision.py)
- [Raspi Build Notes](../BuildRaspi.md)
- [picamera docs](https://picamera.readthedocs.io)
- [opencv docs](https://docs.opencv.org/3.4.5)
