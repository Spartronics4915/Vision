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
import time
import targetUtils
import logging
import targets
import poseEstimation

from pathlib import Path

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

def processFrame(frame, cfg=None):
    # Nb: in runPiCam, the algo-specific config is passed into processFrame.
    #   Thus, we only need to get the "algo" value out of the passed object.
    algo = cfg["algo"]
    if algo == None or algo == "default":
        return defaultAlgo(frame, cfg)
    elif algo == "empty" or algo == "bypass":
        return emptyAlgo(frame, cfg)
    elif algo == "mask":
        return maskAlgo(frame, cfg)
    elif algo == "hsv":
        return hsvAlgo(frame, cfg)
    elif algo == "verticies":
        return generatorHexagonVerticies(frame, cfg)
    elif algo == "calibCap":
        return calibrationCapture(frame, cfg)
    elif algo == "pnp":
        return realPNP(frame, cfg)
    else:
        logging.info("algo: unexpected name " + algo + " running default")
        return defaultAlgo(frame, cfg)

def defaultAlgo(frame, cfg):
    return hsvAlgo(frame, cfg)

def maskAlgo(frame, cfg):
    # Show what is shown by the opencv HSV values
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(frame, cfg["hsvRangeLow"], cfg["hsvRangeHigh"])
    return None,mask

def emptyAlgo(frame, cfg):
    return (None,frame)

def hsvAlgo(frame,cfg):
    return (None,cv2.cvtColor(frame, cv2.COLOR_BGR2HSV))  # HSV color space

def generatorHexagonVerticies(frame, cfg):

    # Apply our thresholds to the frame
    frame = targetUtils.threshholdFrame(frame,cfg)

    # Taget acquisition
    target, frame = targetUtils.findTarget(frame,cfg)


    return (None, frame)

def calibrationCapture(frame, config):
    # A pipeline to capture frames (asymetic circles) to be used for clibration

    # TODO: Format for use with /data directory
    output_dir = Path('calib_imgs')

    output_dir.mkdir(exist_ok=True)
    '''
    # Pattern intrensics    
    pattern_width = 8
    pattern_height = 27
    pattern_size = (pattern_width, pattern_height)
    img_ind = 0
            
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # cv2.imshow('frame',gray)
    ret, centers = cv2.findCirclesGrid(gray, pattern_size, None, cv2.CALIB_CB_ASYMMETRIC_GRID)
    
    if ret:
        cv2.imwrite(str(output_dir/'frame-{:04d}.png'.format(img_ind)), gray)
        img_ind += 1
        cv2.drawChessboardCorners(frame, pattern_size, centers, ret)
        # cv2.imshows are here
        
    
    time.sleep(.01)
    '''
    cv2.imwrite(str(output_dir/'frame-{}.png'.format(time.monotonic())), frame)
    time.sleep(.3)
    logging.debug("Frame captured")

    return (None, frame)

def realPNP(frame, config):
    # TODO: Try and convert the chamelion 'boundingbox' method to python
    # frame --> visImg (used for drawing) and mask (used for target detection)

    # -== Frame Threshholding ==-
    mask = targetUtils.threshholdFrame(frame,config)

    # Slight renaming, for convention
    visImg = frame
    # TODO: Add bitwise and 
    # -== Target Detection ==- 
    hexagonTarget, visImg = targetUtils.findTarget(visImg, mask, config)

    # If we don't detect a target, drop out here
    if hexagonTarget == None:
        return (None, visImg)
    # -== Target Manipulation ==-
    # TODO: Pretty sure config in unnessissary here
    imgPts = targetUtils.target2pnp8Points(hexagonTarget,config)

    xlateVector, rotVec, visImg = poseEstimation.estimatePose(visImg, imgPts, config)

    # Debug
    logging.debug("Translation Vector: ".format(xlateVector))
    logging.debug("Rotation Vector: ".format(rotVec))

    # Testing pnpTransformRobotCoordinates
    robotVector = targetUtils.pnpTransformRobotCoordinates(xlateVector, config)
    logging.debug("Transformed Vector: ".format(robotVector))
    # XXX: For now
    return (None, visImg)
