#!/usr/bin/env python
#
# minimal test for picamera

import cv2
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera

import comm

import time
import sys
import argparse

windowName = "picamera"

def parse_args():
    """
    Parse input arguments
    """
    parser = argparse.ArgumentParser(description=
                         "Capture and display live camera video on raspi")
    parser.add_argument("--width", dest="image_width",
                        help="image width [320]",
                        default=320, type=int)
    parser.add_argument("--height", dest="iheight",
                        help="image width [240]",
                        default=240, type=int)
    parser.add_argument("--fps", dest="fps",
                        help="FPS",
                        default=60, type=int)
    parser.add_argument("--display", dest="display",
                        default=0, type=int)
    parser.add_argument("--robot", dest="robot",
                        help="robot (off, localhost, roborio)",
                        default="localhost")
    parser.add_argument("--brightness", dest="brightness",
                        help="brightness: [0, 100]",
                        default=50, type=int)
    parser.add_argument("--exposure", dest="exposure",
                        help="exposure: [5, 20000]",
                        default=10, type=int)
    parser.add_argument("--contrast", dest="contrast",
                        help="contrast: [-100, 100]",
                        default=0, type=int)
    parser.add_argument("--color", dest="color",
                        help="color: ([0,255],[0,255])",
                        default=None)

    args = parser.parse_args()
    return args

def processFrame(image, display):
    if display:
        cv2.imshow("Frame", image)

def readCam(commChan, width, height, fps, exposure):
    with PiCamera(resolution=(width,height),
                      framerate=fps,
                      sensor_mode=7  # for fastest frame rates, 0 is auto
                      ) as camera:


        rawCapture = PiRGBArray(camera, size=(width, height))
        time.sleep(0.1) # allow the camera to warmup

        camera.awb_mode = "off"
        camera.awb_gains = (1.2, 1.6) # (red, blue) balance

        # disable auto gain controls - fixes values for
        # for digital-gain and analog_gain. These values can't
        # be set directly, rather "let them settle"...
        camera.exposure_mode = "off"
        camera.exposure_compensation = -25 # [-25, 25]
        camera.shutter_speed = 10000 # set to 0 to go auto
        camera.contrast = 80  # [-100, 100]

        print("camera settings:")
        print("  analog_gain:%s" % camera.analog_gain)
        print("  digital_gain:%s" % camera.digital_gain)
        print("  awb_mode:%s" % camera.awb_mode)
        print("  awb_gains:(%g, %g)" % camera.awb_gains)
        print("  brightness:%d" % camera.brightness)
        print("  contrast:%d"  % camera.contrast)
        print("  saturation:%d" % camera.saturation)
        print("  drc_strength:%s" % camera.drc_strength)
        print("  exposure_compensation:%d" % camera.exposure_compensation)
        print("  exposure_mode:%s" % camera.exposure_mode)
        print("  exposure_speed:%d us" % camera.exposure_speed)
        print("  shutter_speed:%d us" % camera.shutter_speed)
        print("  framerate:%s" % camera.framerate)

        target = comm.Target()

        for frame in camera.capture_continuous(rawCapture, format="bgr", 
                                            use_video_port=True):
            image = frame.array
            if commChan:
                target.clock = time.clock()
                commChan.SetTarget(target)

            rawCapture.truncate() # clear the stream for the next frame
            rawCapture.seek(0) 

            processFrame(image, args.display)

            if args.display:
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q") or key == 27:
                    break
                elif key == 255:
                    pass
                elif key == 22:
                   print("22 --");
                else:
                    print(key)

if __name__ == "__main__":
    args = parse_args()
    print("Called with args:")
    print(args)
    print("OpenCV version: {}".format(cv2.__version__))

    if args.robot != "none":
        if args.robot == "roborio":
            ip = "10.49.15.2"
        else:
            ip = "localhost"
        print("starting comm on " + ip)
        commChan = comm.Comm(ip)
    else:
        commChan = None

    readCam(commChan, args.image_width, args.iheight, args.fps, args.exposure)
    cv2.destroyAllWindows()
