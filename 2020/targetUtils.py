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

def findTarget(frame, cfg):
    """
    Given an imput image and the running configuration, find the 2020 target

    :param frame: frame from which the image points were captured
    :type frame: opencv frame (np.ndarray())

    :param cfg: Config representing our current run at the 'algo' level
    :type cfg: dict

    :return : ???
    :rtype: ???

    Known inputs -> known outputs
    Currently no data frame support findtarget
    >>> import cv2, config
    >>> cfg = config.default['algo']
    >>> cfg['display'] = True
    >>> frame = cv2.imread("data/pnpDebugFrame1.png",cv2.IMREAD_GRAYSCALE)
    >>> cv2.imshow("Read Frame",frame)
    >>> key = cv2.waitKey() # Good time to check if the read frame is proper
    >>> target, frame = findTarget(frame, cfg)
    >>> logging.info("Points of the target: {}".format(target.tolist()))
    """
    # TODO: Double check the version of cv2 and the number of returned items for findContours
    #       Newer version only returns 2?
    cnts,_  = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

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
            
            hexagonTarget = approx

    # NOTE: Double check the useability of the frame
    # NOTE: The list retured here has three layers:
    #       1. Each point. [0] is first point, [len-1] is last point
    #       2. An Extra layer 
    return (hexagonTarget,frame)

def threshholdFrame(frame, cfg):
    """
    Seperate the 'threshholding' portion of a pipeline into its own function

    :param frame: frame from which the image points were captured
    :type frame: opencv frame (np.ndarray())

    :param cfg: Config representing our current run at the 'algo' level
    :type cfg: dict

    :return : mask, after threshholding
    :rtype: cv2 frame (np.ndarray())

    Very hard to doctest, none for now
    >>> pass
    """
    # Blurs on the frame go in this method
    # Image which is operated upon
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Filter out the colors we don't need
    mask = cv2.inRange(frame, cfg["hsvRangeLow"], cfg["hsvRangeHigh"])

    # TODO: There's a bug encountered in picamstreamer
    #       where cv2.imencode fails on an empty image
    if cfg['display'] == 1:
        mask = cv2.bitwise_and(frame, frame, mask=mask)

    return mask

def estimatePosePNP(frame, cfg):
    """
    implements estimatePose() from poseEstimation.py

    :param im: frame from which the image points were captured
    :type im: opencv frame (np.ndarray())

    :param cfg: Config representing our current run at the 'algo' level
    :type cameraMatrix: dict

    :return : ???
    :rtype: ???

    Known inputs -> known outputs
    These points are based on test images
    >>> 
    """
    pass

def getTargetCenter(frame, cfg):
    pass


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