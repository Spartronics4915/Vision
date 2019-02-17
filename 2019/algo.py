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
# Deprecated 2018 values:
# range0 = np.array([0,150,150]) # min hsv
# range1 = np.array([50, 255, 255]) # max hsv

range0 = np.array([30,150,170])
range1 = np.array([90,255,255])

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

def emptyAlgo(frame):
    return (None,frame)

def hsvAlgo(frame):
    return (None,cv2.cvtColor(frame, cv2.COLOR_BGR2HSV))  # HSV color space

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
        print("algo: unexpected name " + algo)
        return emptyAlgo(frame)

def maskAlgo(frame):
    # Show what is shown by the opencv HSV values
    mask = cv2.inRange(frame, np.array([225,225,225]), np.array([255,255,255]))      
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
        # combine original image with mask, for visualization
        cv2.drawContours(visImg, [box], 0,(0,0,255),2)
        visImg = cv2.bitwise_and(frame, frame, mask=mask) # Only run in display
    else:
        visImg = frame # poseEstimation needs valid frame for camMatrix calcs        

    return (None, visImg)

def defaultAlgo(frame,display=0,debug=0):
    return realPNP(frame, display, debug)

def realPNP(frame, display, debug):
    # TODO: Remove debug from all function calls, and use logger.debug()
    # nb: caller is responsible for threading (see runPiCam.py)
    # Spew
    if debug:
        print("The frame type is: " + str(type(frame)))

    rects = rectUtil.findRects(frame,200,display,debug)

    if display:
        # combine original image with mask, for visualization
        visImg = cv2.bitwise_and(frame, frame, mask=mask) 
        for r in rects:
            pts = cv2.boxPoints(r)  # Turning the rect into 4 points to draw
            ipts = [np.int32(pts)]
            cv2.polylines(visImg, ipts, True, (255,0,0))
    else:
        # Avoid a NoneType error
        visImg = frame
        
    logging.debug("All valid rectangles are: " + str(rects))   

    success,leftPair,rightPair = rectUtil.pairRectangles(rects,debug=1)

    if success == False:
        # Logger debugs happened in pairRectangles
        return None, visImg

    elif leftPair != None:
        # XXX: No right pair support (yet)
        rleft = leftPair[0]
        rright = leftPair[1]
            
    rectPairs = (leftPair,rightPair)
    lTarget = None
    rTarget = None

    for pair in rectPairs:
        lPts = None
        rPts = None

        # Creating lists of points
        # Left points
        lPts = cv2.boxPoints(pair[0])
        lPts = np.int0(lPts)
        # Right points
        rPts = cv2.boxPoints(rright[0])
        rPts = np.int0(rPts)

        print("sending a point list of: " + str(rleftPts))
        orderedPoints = pnpSorting.sortPoints(rleftPts,rrightPts)
        print("Passing an orderedPoints of: " + str(orderedPoints))
            
        # now estimatePose accepts optional camera matrix
        target,frame = poseEstimation.estimatePose(visImg, orderedPoints,
                                            cameraMatrix=None, display=False)

        if not lTarget:
            lTarget = target
        else:
            rTarget = target

    return target,frame




