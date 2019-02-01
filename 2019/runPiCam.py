#!/usr/bin/env python3 
#
# runPiCam.py runs the imaging algorithm in algo.py on a stream
# of video frames.
#

import cv2
import numpy as np
import picam
import time, datetime
import sys
import argparse
import os
import logging

# local imports
import algo
import comm
import picam

class PiVideoStream:
    def __init__(self):
        # no longer needed:
        #   os.system('sudo ifconfig wlan0 down')
        logFmt = "%(name)-8s %(levelname)-6s %(message)s"
        dateFmt = "%H:%M"
        logging.basicConfig(filename="/tmp/runPiCam.log",level=logging.DEBUG,
                            format=logFmt, datefmt=dateFmt)
        logging.debug("\n--------------------New run------------------")
        logging.debug("Run started at: ")
        logging.debug(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
        logging.debug("---------------------------------------------\n")
        self.target = comm.Target()
        self.commChan = None
        self.parseArgs()
        logging.info("pid: %d" % os.getpid())
        logging.info("args: " + str(self.args))
        logging.info("opencv version: {}".format(cv2.__version__))
        if self.args.robot != "none":
            if self.args.robot == "roborio":
                fmt = "%Y/%m/%d %H:%M:%S"
                logging.debug(datetime.datetime.now().strftime(fmt))
                logging.debug("Connecting to robot at 10.49.15.2...")
                ip = "10.49.15.2"
            else:
                ip = "localhost"
            logging.info("starting comm to " + ip)
            self.commChan = comm.Comm(ip)

        self.picam = picam.PiCam(resolution=(self.args.iwidth, 
                                             self.args.iheight),
                                 framerate=(self.args.fps))

    def parseArgs(self):
        """
        Parse input arguments
        """
        parser = argparse.ArgumentParser(description=
                            "Capture and process picamera stream")
        parser.add_argument("--threads", dest="threads",
                            help="threads: (0-4) [2]",
                            default=2, type=int)
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
                            help="robot (localhost, roborio) [localhost]",
                            default="localhost")
        parser.add_argument("--brightness", dest="brightness",
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
 
        self.args = parser.parse_args()
        #Logging
        logging.debug(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
        logging.debug("Parsed the following args:")
        logging.debug(self.args)

    def Run(self):
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
        value, frame = algo.processFrame(image, algo=self.args.algo, 
                                        display=self.args.display,
                                        debug=self.args.debug)
        if (self.args.debug):
            logging.info("Target value is: ", value)

        if self.commChan:
            if (value == None):
                self.commChan.updateVisionState("Searching")
            else:
                self.commChan.updateVisionState("Acquired")  
                if self.target.setValue(value):
                    self.commChan.SendTarget(self.target)
        else:
            print("Target value is: {}".format(value))
        
    def Shutdown(self):
        self.picam.stop()
        if self.commChan:
            self.commChan.Shutdown()
            
def main():
    pistream = PiVideoStream()
    pistream.Run()
    pistream.Shutdown()

if __name__ == "__main__":
    main()

