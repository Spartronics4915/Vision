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
# Deprecated 2018 values:
# range0 = np.array([0,150,150]) # min hsv
# range1 = np.array([50, 255, 255]) # max hsv

range0 = np.array([10,50,200])
range1 = np.array([115,255,255])

# Reasoning behind Current range values:
    # After changes to exposure of camera (Ridiculously low ISO),
    # retro-reflective tape stands out more than it ever has,
    # thus, type of color, and the saturation of color has less importance,
    # which explains the wide range on the first two numbers. 10-115 represents an
    # (approximate) range of blue to green in the HSV colorspace
    # 50-255 represents a wide range of the saturation of any given color
    # (This value is fluid, as we arn't searching for any particular 'color',
    #  [read: 2018], it can be very open)
    # Finially, the tightest value needs to be the value, representing how close the color is to black.
    # We want colors as far away from black as possible, thus the high range.

def emptyAlgo(frame):
    return (0,frame)

def hsvAlgo(frame):
    return (0,cv2.cvtColor(frame, cv2.COLOR_BGR2HSV))  # HSV color space

def processFrame(frame, algo=None, display=0,debug=0):
    if algo == None or algo == "default":
        return defaultAlgo(frame, display, debug)
    elif algo == "rect":
        return rectAlgo(frame, display, debug)
    elif algo == "empty" or algo == "bypass":
        return emptyAlgo(frame)
    elif algo == "mask":
        return hsvAlgo(frame)
    elif algo == "hsv":
        return hsvAlgo(frame)
    else:
        print("algo: unexpected name " + algo)
        return emptyAlgo(frame)

def maskAlgo(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # HSV color space
    mask = cv2.inRange(frame, range0, range1)       # Our HSV filtering
    return 0, mask

def rectAlgo(frame,display=1,debug=0):
    # TODO: Implement some form of threading / process optimisation
    rects = []
    #largeTargetA = 0        # Need these vars to filter for large targets
    #largeTargetC = (1600,0)

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # HSV color space
    mask = cv2.inRange(frame, range0, range1)       # Our HSV filtering

    if display:
        # combine original image with mask, for visualization
        visImg = cv2.bitwise_and(frame, frame, mask=mask) # Only run in display
    else:
        visImg = None

    # could employ erosion+dilation if noise presents a prob (aka MORPH_OPEN)
    im2, contours, hierarchy = cv2.findContours(mask,
                    cv2.RETR_EXTERNAL,          # external contours only
                    cv2.CHAIN_APPROX_SIMPLE     # used by 254, cf:APPROX_SIMPLE
                                                # Less CPU intensive
                        )
    for cnt in contours:

        rect = cv2.minAreaRect(cnt) # Search for rectangles in the countour

        box = cv2.boxPoints(rect)  # Turning the rect into 4 points to draw
        box = np.int0(box)         # convert to integers

        if display:
            cv2.drawContours(visImg, [box], 0,(0,0,255),2)

    return (0, visImg)

def defaultAlgo(frame,display=0,debug=0):
    return realPNP(frame, display, debug)

# cribbed from team492
def getCorrectedAngle(sz, angle):
    if sz[0] < sz[1]:
        return angle + 180
    else:
        return angle + 90

def realPNP(frame, display, debug):
    # nb: caller is responsible for threading (see runPiCam.py)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # HSV color space
    mask = cv2.inRange(frame, range0, range1)       # Our HSV filtering
    if display:
        # combine original image with mask, for visualization
        visImg = cv2.bitwise_and(frame, frame, mask=mask) # Only run in display
    else:
        visImg = None
    # could employ erosion+dilation if noise presents a prob (aka MORPH_OPEN)
    im2, contours, hierarchy = cv2.findContours(mask,
                    cv2.RETR_EXTERNAL,          # external contours only
                    cv2.CHAIN_APPROX_SIMPLE     # used by 254, cf:APPROX_SIMPLE
                                                # Less CPU intensive
                        )
    # first convert contours to rects
    rects = []
    for cnt in contours:
        rects.append(cv2.minAreaRect(cnt))
        # a rect is ((cx,cy), (sx,sy), degrees)

    print("I see " + str(len(rects)) + " rects")
    if len(rects) < 6:
        print(" " + str(rects))
    if display: # draw boxes in blue
        for r in rects:
            pts = cv2.boxPoints(r)  # Turning the rect into 4 points to draw
            ipts = [np.int32(pts)]
            cv2.polylines(visImg, ipts, True, (255,0,0))

    # select two "opposing rects"
    rleft = None
    rright = None
    for r in rects:
        sz = r[1]
        area = sz[0] * sz[1]
        if area > 200:  # XXX: is this a good size contraint?
            angle = getCorrectedAngle(sz, r[2])
            if angle <= 90:
                if not rleft: # currently we do first-one-wins, (XXX: improve)
                    rleft = r
            else:
                if not rright: # currently we do first-one-wins, (XXX: improve)
                    rright = r

    if rleft != None and rright != None:
        orderedPoints = []  # build a list of 6 pairs (pts)
        boxPts = cv2.boxPoints(rleft) # an array of 4 pairs
        for i in range(0,3):
            orderedPoints.append(boxPts[i])
        boxPts = cv2.boxPoints(rright) # an array of 4 pairs
        for i in range(0,3):
            orderedPoints.append(boxPts[i])
        dx,dy,theta = poseEstimation.estimatePose(visImg, orderedPoints, 0)
        return (dx,dy,theta), visImg
    else:
        print("couldn't find two rects")
        return None, visImg


# ax = ax - 160           # center o' the screen being 0(-160-160)
# dx = ax * 0.1375        # See: LearningVision.md (-22-22)

'''
if boxArea > 1500:


            if display:  # No need to do this math and computation if we
                         # are not running in dispay mode
                cv2.drawContours(visImg, [box], 0,(0,0,255),2)


            if debug:   # This is helpful because I can glance at my computer,
                        # and see if it found a target or not.
                print("center is currently: %d, %d" %
                        (int(boxCenter[0]), int(boxCenter[1])))

            if boxArea > largeTargetA:
                largeTarget = box           # Set of poitns
                largeTargetA = boxArea     # Area of the box
                largeTargetC = boxCenter   # Center of the box (sent)

    ### DX math ###
    ax = largeTargetC[0]    # X value(0-320)
    ax = ax - 160           # center o' the screen being 0(-160-160)
    dx = ax * 0.1375        # See: LearningVision.md (-22-22)
'''
