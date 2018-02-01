import numpy as np
import cv2
		# I only care about hightly saturated images150
range0 = np.array([25,220, 160]) # min hsv
range1 = np.array([40, 255, 255]) # max hsv
		  #THEOretical number is 30, but I'm compensating for the green light
def emptyAlgo(frame):
    return frame

def defaultAlgo(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(frame, range0, range1)

    # Return bitwise and 
    res = cv2.bitwise_and(frame, frame, mask=mask)
    # could employ erosion+dilation if noise presents a prob (aka MORPH_OPEN)
    im2, contours, hierarchy = cv2.findContours(mask,
                    cv2.RETR_EXTERNAL,  # external contours only
                    cv2.CHAIN_APPROX_TC89_KCOS # used by 254, cf:APPROX_SIMPLE
                        )
    
    for cnt in contours:

	epsilon = 0.1*cv2.arcLength(cnt,True)	

	approx = cv2.approxPolyDP(cnt,epsilon,True)

	rect = cv2.minAreaRect(approx)

	box = cv2.boxPoints(rect)

	box = np.int0(box)

	cv2.drawContours(res, [box], 0,(0,0,255),2)
	
    return res

    # filter/reduce contours
    # convert nominated contour to target
    return res

def processFrame(frame, algo=None):
    if algo == None or algo == "default":
        return defaultAlgo(frame)
    elif algo == "empty":
        return emptyAlgo(frame)
    
