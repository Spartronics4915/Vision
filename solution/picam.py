from picamera import PiCamera
from picamera.array import PiRGBArray
import time
import threading
import sys

# -------------------------------------------------------------------------
class PiCam:
    def __init__(self, resolution=(320,240), framerate=60, auto=False):
        self.resolution = resolution
        self.framerate = framerate
        self.stream = None
        self.rawCapture = None
        if auto:
            smode = 0
        else:
            smode = 7 # fast
        self.cam = PiCamera(resolution=resolution, framerate=framerate,
                            sensor_mode=smode) # for fastest rates, 0 is auto)
        time.sleep(.1) # allow the camera to warm up
        if auto:
            self.cam.awb_mode = "auto"
            self.cam.exposure_mode = "auto"
            self.cam.shutter_speed = 0 # set to 0 to go auto
        else:
            self.cam.awb_mode = "off"
            # for digital-gain and analog_gain. These values can't
            # be set directly, rather "let them settle"...
            self.cam.exposure_mode = "off"
            self.cam.shutter_speed = 10000 # set to 0 to go auto

        self.cam.exposure_compensation = -25 # [-25, 25]
        self.cam.shutter_speed = 0 #10000 # set to 0 to go auto
        self.cam.contrast = 70  # [-100, 100]
        self.cam.awb_gains = (1.2, 1.6)  # red, blue balance
        self.cam.hflip = True
        self.cam.vflip = True
        self.cam.brightness = 70 # [0, 100]
        self.cam.sharpness = 0 # [-100, 100]
        time.sleep(.1) # more settling

        print("camera settings:")
        print("  analog_gain:%s" % self.cam.analog_gain)
        print("  digital_gain:%s" % self.cam.digital_gain)
        print("  awb_mode:%s" % self.cam.awb_mode)
        print("  awb_gains:(%g, %g)" % self.cam.awb_gains)
        print("  brightness:%d" % self.cam.brightness)
        print("  contrast:%d"  % self.cam.contrast)
        print("  saturation:%d" % self.cam.saturation)
        print("  drc_strength:%s" % self.cam.drc_strength)
        print("  exposure_compensation:%d" % self.cam.exposure_compensation)
        print("  exposure_mode:%s" % self.cam.exposure_mode)
        print("  exposure_speed:%d us" % self.cam.exposure_speed)
        print("  shutter_speed:%d us" % self.cam.shutter_speed)
        print("  framerate:%s" % self.cam.framerate)

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
        print("Capture thread starting")
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
                    # pool is empty, what for work to complete
                    sys.stderr.write('z')
                    time.sleep(0.01)
        self.picam.stop()
        print("Capture thread terminated")

    def cleanup():
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
        print('Processor thread %s started with idle time of %.2fs' %
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
        print("Processor thread %s terminated" % self.name)

