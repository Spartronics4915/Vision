#! /usr/bin/python3

# Sepreate file to manage all mid-low level functions managing the targets
# Ideally, ALL functions accept a config, frame, and variables that are specific
# to that pipeline

# For short-ness purposes:
#       target = half-hexagon

# TODO: Integration Tests
# TODO: Take 
import numpy as np
import cv2
import logging
import math

def findTarget(frame, mask, cfg):
    """
    Given an imput image and the running configuration, find the 2020 target

    :param frame: frame from which the image points were captured
    :type frame: opencv frame (np.ndarray())

    :param mask: the mask generated from thresholding the input frame
    :type mask: opencv frame (np.ndarray()) (but in a strange colorspace, likely binary)

    :param cfg: Config representing our current run at the 'algo' level
    :type cfg: dict

    :return hexagonTarget: the verticies of the target not (yet) in any particular order
    :rtype: np.ndarray()

    Known inputs -> known outputs
    Currently no data frame support findtarget
    >>> import cv2, config
    >>> logging.info("-=  findTarget Doctest  =-")
    >>> cfg = config.default['algo']
    >>> cfg['display'] = True
    >>> frame = cv2.imread("data/pnpDebugFrame1.png",cv2.IMREAD_GRAYSCALE)
    >>> cv2.imshow("Read Frame",frame)
    >>> key = cv2.waitKey() # Good time to check if the read frame is proper
    >>> target, frame = findTarget(frame,frame, cfg)
    >>> logging.info("Points of the target: {}".format(target.tolist()))
    """
    # XXX: There is a difference between the return format for findContours between opencv v3 and v4
    #      v3 returns 3 items (img,cnts,hirearchy) where v4 only returns 2 items (img,cnts)(?) 
    _,cnts,_  = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    hexagonTarget = None
    for c in cnts:
        # Contour perimiter
        peri = cv2.arcLength(c, True)
        # approximating a shape around the contours
        # Can be tuned to allow/disallow hulls
        # Approx is the number of verticies
        # Ramer–Douglas–Peucker algorithm
        approx = cv2.approxPolyDP(c, 0.01 * peri, True)

        # logging.debug("Value of approxPolyDP: " + str(len(approx)))

        if len(approx) == 8:
            # Found a half-hexagon
            logging.debug("generatorHexagonVerticies found a half-hexagon")
            # Draw for visualization
            if cfg['display'] == 1:

                cv2.drawContours(frame, [c],-1,(0,255,255),1)
            area = cv2.moments(approx)

            if area['m00'] > 200:
                hexagonTarget = approx

    # TODO: Double check the useability of the frame
    # NOTE: The list retured here has three layers:
    #       1. Each point. [0] is first point, [len-1] is last point
    #       2. An Extra layer, only surrounding the point
    #           - The only object requrested form this layer should be [0]
    #       3. The final layer, representing the x and y value of each point
    # NOTE: target.tolist() is no longer an np.ndarray object, it becomes a python list (duh)
    return (hexagonTarget,frame)

def findTargetChameleon(frame, mask, cfg):
    """
    Given an imput image and the running configuration, find the 2020 target

    :param frame: frame from which the image points were captured
    :type frame: opencv frame (np.ndarray())

    :param mask: the mask generated from thresholding the input frame
    :type mask: opencv frame (np.ndarray()) (but in a strange colorspace, likely binary)

    :param cfg: Config representing our current run at the 'algo' level
    :type cfg: dict

    :return hexagonTarget: the verticies of the target not (yet) in any particular order
    :rtype: np.ndarray()

    Known inputs -> known outputs
    Currently no data frame support findtarget
    """
    _,cnts,_  = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)
    polyOut = []

    for c in cnts:

        convexHull = cv2.convexHull(c)

        polyOut.append(cv2.approxPolyDP(convexHull, 5, True))

        if cfg['display'] == 1:

            cv2.drawContours(frame, cv2.approxPolyDP(convexHull, 5, True),-1,(0,255,255),1)

    return  (None, frame)

def threshholdFrame(frame, cfg):
    """
    Seperate the 'threshholding' portion of a pipeline into its own function

    :param frame: frame from which the image points were captured
    :type frame: opencv frame (np.ndarray())

    :param cfg: Config representing our current run at the 'algo' level
    :type cfg: dict

    :return mask: the frame after threshholding
    :rtype: cv2 frame (np.ndarray())

    Very hard to doctest, none for now
    """
    # Blurs on the frame go in this method
    # Image which is operated upon
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Filter out the colors we don't need
    mask = cv2.inRange(frame, cfg["hsvRangeLow"], cfg["hsvRangeHigh"])

    # TODO: There's a bug encountered in picamstreamer
    #       where cv2.imencode fails on an empty image
    return mask

