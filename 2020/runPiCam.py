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
import targets
import config

class PiVideoStream:
    def __init__(self):
        
        self.commChan = None
        self.parseArgs()

        #   logger init:
        #     - we write logging info to file, for performance this should be
        #       minimized.
        #     - during debugging, set the loglevel to debug and see the 'spew'
        #       via:  "tail -f /tmp/runPiCam.log"
        if self.args.debug:
            logLevel = logging.DEBUG
        else:
            logLevel = logging.INFO
        
        logging.basicConfig(level=logLevel,
                            format="%(asctime)s %(levelname)-6s: %(message)s",
                            datefmt="%m/%d %H:%M:%S",
                            # This file is avible to write to, even when the pi is in 'read-only' mode
                            filename="/tmp/runPiCam.log",
                            filemode="a")
        logging.info("--------------------New run------------------")
        logging.info("pid: %d" % os.getpid())
        logging.info("args: " + str(self.args))
        logging.info("opencv version: {}".format(cv2.__version__))
        logging.debug("Parsed the following args:")
        logging.debug(self.args)
        
        if self.args.robot != "none":
            if self.args.robot == "roborio":
                fmt = "%Y/%m/%d %H:%M:%S"
                logging.debug(datetime.datetime.now().strftime(fmt))
                logging.debug("Connecting to robot at 10.49.15.2...")
                ip = "10.49.15.2"
            else:
                ip = self.args.robot
            logging.info("starting comm to " + ip)
            self.commChan = comm.Comm(ip)

        # parameter configuration -----
        self.config = getattr(config, self.args.config) # reads named dict
        self.picam = picam.PiCam(self.config["picam"])
        self.algoConfig = self.config["algo"]
        # Updating config with passed commands
        # XXX: Need logic to check if these values exist in the chosen config
        #      Unsure if an error will be thrown
        if (self.args.display):
            self.algoConfig["display"] = True

        if (self.args.algo is not None):
            self.algoConfig["algo"] = self.args.algo

    def parseArgs(self):
        """
        Parse input arguments
        """
        parser = argparse.ArgumentParser(description=
                            "Capture and process picamera stream")
        parser.add_argument("--config", dest="config",
                            help="config: default,greenled,noled...",
                            default="default")
        parser.add_argument("--threads", dest="threads",
                            help="threads: (0-4) [2]",
                            default=2, type=int)
        parser.add_argument("--algo", dest="algo",
                            help="(empty, default)",)
        parser.add_argument("--display", dest="display",
                            help="display [0,1]",
                            action=store_true)
        parser.add_argument("--robot", dest="robot",
                            help="robot (localhost, roborio) [localhost]",
                            default="localhost")
        parser.add_argument("--debug", dest="debug",
                            help="debug: [0,1] ",
                            default=0)

        self.args = parser.parse_args()

    def Run(self):
        self.go()

    def go(self):
        if self.args.threads <= 1:
            self.processVideo()
        else:
            try:
                self.captureThread = picam.CaptureThread(self.picam,
                                                        self.processFrame,
                                                        self.args.threads)
                while self.captureThread.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                logging.info("\nuser shutdown")
            except:
                e = sys.exc_info()
                logging.info("\n")
                logging.info(e)
                logging.info("\nunexpected error")

            self.captureThread.running = False
            self.captureThread.join()
            self.captureThread.cleanup()

        if self.args.display:
            cv2.destroyAllWindows()

    def processVideo(self):
        """ create a camera, continually read frames and process them.
        """
        logging.info("  (single threaded)")
        self.picam.start()
        logging.debug(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
        logging.debug("Began processing images")
        while True:
            # The image here is directly passed to cv2.
            image = self.picam.next()
            if self.processFrame(image):
                break

    def processFrame(self, image):
        # ?
        logging.debug("  (multi threaded)")

        target, frame = algo.processFrame(image, cfg=self.config["algo"])

        if target != None:
            logging.debug("Target value is: " + str(target))
        if self.commChan:
            if target != None:
                self.commChan.UpdateVisionState("Aquired")
                target.send()
            else:
                self.commChan.UpdateVisionState("Searching")

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

