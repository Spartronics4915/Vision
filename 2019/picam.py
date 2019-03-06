from picamera import PiCamera
from picamera.array import PiRGBArray
import time
import threading
import sys
import logging

# -------------------------------------------------------------------------
class PiCam:
    def __init__(self, config=None):
        self.config = config
        if self.config == None:
            self.config = {
                "resolution": (640,480),
                "framerate": 60,
                "sensormode": 0,
            }

        self.resolution = self.config["resolution"]
        self.stream = None
        self.rawCapture = None

        self.cam = PiCamera(resolution=self.config["resolution"],
                            framerate=self.config["framerate"],
                            sensor_mode=self.config["sensormode"])
        time.sleep(.1) # allow the camera to warm up


        if "iso" in self.config:
            self.cam.iso = self.config["iso"]
            # allow the camera to warm up in case exposure_mode is "off"
            time.sleep(.1) 

        if "awb_mode" in self.config:
            self.cam.awb_mode = self.config["awb_mode"]

        if "awb_gains" in self.config:
            self.cam.awb_gains = self.config["awb_gains"]

        if "brightness" in self.config:
            self.cam.brightness = self.config["brightness"]

        if "contrast" in self.config:
            self.cam.contrast = self.config["contrast"]

        if "exposure_mode" in self.config:
            self.cam.exposure_mode = self.config["exposure_mode"]

        if "exposure_compensation" in self.config:
            self.cam.exposure_compensation=self.config["exposure_compensation"]

        if "flip" in self.config:
            self.cam.vflip = self.cam.hflip = self.config["flip"]

        if "rotation" in self.config:
            self.cam.rotation = self.config["rotation"]

        if "saturation" in self.config:
            self.cam.saturation = self.config["saturation"]

        if "sharpness" in self.config:
            self.cam.sharpness = self.config["sharpness"]

        if "shutter_speed" in self.config:
            self.cam.shutter_speed = self.config["shutter_speed"]

        time.sleep(.1) # more settling

        logging.info("camera settings:")
        logging.info("  analog_gain:%s" % self.cam.analog_gain)
        logging.info("  digital_gain:%s" % self.cam.digital_gain)
        logging.info("  awb_mode:%s" % self.cam.awb_mode)
        logging.info("  awb_gains:(%g, %g)" % self.cam.awb_gains)
        logging.info("  brightness:%d" % self.cam.brightness)
        logging.info("  contrast:%d"  % self.cam.contrast)
        logging.info("  saturation:%d" % self.cam.saturation)
        logging.info("  drc_strength:%s" % self.cam.drc_strength)
        logging.info("  exposure_compensation:%d" % self.cam.exposure_compensation)
        logging.info("  exposure_mode:%s" % self.cam.exposure_mode)
        logging.info("  exposure_speed:%d us" % self.cam.exposure_speed)
        logging.info("  shutter_speed:%d us" % self.cam.shutter_speed)
        logging.info("  framerate:%s" % self.cam.framerate)
        logging.info("  iso:%s" % self.cam.iso)

    def start(self):
        self.rawCapture = PiRGBArray(self.cam, size=self.resolution)
        self.stream = self.cam.capture_continuous(self.rawCapture, format="bgr",
                                                    use_video_port=True)
        self.numFrames = 0

    def next(self):
        frame = next(self.stream)
        image = frame.array
        self.rawCapture.truncate(0)
        self.numFrames += 1
        return image
    
    def stop(self):
        if self.stream:
            self.stream.close()
        if self.rawCapture:
            self.rawCapture.close()
        self.cam.close()

# ------------------------------------------------------------------------
class CaptureThread(threading.Thread):
    def __init__(self, picam, procCallback, numProcessingThreads=0):
        super(CaptureThread, self).__init__()
        self.picam = picam
        self.running = False
        if numProcessingThreads == 0:
            self.procThreads = None
        else:
            self.running = True
            wait = float(numProcessingThreads) / picam.framerate
            self.procPool = [ProcessingThread(self, i, procCallback, wait) 
                                for i in range(numProcessingThreads)]
            self.procThreads = self.procPool[:]
            self.lock = threading.Lock()
        self.procCallback = procCallback
        self.start()

    def run(self):
        logging.info("Capture thread starting")
        self.picam.start()
        while self.running:
            if self.procThreads == None:
                frame = self.picam.next()
                self.procCallback(frame)
            else:
                with self.lock:
                    if self.procPool: 
                        procThread = self.procPool.pop()
                    else:
                        procThread = False
                if procThread:
                    frame = self.picam.next()
                    procThread.nextFrame = frame # XXX: frame.copy()?
                    procThread.event.set()
                else:
                    # pool is empty, wait for work to complete
                    sys.stderr.write('z')
                    time.sleep(0.01)
        self.picam.stop()
        logging.info("Capture thread terminated")

    def cleanup(self):
        self.running = False
        if self.procThreads:
            for proc in self.procThreads:
                proc.event.set()
                proc.join()


# ------------------------------------------------------------------------
class ProcessingThread(threading.Thread):
    def __init__(self, mainthread, id, processCB, wait):
        super(ProcessingThread, self).__init__()
        self.mainthread = mainthread
        self.processCB = processCB
        self.event = threading.Event()
        self.eventWait = .01 # wait 
        self.name = str(id)
        logging.info('Processor thread %s started with idle time of %.2fs' %
                             (self.name, self.eventWait))
        self.start() 

    def run(self):
        while self.mainthread.running:
            self.event.wait(self.eventWait)
            if self.event.isSet():
                if not self.mainthread.running:
                    break;
                try:
                    self.processCB(self.nextFrame)
                finally:
                    self.nextFrame = None
                    self.event.clear()
                    with self.mainthread.lock:
                        self.mainthread.procPool.insert(0, self)
        logging.info("Processor thread %s terminated" % self.name)