def target2pnpPoints(target, cfg):
    """
    Sort the target's points into a 'pnp format' as defined in poseEstimation.py

    :param target: the verticies of the target
    :type target: np.array()

    :param cfg: Config representing our current run at the 'algo' level
    :type cfg: dict

    :return targetPnPPoints: an array of target verticies in the agreed-upon 'pnp format'
    :rtype: np.array()

    >>> import config, cv2
    >>> logging.info("-=  target2pnpPoints Doctest  =-")
    >>> target = [[[460, 140]], [[445, 140]], [[392, 234]], [[291, 236]], [[243, 152]], [[231, 155]], [[284, 247]], [[399, 246]]]
    >>> cfg = config.default
    >>> target = target2pnpPoints(target, cfg)
    >>> logging.info("PnP Format: {}".format(target))
    >>> # logging.info("Points Sorted by Y: {}".format(ySorted))
    """
    # Create the empty points
    a = None
    b = None
    c = None
    d = None

    # low -> high
    # Sort points by x
    xSorted = sorted(target,key=lambda p:p[0][0])
    # Sort points by y
    ySorted = sorted(target,key=lambda p:p[0][1])

    # We know points a and d are the left-most and right-most points
    # In other words, the point with the smallest x and the largest x

    # Removes the middle '2nd layer' of the point
    a = xSorted[0][0]
    d = xSorted[len(xSorted)-1][0]

    # We know points b and c are the two bottom most points, or the two points with the largest y
    # Get the two bottom-most points
    botomMostPoints = (ySorted[len(ySorted)-1],ySorted[len(ySorted)-2])

    # Still haven't removed the 'middle layer'
    # low -> high
    bottomMostSortedX = sorted(botomMostPoints,key=lambda p:p[0][0])

    # Removes the middle layer
    b = bottomMostSortedX[0][0]
    c = bottomMostSortedX[1][0]

    # NOTE: PnP input points have to be float32/64
    return np.array([a,b,c,d],dtype="float32")
    # return targetPnPPoints

def target2pnp8Points(target, cfg):
    """
    Sort the target's points into a 'pnp format' as defined in poseEstimation.py

    :param target: the verticies of the target
    :type target: np.array()

    :param cfg: Config representing our current run at the 'algo' level
    :type cfg: dict

    :return targetPnPPoints: an array of target verticies for a pnp target with 8 points
    :rtype: np.array()
    >>> import config, cv2
    >>> logging.info("-=  taget2pnp8Points Doctest  =-")
    >>> target = [[[460, 140]], [[445, 140]], [[392, 234]], [[291, 236]], [[243, 152]], [[231, 155]], [[284, 247]], [[399, 246]]]
    >>> cfg = config.default
    >>> target = taget2pnp8Points(target, cfg)
    >>> logging.info("PnP Format: {}".format(target))
    >>> # logging.info("Points Sorted by Y: {}".format(ySorted)) 
    """
    # Create the empty points
    a,b,c,d = None,None,None,None 
    d,e,f,g = None,None,None,None

    # low -> high
    # Sort points by x
    xSorted = sorted(target,key=lambda p:p[0][0])
    # Sort points by y
    ySorted = sorted(target,key=lambda p:p[0][1])

    # We know points a and d are the left-most and right-most points
    # In other words, the point with the smallest x and the largest x

    # Likewise Logic for e and h

    # Removes the middle '2nd layer' of the point
    a = xSorted[0][0]
    h = xSorted[1][0]

    d = xSorted[len(xSorted)-1][0]
    e = xSorted[len(xSorted)-2][0]

    # We know points b and c are the two bottom most points, or the two points with the largest y
    # Get the two bottom-most points
    botomMostPoints = (ySorted[len(ySorted)-1],ySorted[len(ySorted)-2])

    midBottomMostPoints = (ySorted[len(ySorted)-3],ySorted[len(ySorted)-4])
    # Still haven't removed the 'middle layer'
    # low -> high
    bottomMostSortedX = sorted(botomMostPoints,key=lambda p:p[0][0])
    midBottomMostSortedX = sorted(midBottomMostPoints,key=lambda p:p[0][0])
    # Removes the middle layer
    b = bottomMostSortedX[0][0]
    c = bottomMostSortedX[1][0]

    g = midBottomMostSortedX[0][0]
    f = midBottomMostSortedX[1][0]

    # NOTE: PnP input points have to be float32/64
    return np.array([a,b,c,d,e,f,g,h],dtype="float32")
    # return targetPnPPoints

