#!/usr/bin/env python
#
# picamera test & processing rig

# TODO:
#   wire-in (or eliminate) more of the args controlling, eg brightness
#

import cv2
import numpy as np
import picam
import time
import sys
import argparse
import os
import daemon

# local imports
import algo
import comm
import picam

class PiVideoStream:
    def __init__(self):
        self.windowName = "picamera"
        self.target = comm.Target()
        self.commChan = None
        self.parseArgs()
        print("testPCam pid: %d args:" % os.getpid())
        print(self.args)
        print("OpenCV version: {}".format(cv2.__version__))

        if self.args.robot != "none":
            if self.args.robot == "roborio":
                ip = "10.49.15.2"
            else:
                ip = "localhost"
            print("starting comm to " + ip)
            self.commChan = comm.Comm(ip)

        self.picam = picam.PiCam(resolution=(self.args.iwidth, 
                                             self.args.iheight),
                                 framerate=(self.args.fps))

    def parseArgs(self):
        """
        Parse input arguments
        """
        parser = argparse.ArgumentParser(description=
                             "Capture and display live camera video on raspi")
        parser.add_argument("--threads", dest="threads",
                            help="threads: (0-4) [0]",
                            default=0, type=int)
        parser.add_argument("--algo", dest="algo",
                            help="(empty, default)",
                            default="default")
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
        parser.add_argument("--debug", dest="debug",
                            help="debug: [0,1] ",
                            default=0)
        parser.add_argument("--daemonize",
                            help="run app in background",
                            action="store_true")
               
        self.args = parser.parse_args()

    def Run(self):
        if self.args.daemonize:
            with daemon.DaemonContext():
                self.go();
        else:
            self.go();

    def go(self):
        if self.args.threads == 0:
            self.processVideo()
        else:
            try:
                self.captureThread = picam.CaptureThread(self.picam, 
                                                        self.processFrame, 
                                                        self.args.threads)
                while self.captureThread.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nuser shutdown")
            except:
                e = sys.exc_info()
                print("\n")
                print(e)
                print("\nunexpected error")

            self.captureThread.running = False
            self.captureThread.join()
            self.captureThread.cleanup()

        if self.args.display:
            cv2.destroyAllWindows()

    def processVideo(self):
        """ create a camera, continually read frames and process them.
            In display mode, we run til 'q' or 'ESC' key is hit.
        """
        print("  (single threaded)")
        self.picam.start()
        while True:
            image = self.picam.next()
            if self.processFrame(image):
                break

    def processFrame(self, image):
        abort = False

        dx, frame = algo.processFrame(image, algo=self.args.algo, 
                                    display=self.args.display,
                                    debug=self.args.debug)
        
        if self.commChan:
            self.target.clock = time.clock()
            self.target.angleX = dx
            # Not setting dy, because that may mess things up
            self.commChan.SetTarget(self.target)

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
        
    def Shutdown(self):
        self.picam.stop()
        if self.commChan:
            self.commChan.Shutdown()
            
if __name__ == "__main__":
    pistream = PiVideoStream()
    pistream.Run()
    pistream.Shutdown()

