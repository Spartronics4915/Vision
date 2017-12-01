#!/usr/bin/python
import cv2
import numpy as np;
from multiprocessing.pool import ThreadPool
from collections import deque
import argparse

# local imports
import timing

class Settings:
    """contains program-wide config"""
    def __init__(self):
        self.width = 320
        self.height = 240
        self.fps =  60
        self.numThreads = 2
        self.display = True
        self.waitMS = 10 # for waitKey

class Mgr:
    """manages threads and work"""
    def __init__(self, settings):
        self.threadPool = ThreadPool(processes=settings.numThreads)
        self.pending =  deque()
        self.update = False

class Timing:
    """contains timing state"""
    def __init__(self):
        self.latency = timing.StatValue()
        self.frameT = timing.StatValue()
        self.lastFrameTime = timing.clock()

class Work:
    def __init__(self):
        self.ret = None
        self.img = None
        self.startTime = None

    def init(self, ret, img, st):
        self.ret = ret
        self.img = img
        self.startTime = st
        
class Result:
    def __init__(self):
        self.img = None
        self.keypoints = None
        self.startTime = None
        self.endTime = None

    def init(self, img, kp, st, et):
        self.img = img
        self.keypoints = kp
        self.startTime = st
        self.endTime = et

class App:
    # global container of all things
    def __init__(self):
        self.settings = Settings()
        self.mgr = Mgr(self.settings)
        self.timing = Timing()
        self.work = Work()
        self.result = Result()
        self.vsrc = None

        # first check for camera connection and config -------------------
        for i in range(0, 4):
            self.vsrc = cv2.VideoCapture(i)
            if not self.vsrc or not self.vsrc.isOpened():
                print("Problem opening video source %d" % i)
                self.vsrc = None
            else:
                break
        if not self.vsrc:
            exit(1)

        self.vsrc.set(cv2.CAP_PROP_FRAME_WIDTH, self.settings.width)
        self.vsrc.set(cv2.CAP_PROP_FRAME_HEIGHT, self.settings.height)
        self.vsrc.set(cv2.CAP_PROP_FPS, self.settings.fps)

        # next setup params for BlobDetector ------------------------------
        self.params = cv2.SimpleBlobDetector_Params()
        self.params.minThreshold = 10
        self.params.maxThreshold = 200
        self.params.filterByArea = True
        self.params.minArea = 1500
        self.params.filterByCircularity = True
        self.params.minCircularity = 0.1
        self.params.filterByConvexity = True
        self.params.minConvexity = 0.87
        self.params.filterByInertia = True
        self.params.minInertiaRatio = 0.01
        self.detector = cv2.SimpleBlobDetector_create(self.params)

    def Run(self):
        # loop forever searching for blobs ------------------------------------
        while True:
            # frames are captured in the main thread (below) and processed 
            # in another thread, then post-processed in main thread.
    
            # first check if processed frames are ready for postprocessing...
            while len(self.mgr.pending) > 0 and  \
                    self.mgr.pending[0].ready():
                result = self.mgr.pending.popleft().get()
                now = timing.clock()
                self.timing.latency.update(now - result.startTime)
                # XXX: latency includes both processing time and deque time
                self.postProcessFrame(result)

            # next capture image if we aren't too busy processing the last one
            if len(self.mgr.pending) < self.settings.numThreads:
                ret, img = self.vsrc.read()  # <--- this blocks for XXms
                now = timing.clock()
                self.timing.frameT.update(now - self.timing.lastFrameTime)
                self.timing.lastFrameTime = now
                self.work.init(ret, img, now)
                task = self.mgr.threadPool.apply_async(
                                    processFrameCB, 
                                    (self, self.work))
                self.mgr.pending.append(task)
            else:
                print("busy")

            if self.settings.display:
                key = 0xFF & cv2.waitKey(self.settings.waitMS)
                if key == 27: # ESC
                    print("exiting...")
                    break

    # ----------------------------------------------------------------------
    def processFrame(self, work):
        """
        Runs in a secondary thread, processing incoming image and returns
        results to main thread for post-processing.
        """
        bwimg = cv2.cvtColor(work.img, cv2.COLOR_BGR2GRAY) # required by detect
        kp = self.detector.detect(bwimg)
        self.result.init(bwimg, kp, work.startTime, timing.clock())
        # XXX: release work.img here?
        # XXX: release bwimg here if not settings.display
        return self.result

    # ----------------------------------------------------------------------
    def postProcessFrame(self, result):
        """
        Runs in main thread, delivers keypoints to robot and screen
        """
        kp = result.keypoints
        img = result.img
        if self.settings.display:
            if len(kp) > 0:
                # Draw detected blobs as red circles.
                # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures
                # the size of the circle corresponds to the size of blob
                kpimg = cv2.drawKeypoints(img, kp, np.array([]), 
                        (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
                cv2.imshow("Keypoints", kpimg)
            else:
                cv2.imshow("bw", img)

def processFrameCB(o, work):
    return o.processFrame(work)

if __name__ == '__main__':
    App().Run()