def estimatePosePNP(frame, cfg):
    """
    Blank function only used to doctest poseEstimaion

    :param frame: frame from which the image points were captured
    :type frame: opencv frame (np.ndarray())

    :param cfg: Config representing our current run at the 'algo' level
    :type cameraMatrix: dict

    :return : ???
    :rtype: ???

    Known inputs -> known outputs
    These points are based on test images
    >>> import cv2, config, poseEstimation
    >>> logging.info("-=  estimatePosePNP Doctest  =-")
    >>> cfg = config.default['algo']
    >>> cfg['display'] = True
    >>> frame = cv2.imread("data/pnpDebugFrame3.png",cv2.IMREAD_GRAYSCALE)

    >>> # cv2.imshow("Read Frame",frame)
    >>> # key = cv2.waitKey() # Good time to check if the read frame is proper

    >>> target, frame = findTarget(frame,frame, cfg)
    >>> pnpTarget = target2pnpPoints(target,cfg)
    >>> logging.info("{}".format(type(pnpTarget)))
    >>> xlate,rot,im = poseEstimation.estimatePose(frame,pnpTarget,cfg)
    >>> logging.info("Translate Vector: {}".format(xlate))
    
    >>> # cv2.imshow("Final", im) # Uncomment to see final frame
    >>> # key = cv2.waitkey()
    """
    pass

def getTargetCenter(target):
    # Takes the points of a target, and returns an approximation of where the (0,0) is
    #   in PnP coordinate space

    # Hacky, for now
    center = (target[0] + target[3])/2
    return center

def getYawError(frame, center):
    # TBD for closed-loop PID aiming
    yawOffset = (frame.size()[1]/2) / center
    return yawOffset

def pnpTransformRobotCoordinates(translation, cfg):
    # translation is a translation vector, cfg is the camera's angle in radians
    y = translation[1]
    z = translation[2]
    # Get the translation vector's y and z
    distance = math.sqrt(math.pow(y,2) + math.pow(z,2))
    # Find the distance between the target and the camera. X coordinates will not be affected by the rotation 
    thetaPrime = cfg["theta"] + math.atan2(y,z)
    # Find the angle between the ground and the target
    zPrime = distance * math.cos(thetaPrime)
    yPrime = distance * math.sin(thetaPrime)
    # Calculate the robot-relative y and z distance to the target using basic trigonometry
    return np.array([translation[0],yPrime,zPrime],dtype="float32")

if __name__ == "__main__":
    import doctest

    # We have to init logger
    logFmt = "%(name)-8s %(levelname)-6s %(message)s"
    dateFmt = "%H:%M"
    logging.basicConfig(level=logging.INFO,format=logFmt, datefmt=dateFmt)

    logging.info("Began logger")
    logging.info("openCV version: {}".format(cv2.__version__))

    # Run Doctests
    doctest.testmod()

'''
    leftMostVal = 100000
    rightMostVal = -10000
    returnedTarget = None
    offset = 0

    for c in cnts:
        #logging.debug("Contours of: " + str(c))

        # Contour perimiter
        peri = cv2.arcLength(c, True)

        # approximating a shape around the contours
        # Can be tuned to allow/disallow hulls
        # Approx is the number of verticies
        # Ramer–Douglas–Peucker algorithm
        approx = cv2.approxPolyDP(c, 0.01 * peri, True)

        # logging.debug("Value of approxPolyDP: " + str(len(approx)))

        if len(approx) == 8:
            # Found a half-hexagon
            logging.debug("generatorHexagonVerticies found a half-hexagon")
            if cfg['display'] == 1:

                cv2.drawContours(visImg, [c],-1,(0,0,255),1)

            # x 
            for c in approx:
                if c[0][0] < leftMostVal:
                    leftMostVal = c[0][0]

                # y
                if c[0][0] > rightMostVal:
                    rightMostVal = c[0][0]

            logging.debug("leftMostVal: " + str(leftMostVal))
            logging.debug("rightMostVal: " + str(rightMostVal))
            center = (leftMostVal + rightMostVal)/2

            offset = center/320
        # Only for debugging

'''
