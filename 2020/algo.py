'''
Solution/algo.py

Script to hold OpenCV calls, in addition to all tuning values assoicated with the finding of the object of intrest in frame

Used by:
    - runPicam.py
    - testPiCam.py
TODO: Refactor some parts of the pipeline into classes
TODO: Better Varible Names
'''

import numpy as np
import cv2
import poseEstimation
import time
import traceback
import rectUtil
import logging
import targets


# Reasoning behind Current range values:
#   After changes to exposure of camera (Ridiculously low ISO),
#   retro-reflective tape stands out more than it ever has,
#   thus, hue and the saturation have less importance,
#   which explains the wide range on the first two numbers.
#   10-115 represents an (approximate) range of blue to green
#   in the HSV colorspace 50-255 represents a wide range of the
#   saturation of any given color
#
#   (This value is fluid, as we aren't searching for any particular 'color',
#   [read: 2018], it can be very open)
#
#   Finally, the tightest value needs to be the value, representing how
#   close the color is to black.  We want colors as far away from black
#   as possible, thus the high range.

#   TODO: Change all algo's to return a target

def processFrame(frame, algo=None, cfg=None, display=0, debug=0):
    if algo == None or algo == "default":
        return defaultAlgo(frame, cfg, display, debug)
    elif algo == "empty" or algo == "bypass":
        return emptyAlgo(frame, cfg)
    elif algo == "mask":
        return maskAlgo(frame, cfg)
    elif algo == "hsv":
        return hsvAlgo(frame, cfg)
    else:
        logging.info("algo: unexpected name " + algo + " running default")
        return defaultAlgo(frame, cfg, display, debug)

def defaultAlgo(frame, cfg, display=0, debug=0):
    return hsvAlgo(frame, cfg)

def maskAlgo(frame, cfg):
    # Show what is shown by the opencv HSV values
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(frame, cfg["hsvRange0"], cfg["hsvRange1"])
    return None,mask

def emptyAlgo(frame,cfg):
    return (None,frame)

def hsvAlgo(frame,cfg):
    return (None,cv2.cvtColor(frame, cv2.COLOR_BGR2HSV))  # HSV color space