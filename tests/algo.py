import numpy as np
import cv2

range0 = np.array([40, 100, 30]) # min hsv
range1 = np.array([80, 255, 255]) # max hsv

def emptyAlgo(frame):
    return frame

def defaultAlgo(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(frame, range0, range1)
    # could employ erosion+dilation if noise presents a prob (aka MORPH_OPEN)
    contours = cv2.findContours(mask,
                    cv2.RETR_EXTERNAL,  # external contours only
                    cv2.CHAIN_APPROX_TC89_KCOS # used by 254, cf:APPROX_SIMPLE
                        )
    # filter/reduce contours
    # convert nominated contour to target
    return mask

def processFrame(frame, algo=None):
    if algo == None or algo == "default":
        return defaultAlgo(frame)
    elif algo == "empty":
        return emptyAlgo(frame)
    
