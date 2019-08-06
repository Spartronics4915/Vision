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

def emptyAlgo(frame,cfg):
    return (None,frame)

def hsvAlgo(frame,cfg):
    return (None,cv2.cvtColor(frame, cv2.COLOR_BGR2HSV))  # HSV color space

def processFrame(frame, algo=None, cfg=None, display=0, debug=0):
    if algo == None or algo == "default":
        return defaultAlgo(frame, cfg, display, debug)
    elif algo == "rect":
        return rectDebugAlgo(frame, cfg, display, debug)
    elif algo == "empty" or algo == "bypass":
        return emptyAlgo(frame, cfg)
    elif algo == "mask":
        return maskAlgo(frame, cfg)
    elif algo == "realPNP":
        return realPNP(frame, cfg, display, debug)
    elif algo == "heading":
        return headingAlgo(frame,cfg, display, debug)
    elif algo == "hsv":
        return hsvAlgo(frame, cfg)
    else:
        logging.info("algo: unexpected name " + algo + " running default")
        return defaultAlgo(frame, cfg, display, debug)

def defaultAlgo(frame, cfg, display=0, debug=0):
    return realPNP(frame, cfg, display, debug)

def maskAlgo(frame, cfg):
    # Show what is shown by the opencv HSV values
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(frame, cfg["hsvRange0"], cfg["hsvRange1"])
    return None,mask

def rectDebugAlgo(frame, cfg, display=1, debug=0):
    # Used to find all relevent imformation about rectangles on screen
    logging.warning("running rectDebugAlgo on frame, not hsv")
    mask = cv2.inRange(frame, cfg["hsvRange0"], cfg["hsvRange1"]) # Our HSV filtering
    rects = rectUtil.findRects(frame, 200, cfg, display, debug)

    if display:
        visImg = cv2.bitwise_and(frame, frame, mask=mask) # Only run in display
        # Draw each rect + properties of it
        for r in rects:
            # combine original image with mask, for visualization

            pts = cv2.boxPoints(r)  # Turning the rect into 4 points to draw
            boxPts = [np.int32(pts)]

            # Draw the box
            cv2.drawContours(visImg,boxPts, 0,(0,0,255),2)
            # Draw a line through the center of the rect
            #cv2.line(visImg,(frame.shape[1],r[0][1],(0,r[0][1]),(0,255,0)))
            # Draw a line between Two points in the rectangle
            #cv2.line(visImg,boxPts[1],boxPts[2],(0,255,0))

            # Draw each point
            i = 0
            for p in boxPts:
                # cv2.circle(visImg,p,5,(0,255,0))
                print("At index " + str(i) + str(p))

    else:
        visImg = frame

    return None,visImg

def headingAlgo(frame, cfg, display, debug):
    # Intrestingly, with this algo, it also requires proper different 
    #  configs in runPiCam (lower res)
    rects = rectUtil.findRects(frame, 200, cfg, display, debug)
    success,leftPair,rightPair = rectUtil.pairRectangles(rects, wantedTargets=1,
                                                         debug=debug)

    # For simplicity, we are only thinking about one target
    if leftPair:

        lRect = leftPair[0]
        rRect = leftPair[1]
        if lRect:
            lPts = cv2.boxPoints(lRect)
            lPts = np.int0(lPts)
        if rRect:
            rPts = cv2.boxPoints(rRect)
            rPts = np.int0(rPts)

        PnpPts = rectUtil.sortPoints2PNP(lPts,rPts)

        targetCenter = rectUtil.points2center(PnpPts)

        angleOffset = rectUtil.computeTargetAngleOffSet(frame,targetCenter)

        # Getting average height offset (between the two rectangles in a target)
        targetAvgHeight = (rectUtil.getRectHeight(lRect) + rectUtil.getRectHeight(rRect)) / 2

        heightError = rectUtil.computeHeightError(targetAvgHeight)

        if (display):
            # frame.size is in the form (y,x,channel)
            cv2.line(frame,(int(targetCenter[0]),0),(int(targetCenter[0]),frame.size[0]), (255,255,255), 3) 

        # tgval = rectUtil.computeTargetOffsetAndHeightErrors(lPts,rPts)
        return targets.TargetHeadingsAndHeightOffset(angleOffset,heightError),frame

    else:
        return None, frame


def realPNP(frame, cfg, display, debug):
    # TODO: Remove debug from all function calls, and use logger.debug()
    # nb: caller is responsible for threading (see runPiCam.py)
    # Spew
    #logging.debug("The frame type is: " + str(type(frame)))

    rects = rectUtil.findRects(frame, 200, cfg, display, debug)
    if display:
        # combine original image with mask, for visualization
        mask = cv2.inRange(frame, cfg["hsvRange0"], cfg["hsvRange1"])     # Our HSV filtering
        visImg = cv2.bitwise_and(frame, frame, mask=mask)
        for r in rects:
            pts = cv2.boxPoints(r)  # Turning the rect into 4 points to draw
            ipts = [np.int32(pts)]
            cv2.polylines(visImg, ipts, True, (0,255,0))
    else:
        # Avoid a NoneType error
        visImg = frame

    if logging.getLogger().getEffectiveLevel() <= logging.DEBUG:
        print("%d rects: %s" % (len(rects), rectUtil.prettyRects(rects)), end="\r")

    # Leftpair is allways leftmost
    # XXX: rightPair is not always the rightmost
    success,leftPair,rightPair = rectUtil.pairRectangles(rects,wantedTargets=2,debug=1)

    if success == False:
        # Logger debugs happened in pairRectangles
        return None, visImg

    rectPairs = (leftPair,rightPair)

    # TODO: support for infinite targets
    lTarget = None
    rTarget = None

    for pair in rectPairs:

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

        if False:
            logging.debug("sending a left point list of: " + str(lPts))
            logging.debug("sending a right point list of: " + str(rPts))

        # Orders the points according to modelpoints in solvePNP()
        orderedPoints = rectUtil.sortPoints2PNP(lPts,rPts)

        if False:
            logging.debug("Passing an orderedPoints of: " + str(orderedPoints))

        # now estimatePose accepts optional camera matrix
        target,frame = poseEstimation.estimatePose(visImg, orderedPoints, cfg,
                                            cameraMatrix=None, display=display)

        if not lTarget:
            lTarget = target
        else:
            rTarget = target

    return targets.TargetPNP(lTarget,rTarget),frame




