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
import pnpSorting
import time
import traceback
import rectUtil
import logging
import targets

# Deprecated 2018 values:
# range0 = np.array([0,150,150]) # min hsv
# range1 = np.array([50, 255, 255]) # max hsv

range0 = np.array([50,150,100])
range1 = np.array([70,255,255])

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
#   TODO: Change all algo's to return the same amount of things

def processFrame(frame, algo=None, display=0,debug=0):
    if algo == None or algo == "default":
        return defaultAlgo(frame, display, debug)
    elif algo == "rect":
        return rectAlgo(frame, display, debug)
    elif algo == "empty" or algo == "bypass":
        return emptyAlgo(frame)
    elif algo == "mask":
        return maskAlgo(frame)
    elif algo == "realPNP":
        return realPNP(frame,display,debug)
    elif algo == "hsv":
        return hsvAlgo(frame)
    else:
        print("algo: unexpected name " + algo + " running default")
        return defaultAlgo(frame)

def emptyAlgo(frame):
    return (None,frame)

def hsvAlgo(frame):
    return (None,cv2.cvtColor(frame, cv2.COLOR_BGR2HSV))  # HSV color space

def maskAlgo(frame):
    # Show what is shown by the opencv HSV values
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(frame, range0, range1)

    return None,mask

def rectAlgo(frame,display=1,debug=0):
    # TODO: Implement some form of threading / process optimisation
    rects = []
    #largeTargetA = 0        # Need these vars to filter for large targets
    #largeTargetC = (1600,0)

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # HSV color space
    mask = cv2.inRange(frame, range0, range1)       # Our HSV filtering

    rects = rectUtil.findRects(frame,200,display,debug)

    if display:
        for r in rects:
            # combine original image with mask, for visualization
            visImg = cv2.bitwise_and(frame, frame, mask=mask) # Only run in display

            pts = cv2.boxPoints(r)  # Turning the rect into 4 points to draw
            box = [np.int32(pts)]

            cv2.drawContours(visImg, [box], 0,(0,0,255),2)
    else:
        visImg = frame # poseEstimation needs valid frame for camMatrix calcs

    return (None, visImg)

def defaultAlgo(frame,display=0,debug=0):
    # Thoughts: See white board, soon to move to README.md
    # Find rectangle
    rects = rectUtil.findRects(frame,200,display,debug)
     
    # Pair rectangles
    # Leftpair is allways leftmost
    # XXX: rightPair is not always the rightmost
    success, leftPair,rightPair = rectUtil.pairRectangles(rects,wantedTargets=1,debug=1)

    # Apply real pnp
    # THIS IS A FUNCTION TO CALL:
    # sort points
    # estimate pose
    target, frame = realPNP(frame,(leftPair,rightPair),success,display)

    # TODO: Fix this, bad stle code
    targetRects = []

    for r in leftPair:
        targetRects.append(r)
    for r in rightPair:
        targetRects.append(r)

    # Generate drawing values
    displayTarget = rectUtil.circlesFromRects(targetRects)

    return target, displayTarget, frame

def realPNP(frame, pairs, success,display=0):
    # TODO: Remove debug from all function calls, and use logger.debug()
    # nb: caller is responsible for threading (see runPiCam.py)
    # Spew

    if success == False:
        # Logger debugs happened in pairRectangles
        return None, frame

    if display:
        # combine original image with mask, for visualization
        mask = cv2.inRange(frame, range0, range1)       # Our HSV filtering
        visImg = cv2.bitwise_and(frame, frame, mask=mask)
        for r in rects:
            pts = cv2.boxPoints(r)  # Turning the rect into 4 points to draw
            ipts = [np.int32(pts)]
            cv2.polylines(visImg, ipts, True, (255,0,0))
    else:
        # Avoid a NoneType error
        visImg = frame

    logging.debug("All valid rectangles are: " + str(rects))

    # TODO: support for infinite targets
    lTarget = None
    rTarget = None

    for pair in pairs:

        lPts = None
        rPts = None

        # Creating lists of points
        try:
            # Left points
            lPts = cv2.boxPoints(pair[0])
            lPts = np.int0(lPts)
            # Right points
            rPts = cv2.boxPoints(pair[1])
            rPts = np.int0(rPts)

        except (TypeError, IndexError) as e:
            # nb:   This is poor code in the event that we get a rectpair
            #       (l,None,r)  because the loop will break at the middle
            #       rect, and never reach the right rect.
            break

        logging.debug("sending a point list of: " + str(lPts))
        # Orders the points according to modelpoints in solvePNP()
        orderedPoints = pnpSorting.sortPoints(lPts,rPts)
        logging.debug("Passing an orderedPoints of: " + str(orderedPoints))

        # Now estimatePose accepts optional camera matrix
        # Only takes a image to draw on it if spectified
        target,frame = poseEstimation.estimatePose(visImg, orderedPoints,
                                            cameraMatrix=None, display=False)

        if not lTarget:
            lTarget = target
        else:
            rTarget = target

    return targets.TargetPNP(lTarget,rTarget),frame




