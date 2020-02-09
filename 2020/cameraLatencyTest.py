from picamera import PiCamera
from picamera.array import PiRGBArray
import time
import picam

cfg = {"resolution": (1920, 1080), # cv2.resize() later
    "framerate": 30, # TODO: Come back to
    "iso": 400,
    "brightness": 40,
    "contrast": 100,
    "flip": False,
    "rotation": 0,
    "exposure_mode": "off", #"fixedfps",
    "exposure_compensation": -25,
    "sensormode": 7
}

framesCap = 0
camera = picam.PiCam(config = cfg)

camera.start()
times = []
initTime = time.monotonic()
while framesCap < 10:
     frame = camera.next()
     framesCap += 1
finalTime = time.monotonic()
print("Frames Capped: {}".format(framesCap))
print("Average Time : {}".format((finalTime - initTime)/framesCap))
