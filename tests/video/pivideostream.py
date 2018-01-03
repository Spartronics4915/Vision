# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
import time
import cv2
import sys

class PiVideoStream:
    def __init__(self, resolution=(320, 240), framerate=32):
        # initialize the camera and stream
        self.camera = PiCamera(resolution=resolution, framerate=framerate,
                                sensor_mode=7) # 7 is fastest frame rate
        self.camera.exposure_mode = "off"
        self.camera.exposure_compensation = -25 # [-25,25]
        self.camera.shutter_speed = 10000 # set to 0 for auto
        self.camera.contrast = 80 # [-100,100]
        self.rawCapture = PiRGBArray(self.camera, size=resolution)

        time.sleep(0.1)
        self.stream = self.camera.capture_continuous(self.rawCapture,
            format="bgr", use_video_port=True)

        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.stopped = False
        self.frameNum = 0

    def getFrameNum(self):
        return self.frameNum
    
    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        time.sleep(.1)
        return self

    def next(self):
        if self.stream:
            f = next(self.stream).array
            self.rawCapture.truncate(0)
            self.frameNum += 1
            return f
        else:
            return None

    def shutdown(self):
        self.stream.close()
        self.rawCapture.close()
        self.camera.close()

    def update(self):
        # keep looping infinitely until the thread is stopped
        for f in self.stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            sys.stderr.write(".")
            self.frame = f.array
            self.rawCapture.truncate(0)
            self.frameNum += 1
    
            # if the thread indicator variable is set, stop the thread
            # and resource camera resources
            if self.stopped:
                self.shutdown()
                return

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
