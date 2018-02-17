import numpy as np
import cv2
        # I only care about hightly saturated images150
range0 = np.array([30,120, 100]) # min hsv
range1 = np.array([50, 255, 255]) # max hsv

largeTargetC = [0,0]
          #THEOretical number is 30, but I'm compensating for the green light

#largeTargetC = (160,0)
# This is by design to keep a target in the works to transmit,
# Also needed for testPiCam to work properly
# TODO: Class
# TODO: Better Varible Names

def emptyAlgo(frame):
    return frame

def defaultAlgo(frame,display=0,debug=0):
    largeTargetA = 0        # Need these vars to filter for large targets
    largeTargetC = (160,0)

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # HSV color space
    mask = cv2.inRange(frame, range0, range1)       # Our HSV filtering

    # Return bitwise and
    if display:
        res = cv2.bitwise_and(frame, frame, mask=mask) # Only run in display

    # could employ erosion+dilation if noise presents a prob (aka MORPH_OPEN)
    im2, contours, hierarchy = cv2.findContours(mask,
                    cv2.RETR_EXTERNAL,          # external contours only
                    cv2.CHAIN_APPROX_TC89_KCOS  # used by 254, cf:APPROX_SIMPLE
                        )

    for cnt in contours:

    # Perhaps contour approxomation?

        rect = cv2.minAreaRect(cnt)

        box_h = rect[1][1]          # Width of the box
        box_w = rect[1][0]          # Height of the box
        box_center = rect[0]        # (x,y) center of the box
        box_area = box_h*box_w      # Area of the box
        box = cv2.boxPoints(rect)   # Turning the rect into 4 points to draw

        box = np.int0(box)

        # Filter by size
        if box_area > 3000:

            if display:  # No need to do this math and computation if we are not running in dispay mode
                cv2.drawContours(res, [box], 0,(0,0,255),2)

            if debug:   # This is helpful because I can glance at my computer, and see if it found a target or not.
                print("center is currently:", int(box_center[0]),int(box_center[1]))   

            if box_area > largeTargetA:
                largeTarget = box           # Set of poitns
                largeTargetA = box_area     # Area of the box
                largeTargetC = box_center   # Center of the box(what is transmitted)

    ### DX math ###
    ax = largeTargetC[0]    # X value(0-320)

    ax = ax - 160           # Converting to the center o' the screen being 0(-160-160)
    dx = ax * 0.1375        # See: LearningVision.md (-22-22)

    if debug:
        print("dx is at: ", dx)

    if display:
        return dx, res
    else:
        return dx, 0    # This is to make shure that anyone asking for two values allways get them.
                        # I am unshure if asking for two values and only giving one produces a syntax error

def processFrame(frame, algo=None, display=0,debug=0):
    if algo == None or algo == "default":
        return defaultAlgo(frame,display,debug)
    elif algo == "empty":
        return emptyAlgo(frame)
    
