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

    # Pattern intrensics    
    pattern_width = 8
    pattern_height = 27
    diagonal_dist = 30e-3 # In meters
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
    return (None, frame)

def realPNP(frame, config):
    # TODO: Doctests
    # TODO: Try and convert the chamelion 'boundingbox' method to python
    # -== Target Detection ==-
    goodPoints = None


    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Filter out the colors we don't need
    mask = cv2.inRange(frame, cfg["hsvRangeLow"], cfg["hsvRangeHigh"])

    visImg = None

    if cfg['display'] == 1:
        visImg = cv2.bitwise_and(frame, frame, mask=mask)

    # Get countours
    img, cnts, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Get the shape
    for c in cnts:

        # Contour perimiter
        peri = cv2.arcLength(c, True)

        # approximating a shape around the contours
        # Can be tuned to allow/disallow hulls
        # Approx is the number of verticies
        # Ramer–Douglas–Peucker algorithm
        approx = cv2.approxPolyDP(c, 0.01 * peri, True)
        # Approx is a list of points that defines the polygon

        # logging.debug("Value of approxPolyDP: " + str(len(approx)))

        if len(approx) == 8:
            # Only add known good rectangles to out list of good poitns
            # XXX: Hack for now
            goodPoints = approx

    # -= Get points in 2019.01.22 'PnP Format' =- #
    # XXX: THIS LOGIC DOES NOT WORK WITH A ROTATED TAGET, EVERYTHING
    #      ASSUMES A HORIZONTAL TARGET
    # 
    # Fall out if there is no target detected

    if goodPoints is None:
        return (None, img)

    a = None # Leftmost point
    b = None # Leftmost, bottom-most point
    c = None # Rightmost, bottom-most point
    d = None # Rightmost point

    # Sidestepping the strange way numpy organises its lists
    formattedPoints = []
    for i in goodPoints:
        formattedPoints.append(i[0])


    # Sorts in low -> high
    # Origin of cv2 img is top left
    xSorted = sorted(formattedPoints,key=lambda p:p[0])
    ySorted = sorted(formattedPoints,key=lambda p:p[1])

    # bottomMost = (bottomMost point, next point up)
    bottomMost = (ySorted[len(ySorted)-1], ySorted[len(ySorted)-2])
    
    # Sorts in low -> high
    # Now should be the (leftMost, bottomMost point, rightMost, bottomMost point)
    bottomMost = sorted(bottomMost,key=lambda p:p[0])

    b = bottomMost[0].tolist()
    c = bottomMost[1].tolist()

    # Left-Most
    a = xSorted[0].tolist()
    # Right-Most
    d = xSorted[len(xSorted)-1].tolist()

    imgPts = np.array([a,b,c,d],dtype='int32')

    xlateVector, rotVec, frame = poseEstimation.estimatePose(visImg, imgPts, config)

    # Deubg
    logging.debug("Translation Vector: " + str(xlateVector))
    logging.debug("Rotation Vector: " + str(rotVec))

    if config['display']:
        for point in goodPoints:
            # Draw our point
            cv2.circle(frame, point, 3, (255,255,0))

    # XXX: For now
    return (None, frame)
    pass