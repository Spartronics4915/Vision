import numpy as np
import cv2
        # I only care about hightly saturated images150
range0 = np.array([25,220, 160]) # min hsv
range1 = np.array([40, 255, 255]) # max hsv

largeTargetC = [0,0]
          #THEOretical number is 30, but I'm compensating for the green light

#largeTargetC = (160,0)
# This is by design to keep a target in the works to transmit,
# Also needed for testPiCam to work properly
# TODO: Class
# TODO: Better Varible Names

def emptyAlgo(frame):
    return frame

def defaultAlgo(frame):
    num_squares = 0
    global largeTargetC
    largeTargetA = 0
    largeTargetC = (160,0)

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(frame, range0, range1)

    # Return bitwise and
    res = cv2.bitwise_and(frame, frame, mask=mask) # In the real world, this would never be run, because this is only for visual
    # could employ erosion+dilation if noise presents a prob (aka MORPH_OPEN)
    im2, contours, hierarchy = cv2.findContours(mask,
                    cv2.RETR_EXTERNAL,  # external contours only
                    cv2.CHAIN_APPROX_TC89_KCOS # used by 254, cf:APPROX_SIMPLE
                        )
    #Dimensions of the window, also deprecated
    rHeight, rWidth, chan = res.shape

    for cnt in contours:

    #epsilon = 0.1*cv2.arcLength(cnt,True)

    #approx = cv2.approxPolyDP(cnt,epsilon,True)

    rect = cv2.minAreaRect(cnt)

    box_h = rect[1][1]
    box_w = rect[1][0]
    box_center = rect[0]
    box_area = box_h*box_w
    box = cv2.boxPoints(rect)

    box = np.int0(box)

    #Filter by size
    if box_area > 3000:
        cv2.drawContours(res, [box], 0,(0,0,255),2)
        num_squares += 1 

#       print("area is currently:",int(box_area))
        print("center is currently:", int(box_center[0]),int(box_center[1]))        
        #print("The screen is:",rWidth,rHeight)

        if box_area > largeTargetA:
            largeTarget = box #set of poitns
            largeTargetA = box_area #Area of the box
            largeTargetC = box_center #Center of the box(what is transmitted)
            print("largeTargetC @:", largeTargetC)
            print(largeTargetC)

    ### DX math ###
    ax = largeTargetC[0] #X value(0-320)
    #print("largeTargetC(0) @:", largeTargetC[0])
    ax = ax - 160 #Converting to the center o' the screen being 0(-160-160)
    dx = ax * 0.1375 # See: LearningVision.md (-22-22)


    #print(num_squares) Leaving commented untill integration with debug mode
    return res, dx

#Deprecated
def getTargetY():
    return largeTargetC[1]

def processFrame(frame, algo=None):
    if algo == None or algo == "default":
        return defaultAlgo(frame)
    elif algo == "empty":
        return emptyAlgo(frame)
    
