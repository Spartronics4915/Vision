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

TARGETCENTER = (200,200)

def checkCenter(point,currentCenter):
    # XXX: Improve varible names
    deltaPoint = (point[0]-TARGETCENTER[0],point[1]-TARGETCENTER[1])
    currentDelta = (currentCenter[0]-TARGETCENTER[0],currentCenter[1]-TARGETCENTER[1])

    # Distance formula
    currentDeltaDist = (currentDelta[0]**2 + currentDelta[1]**2)**.5
    checkDeltaDist = (deltaPoint[0]**2 + deltaPoint[1]**2)**.5

    if checkDeltaDist < currentDeltaDist:
        return True
    else:
        return False

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
    # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # HSV color space
    mask = cv2.inRange(frame, np.array([225,225,225]), np.array([255,255,255]))       # Our HSV filtering
    return None,mask

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
        visImg = frame # poseEstimation needs valid frame for camMatrix calcs

    # could employ erosion+dilation if noise presents a prob (aka MORPH_OPEN)
    im2, contours, hierarchy = cv2.findContours(mask,
                    cv2.RETR_EXTERNAL,          # external contours only
                    cv2.CHAIN_APPROX_SIMPLE     # used by 254, cf:APPROX_SIMPLE
                                                # Less CPU intensive
                        )
    for cnt in contours:
        rect = cv2.minAreaRect(cnt) # Search for rectangles in the countour

        box = cv2.boxPoints(rect)  # Turning the rect into 4 points to draw
        box = np.int0(box)

        # print(type(box.astype(np.uint8)[0][0]))
        if display:
            cv2.drawContours(visImg, [box], 0,(0,0,255),2)

    return (None, visImg)

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
    startAlgo = time.time()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # HSV color space
    mask = cv2.inRange(frame, range0, range1)       # Our HSV filtering
    if display:
        # combine original image with mask, for visualization
        visImg = cv2.bitwise_and(frame, frame, mask=mask) # Only run in display
    else:
        visImg = frame
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
    centerR = (0,0)
    centerL = (0,0)
    for r in rects:
        sz = r[1]
        area = sz[0] * sz[1]
        if area > 200:  # XXX: is this a good size contraint?
            center = r[0]
            angle = getCorrectedAngle(sz, r[2])
            # Sorting by center
            # For every left rectangle
            if angle <= 90:
                if checkCenter(center,centerR):
                    rleft = r
                    centerR = center
                # if not rleft: # currently we do first-one-wins, (XXX: improve)
                #     rleft = r
            else:
                if checkCenter(center,centerL):
                    rright = r
                    centerL = center
                # if not rright: # currently we do first-one-wins, (XXX: improve)
                #     rright = r

    if rleft != None and rright != None:
        # orderedPoints = []  # build a list of 6 pairs (pts)
        # boxPts = cv2.boxPoints(rleft) # an array of 4 pairs
        # for i in range(0,3):
        #     orderedPoints.append(boxPts[i])
        # boxPts = cv2.boxPoints(rright) # an array of 4 pairs
        # for i in range(0,3):
        #     orderedPoints.append(boxPts[i])
        rleftPts = cv2.boxPoints(rleft)
        rrightPts = cv2.boxPoints(rright)
        rleftPts = np.int0(rleftPts)
        rrightPts = np.int0(rrightPts)

        print("sending a point list of: " + str(rleftPts))
        orderedPoints = pnpSorting.sortPoints(rleftPts,rrightPts)
        print("Passing an orderedPoints of: " + str(orderedPoints))

        # TODO: change hardcoded focalLength
        # focalLen was 306.3829787
        # now estimatePose accepts optional camera matrix
        value,frame = poseEstimation.estimatePose(visImg, orderedPoints,
                                            cameraMatrix=None, display=False)

        endAlgo = time.time()
        deltaTime = startAlgo - endAlgo
        
        print("A succcessful run of pnp algo took(sec): "+str(deltaTime))
        return value,frame
    else:
        print("couldn't find two rects")
        return None,frame


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

'''
        box_index = 0
        for point in box:
            foo = []
            foo.append(point[0])
            foo.append(point[1])
            bar = (foo[0],foo[1])
            cv2.putText(visImg,str(box_index),bar,cv2.FONT_HERSHEY_SIMPLEX,2,255)
            box_index += 1
        '''

