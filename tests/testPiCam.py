#!/usr/bin/env python
#
# picamera test & processing rig

# TODO:
#   wire-in (or eliminate) more of the args controlling, eg brightness
#

import cv2
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
import comm
import time
import sys
import argparse

import algo


class PiVideoStream:
    def __init__(self):
        self.windowName = "picamera"
        self.target = comm.Target()
        self.commChan = None
        self.parseArgs()
        print("Called with args:")
        print(self.args)
        print("OpenCV version: {}".format(cv2.__version__))

        if self.args.robot != "none":
            if self.args.robot == "roborio":
                ip = "10.49.15.2"
            else:
                ip = "localhost"
            print("starting comm on " + ip)
            self.commChan = comm.Comm(ip)

    def Run(self):
        self.processVideo()
        if self.args.display:
            cv2.destroyAllWindows()

    def parseArgs(self):
        """
        Parse input arguments
        """
        parser = argparse.ArgumentParser(description=
                             "Capture and display live camera video on raspi")
        parser.add_argument("--width", dest="iwidth",
                            help="image width [320]",
                            default=320, type=int)
        parser.add_argument("--height", dest="iheight",
                            help="image height [240]",
                            default=240, type=int)
        parser.add_argument("--fps", dest="fps",
                            help="FPS [60]",
                            default=60, type=int)
        parser.add_argument("--display", dest="display",
                            help="display [0]",
                            default=0, type=int)
        parser.add_argument("--threaded", dest="threaded",
                            help="threaded: (0,1) [0]",
                            default=0, type=int)
        parser.add_argument("--robot", dest="robot",
                            help="robot (off, localhost, roborio) [robot]",
                            default="localhost")
        parser.add_argument("--brightness", dest="brightness [50]",
                            help="brightness: [0, 100]",
                            default=50, type=int)
        parser.add_argument("--exposure", dest="exposure",
                            help="exposure: (5, 20000) [10]",
                            default=10, type=int)
        parser.add_argument("--contrast", dest="contrast",
                            help="contrast: (-100, 100) [0]",
                            default=0, type=int)
        parser.add_argument("--color", dest="color",
                            help="color: ([0,255],[0,255])",
                            default=None)
        self.args = parser.parse_args()

    def processFrame(self, image):
        abort = False
        if self.commChan:
            self.target.clock = time.clock()
            self.commChan.SetTarget(self.target)

        frame = algo.processFrame(image)
        if self.args.display:
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q") or key == 27:
                abort = True
            elif key == 255:
                pass
            elif key == 22:
               print("22 --");
            else:
                print(key)
        return abort

    def processVideo(self):
        """ create a camera, continually read frames and process them.
            In display mode, we run til 'q' or 'ESC' key is hit.
        """
        rez = (self.args.iwidth, self.args.iheight)
        with PiCamera(resolution=rez, framerate=self.args.fps,
                      sensor_mode=7  # for fastest frame rates, 0 is auto
                      ) as camera:

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

            self.rawCapture = PiRGBArray(camera, size=rez)
            self.stream = camera.capture_continuous(self.rawCapture, format="bgr", 
                                                use_video_port=True)
            if not self.args.threaded:
                print("  (single threaded)")
                for frame in self.stream:
                    image = frame.array
                    self.rawCapture.truncate() # clear the stream for the next frame
                    self.rawCapture.seek(0) 
                    if self.processFrame(image):
                        break
            else:
                print("  (multi threaded)")
                self.processedFrame = -1
                self.capturedFrame = -1 
                self.stopped = 0
                t = Thread(target=self.captureFrames, args=())
                t.daemon = True
                t.start()
                while self.stopped != 2:
                    if self.processedFrame != self.capturedFrame:
                        self.processedFrame = self.capturedFrame
                        if self.processFrame(self.frame):
                            if self.stopped == 0:
                                self.stopped = 1
                        else:
                            # print(".")
                            if self.processedFrame > 500:
                                print("500 frames")
                                self.stopped = 1

            self.stream.close()
            self.rawCapture.close()
            
    def captureFrames(self):
        print('starting capture thread')
        for f in self.stream:
            self.frame = f.array
            self.rawCapture.truncate(0)
            self.rawCapture.seek(0) 
            self.capturedFrame += 1
            if self.stopped == 1:
                self.stopped = 2
                break
        print('stopping capture thread')

if __name__ == "__main__":

    pistream = PiVideoStream()
    pistream.Run()

