#
# vision parameter groups (aka configs)
#
# given the name of a config (eg "greenled") access via:
#
#  import config
#  cfg = getattr(config, "greenled")
#
#  (see bottom for details on parameters)
import numpy as np
import copy

_base = {
    "picam": {
        "resolution": (320, 240),
        "framerate": 60,
        "sensormode": 0,  # auto-calc based on res and framerate
    },
    "algo": {
        # Deprecated 2018 values:
        # "hsvRange0": np.array([0,150,150]),
        #              np.array([50,150,100]),
        # Deprecated 2019 values:
        # "hsvRange1": np.array([50, 255, 255]),
        #              np.array([70,255,255]),
        "hsvRange0": np.array([30,150,170])
        "hsvRange1": np.array([90,255,255])
    }
}

greenled = copy.deepcopy(_base)
greenled.update({
    "name": "greenled",
});
greenled["picam"].update({
    "iso": 400,  # 100-800 (higher numbers are brighter)
    "brightness": 20,
    "contrast": 100,
    "flip": True,
    "rotate": 90,
    "exposure_mode": "fireworks",
    "exposure_compensation": -25, # [-25, 25]
})

noled = copy.deepcopy(_base)
noled.update({
    "name": "noled",
})
noled["picam"].update({
    "iso": 400,
    "brightness": 40,
    "contrast": 100,
    "flip": False,
    "rotate": 0,
    "exposure_mode": "off", #"fixedfps",
    "exposure_compensation": 0, # [-25, 25]
})
noled["algo"].update({
    "hsvRange0": np.array([0,0,100]),
    "hsvRange1": np.array([255,255,255]),
})

default = greenled

# picam parameters ---------------------------------------------
# see: https://picamera.readthedocs.io/en/release-1.13/api_camera.html
#
#  analog_gain: read-only after setting exposure/iso
#  annotate_*
#  awb_gains:  red-blue balance depends upon awb_mode != "off"
#              range: 0-8, typically: .9-1.9
#  awb_mode: ("auto") ["off", "auto", "cloudy", ...' (white balance)
#  brightness: (50) [0-100]
#  clock_mode
#  closed: read-only
#  color_effects: (None) or (u,v) between 0-255
#  contrast: (0) [-100, 100]
#  crop: (see zoom)
#  digital_gain: read-only after setting exposure/iso
#  drc_strength (off) [off, low, medium, high] (dynamic range compression)
#  exposure_compensation (0) [-25, 25]
#  exposure_mode (auto) [off, auto, ..., fixedfps, ...]
#       off is special: disabled auto-gain-control fixing values for 
#       digital_gain and analog_gain.  These are set indirectly via
#       iso call which should be made (and allowed to settle) before
#       setting the mode to off.
#  exposure_speed: read-only microseconds, relates to shutter-speed
#  flash_mode:
#  frame:
#  framerate: pertains to video-port captures. Coupled with resolution
#       determines the mode that the camera operates in. 
#       see also sensor_mode
#  framerate_range:
#  hflip, vflip:  (False)
#  image_denoise: (True)
#  image_effect: (none) [none,negative,blur,...,posterize...]
#  iso (light sensitivity): sets analog_gain and digital_gain
#       (0) [0,100,200,320,400,500,640,800] (0 is auto)
#   certain exposure_modes override iso (esp "off") 
#  led (False)
#  meter_mode: (average) [average,spot,backlit,matrix]
#  preview...
#  raw_format: deprecated
#  recording: read-only
#  resolution: (X,Y), 'XxY', etc
#  revision: read-only  [ov5647, imx219]  means V1 or V2 cam module
#  saturation: (0) [-100, 100]
#  sensor_mode: (0) [0-7]  (0 computes based on framerate & res, 7 is fastest)
#  sharpness: (0) [-100,100]
#  shutter_speed: (0) microsecs (set with framerate, overlap exposure_speed)
#  still_stats
#  timestamp
#  vflip, hflip: (False)
#  video_denoise: (True)
#  video_stabilization: (False)
#  zoom: (0,0,1,1)

# algo parameters ---------------------------------------------

