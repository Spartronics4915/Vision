#!/usr/bin/env python3 
#
# picamera test & processing rig

# TODO:
#   wire-in (or eliminate) more of the args controlling, eg brightness
#

import cv2
import numpy as np
import picam
import time, datetime
import sys
import argparse
import os
import daemon
import logging

# local imports
import algo
import comm
import picam

class PiVideoStream:
    def __init__(self):
        #I am not shure this is correct. According to docs, you do not instantate a logger.
        os.system('sudo ifconfig wlan0 down') # Can't have this up at comp
        logging.basicConfig(filename="../logs/runLogs.log",level=logging.DEBUG)

        logging.debug("\n--------------------New run------------------")
        logging.debug("Run started at: ")
        logging.debug(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
        logging.debug("---------------------------------------------\n")
        self.windowName = "picamera"
        self.target = comm.Target()
        self.commChan = None
        self.parseArgs()
        print("testPCam pid: %d args:" % os.getpid())
        print(self.args)
        print("OpenCV version: {}".format(cv2.__version__))

        if self.args.robot != "none":
            if self.args.robot == "roborio":
                logging.debug(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
                logging.debug("Connecting to robot at 10.49.15.2...")
                ip = "10.49.15.2"
            else:
                ip = "localhost"
            print("starting comm to " + ip)
            self.commChan = comm.Comm(ip)

        self.picam = picam.PiCam(resolution=(self.args.iwidth, 
                                             self.args.iheight),
                                 framerate=(self.args.fps))
        # Push something down the pipe.
        self.commChan.SetTarget(self.target)

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
        #Logging
        logging.debug(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
        logging.debug("Parsed the following args:")
        logging.debug(self.args)

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
        logging.debug(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
        logging.debug("Began processing images")
        while True:
            # The image here is directly passed to cv2. 
            image = self.picam.next()
            if self.processFrame(image):
                break

    def processFrame(self, image):
        abort = False
        dirtyx, frame = algo.processFrame(image, algo=self.args.algo, 
                                    display=self.args.display,
                                    debug=self.args.debug)
        if (self.args.debug):
            print("Dirtyx is at: ", dirtyx)
            print("self.target.anglex is at: ", self.target.angleX)
        if self.commChan:
            self.target.clock = time.clock()
            if (dirtyx > 25): #Largest angle we expect is 22
                #logging.debug(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
                #logging.debug("Sent a 'searching' to networktables\n") 
                self.commChan.updateVisionState("Searching")
            else:
                #logging.debug(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
                #logging.debug("Sent a 'aquired' to networktables\n", )
                self.commChan.updateVisionState("Aquired")  
            # sending 'aquired' may be independent of the fact that we send a new target over   
            if (dirtyx != self.target.angleX):
                if (self.args.debug):
                    print("self.target.angleX is being changed to...", dirtyx)
                    # Fix 0 bug?
                #logging.debug(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
                #logging.debug("DirtyX is currently at:", dirtyx)
                self.target.angleX = dirtyx
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

