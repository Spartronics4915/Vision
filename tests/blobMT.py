#!/usr/bin/python
import cv2
import numpy as np
import argparse

# local imports
from video import WebcamVideoStream

class App:
    # global container of all things
    def __init__(self):
        self.display = True
        self.waitMS = 1
        self.frameNum = -1
        self.vstream = WebcamVideoStream(resolution=(320,240), framerate=60)
        self.params = cv2.SimpleBlobDetector_Params()
        self.params.minThreshold = 150
        self.params.maxThreshold = 230
        self.params.filterByArea = True
        self.params.minArea = 1500
        self.params.filterByCircularity = True
        self.params.minCircularity = 0.1
        self.params.filterByConvexity = False
        self.params.minConvexity = 0.87
        self.params.filterByInertia = False
        self.params.minInertiaRatio = 0.01
        self.detector = cv2.SimpleBlobDetector_create(self.params)

    def Run(self):
        self.vstream.start() # start capturing in another thread
        while True:
            fnum = self.vstream.fps.getFrameCount() 
            if fnum != self.frameNum:
                self.frameNum = fnum
                result = self.processFrame(self.vstream.frame)
                self.postProcessFrame(result)

            if self.display:
                # call to waitKey is *required* for imshow
                key = 0xFF & cv2.waitKey(self.waitMS)
                if key == 27: # ESC
                    print("exiting... %f fps" % self.vstream.fps.getFPS())
                    break

    # ----------------------------------------------------------------------
    def processFrame(self, frame):
        bwimg = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # required by detect
        kp = self.detector.detect(bwimg)
        return (bwimg, kp)

    # ----------------------------------------------------------------------
    def postProcessFrame(self, result):
        img,kp = result
        # here we send processed keypoints to robot

        if self.display:
            if len(kp) > 0:
                # Draw detected blobs as red circles.
                # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures
                # the size of the circle corresponds to the size of blob
                kpimg = cv2.drawKeypoints(img, kp, np.array([]), (0,0,255), 
                                   cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
                cv2.imshow("Keypoints", kpimg)
            else:
                cv2.imshow("bw", img)

if __name__ == '__main__':
    App().Run()

