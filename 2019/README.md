# Vision4915/solution

## applications

* `runPiCam.py` - primary entrypoint when running in competition 
  (no server currently).  To get the highest framerate, we run 
  the frame-capture in a separate thread from the algorithm.

* `picamStreamer.py` - mjpg streaming on port 5080... URL controls 
   whether we stream the results of an algorithm or direct stream.  
   http://{host}:{port}/{algo}.mjpg (or mjpeg).

  * algo: "direct" - direct/fast video streaming
  * algo: "empty" - per-frame streaming, no processing
  * algo: "hsv" - show hsv of camera view
  * algo: "mask" - show hsv of camera view
  * algo: "default" - default algo
  * algo: "realPNP" - pose estimator, this is the default for 2019
  * algo: anythingelse - the "default" algo 

## library

* `startVision.sh` - a script than launches runPiCam.py in competition mode
* `algo.py` - collection of various vision pipelines
* `picam.py` - thin vaneer atop PiCamera, support for threaded streaming
* `comm.py` - manage communication with robot via networktables
* `fakerobot` - start this script to validate target communication.
* `targets.py` - abstraction for target nettab representation
* `rectUtil.py` - utilities for captured and analysis of rectangles

## support

* we either launch picamStreamer.py manually or launch runPiCam.py
  via frcvision's uploaded.py mechanism.
