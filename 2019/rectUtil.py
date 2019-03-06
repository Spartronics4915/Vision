#! /usr/bin/ python3

# TODO: Explain the problem in ASCI art 
# XXX: Returns a maximum of 2 pairs.
# Helpful link explaining how cv2 generates angles:
# https://namkeenman.wordpress.com/2015/12/18/open-cv-determine-angle-of-rotatedrect-minarearect/
import numpy as np
import cv2
import logging

# Philosophy:
# How should bad cases be handled?
#   I.E : When we don't get enough rects to generate a pair ; there isn't enough for a pair
# Current solutions
#     Ideal case (Input in the order of L, then R)
#    >>> pairRectangles([((20,5),(10,5),-89),((40,5),(10,5), -21)])
#    ([((40, 5), (10, 5), -15), ((20, 5), (10, 5), 15)], [])

# Rects are returned in the form:
#  ((cx,cy), (sx,sy), degrees)


# XXX: In a perfect world, this should only be across one file
range0 = np.array([30,150,170])
range1 = np.array([90,255,255])

RPICAMFOV = 45  # Working deg offset for 2018
                # nb: This is different than the noted fov in the rpicam spec sheet


def findRects(frame,minsize,display=0,debug=0):
    # TODO: minsize as a arg for runPiCam.py
    """
    Derive a list of rects from a frame
 
    :param frame: image to scan for rectangles
    :type frame: raw opencv captured frame (no HSV or mask nessissary)

    :param minsize: minimum size of the rectangles (Used for filtering)
    :type minsize: int

    :param display: Chose weather or not to draw rects on frame
    :type display: bool

    :param debug: logger.debug() prints 
    :type debug: bool

    :return: rectangles detected in the frame
    :rtype: array
    """
    rects = []
    sizedRects = []

    # OpenCV Values
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

        rects.append(rect)

    for r in rects:
        sz = r[1]
        area = sz[0] * sz[1]
        if area > 200:
            sizedRects.append(r)

    return sizedRects

def pairRectangles(rectArray,wantedTargets=1,debug=0):   
    """
    Given an input of rectangles, classify them into pairs and return the pairs
 
    :param rectArray: array of rectangles detected in a frame
    :type rectArray: tuple or array
    :return: at a maximum, two valid pairs of rectangles
    :rtype: two tuples
    -----
    Doctest

    Case B
    >>> pairRectangles([((544.0203857421875, 256.99468994140625), (29.743717193603516, 83.71994018554688), -14.620874404907227),((376.6615295410156, 250.90771484375), (81.04014587402344, 30.872438430786133), -74.74488067626953),((221.1119842529297, 246.6160125732422), (30.231643676757812, 80.67733764648438), -10.304845809936523),((61.249996185302734, 241.25003051757812), (81.27052307128906, 28.460494995117188), -71.56504821777344)])
    (True, [((61.249996185302734, 241.25003051757812), (81.27052307128906, 28.460494995117188), -71.56504821777344), ((221.1119842529297, 246.6160125732422), (30.231643676757812, 80.67733764648438), -10.304845809936523)], [((376.6615295410156, 250.90771484375), (81.04014587402344, 30.872438430786133), -74.74488067626953), ((544.0203857421875, 256.99468994140625), (29.743717193603516, 83.71994018554688), -14.620874404907227)])   
    
    Misorienting Case B (Same expected outcome)
    >>> pairRectangles([((376.6615295410156, 250.90771484375), (81.04014587402344, 30.872438430786133), -74.74488067626953),((544.0203857421875, 256.99468994140625), (29.743717193603516, 83.71994018554688), -14.620874404907227),((61.249996185302734, 241.25003051757812), (81.27052307128906, 28.460494995117188), -71.56504821777344),((221.1119842529297, 246.6160125732422), (30.231643676757812, 80.67733764648438), -10.304845809936523)])
    (True, [((61.249996185302734, 241.25003051757812), (81.27052307128906, 28.460494995117188), -71.56504821777344), ((221.1119842529297, 246.6160125732422), (30.231643676757812, 80.67733764648438), -10.304845809936523)], [((376.6615295410156, 250.90771484375), (81.04014587402344, 30.872438430786133), -74.74488067626953), ((544.0203857421875, 256.99468994140625), (29.743717193603516, 83.71994018554688), -14.620874404907227)])   

    Case E - Rightmost (Testing only two rect input)
    >>> pairRectangles([((279.47998046875, 259.8599853515625), (38.325191497802734, 73.11483764648438), -8.130102157592773),((87.36154174804688, 256.3923645019531), (92.26648712158203, 32.100318908691406), -52.12501525878906)])
    (True, [(279.47998046875, 259.8599853515625), (38.325191497802734, 73.11483764648438), -8.130102157592773),((87.36154174804688, 256.3923645019531), (92.26648712158203, 32.100318908691406), -52.12501525878906)],[])
    
    One-Rect Case 
    >>> pairRectangles([((279.47998046875, 259.8599853515625), (38.325191497802734, 73.11483764648438), -8.130102157592773)])
    (False, [], [])
    """

    # nb:
    # Currently the one-list method is implemented 
    # A one-list iteration L-R pattern method can be implemtned

    # For readability; define the two pairs
    # XXX: return pairs based on a property? (size, best estimate?)
    pair1 = []
    pair2 = []

    # Sorted() defaults to low-high
    # Sorting the rectangles by X
    xSortedRects = sorted(rectArray,key=lambda r:r[0][0])

    # Check for size of xsorted rects
    if len(xSortedRects) < 2:
        logging.debug("Not enough rects to generate a pair")    
        return False,pair1,pair2

    # Doing this by index allows us to access the next rect in the list
    for i in range(len(xSortedRects)):
        # check for end (True, [((61.249996185302734, 241.25003051757812), (81.27052307128906, 28.460494995117188), -71.56504821777344), ((221.1119842529297, 246.6160125732422), (30.231643676757812, 80.67733764648438), -10.304845809936523)], [((376.6615295410156, 250.90771484375), (81.04014587402344, 30.872438430786133), -74.74488067626953), ((544.0203857421875, 256.99468994140625), (29.743717193603516, 83.71994018554688), -14.620874404907227)])of list
        # This will ensure we don't get a list index error
        if i == len(xSortedRects) - 1:
            break
        # If left rectangle
        if getCorrectedAngle(xSortedRects[i][1],xSortedRects[i][2]) <= 90:
            # If the next rectangle is right
            logging.debug("Found a left rectangle at index " + str(i))
            logging.debug("The rectangle at that index has an angle of: " + str(getCorrectedAngle(xSortedRects[i][0],xSortedRects[i][2])))
            logging.debug("The following rectangle has an angle of: " + str(getCorrectedAngle(xSortedRects[i+1][0],xSortedRects[i+1][2])))

            if getCorrectedAngle(xSortedRects[i+1][1],xSortedRects[i+1][2]) > 90:
                logging.debug("Found a valid rectangle pair at index: " + str(i) + "\n")
                
                if not pair1:
                    pair1.append(xSortedRects[i])
                    pair1.append(xSortedRects[i+1])

                elif wantedTargets == 2:
                    # TODO: Add infinate support for as many targets as we want
                    # Currently only supports a wantedTargets of 1 and 2
                    pair2.append(xSortedRects[i])
                    pair2.append(xSortedRects[i+1])

            # Slap down a debug message
            else:
                logging.debug("The rect following the left rect at index " + str(i) + " is not a right rect")
        # If right rectangle
        else:
            # XXX: Do something?
            
            continue

    # Check the validity of pair1 and pair2
    if not pair1:
        # We know pair2 is going to be blank
        return False,pair1,pair2
    elif pair1 != None:
        # XXX: True may be returned even if pair2 is an empty array
        logging.debug("Pair1: " + str(pair1))
        logging.debug("Pair2: " + str(pair2))
        return True,pair1,pair2

def pairRectanglesLambda(rectArray,debug=0):
    # 2nd method of sorting, commited for record, not for use
    pair1 = None
    pair2 = None
    xSortedRects = sorted(rectArray,key=lambda r:r[0][0])

    # Creating left-facing rectangles
    leftRects = list(filter(lambda r: getCorrectedAngle(r[0],r[2]) <= 90,rectArray))
    # Creating right-facing rectangles
    rightRects = list(filter(lambda r: getCorrectedAngle(r[0],r[2]) > 90,rectArray))
 
    # Iterating a over a range the size of the left rectangles
    # See: ASCI art in poseEstimation.py

    # len() returns how many elements are in a list
    if (len(leftRects) < 0) or (len(rightRects) < 0):
        # XXX: Begin to transfer prints to logger
        print("Not enough valid L and R rects")
        return False,None,None


    for i in range(len(leftRects)):
        print("Length of leftRects is: " + str(len(leftRects)))
        print("Length of rightRects is: " + str(len(rightRects)))
        print("Trying to access index: ",str(i))
        # If the next right rectangle is closer than the next left rectangle
        
        rightRectX = rightRects[i][0][0]
        leftRectX = leftRects[i][0][0]

        try:
            nextLeftRectX = leftRects[i+1][0][0]
        except:
            # XXX: Technical debt
            nextLeftRectX = -1000

        # If the next right rect is closer than the next left rect
        if (rightRectX - leftRectX) < (leftRectX - nextLeftRectX):
            # If pair1 is empty
            if not pair1:
                pair1.append(leftRects[i])
                pair1.append(rightRects[i])
            else:
                pair2.append(leftRects[i])
                pair2.append(rightRects[i])

    if not pair1:
        print("Could not find a valid pair")
        return False,None,None
    else:
        return True,pair1,pair2

# XXX: Should be a cleaner way of sharing this across files
def getCorrectedAngle(sz, angle):
    """
    Corrects an angle returned by minAreaRect()
 
    :param sz: Width x height of rectangle
    :param angle: Angle of rectangle 
    :type sz: Tuple of np.int0
    :type angle: np.int0
    :return: the corrected angle
    :rtype: np.int0
    -----
    """
    if sz[0] < sz[1]:
        return angle + 180
    else:
        return angle + 90

def checkCenter(point,currentCenter):
    # Depricated from old algo.py logic
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

def sortPoints2PNP(leftPoints, rightPoints):
    # XXX: change defualt debug value
    logging.debug("Received a leftPoints of: " + str(leftPoints))
    logging.debug("Received a rightPoints of:" + str(rightPoints))
    logging.debug("Type of the points is: " + str(type(leftPoints[0])))
    logging.debug("A sample point is: " + str(leftPoints[0]))
    logging.debug("A sample value is: " + str(type(leftPoints[0][0])))
    """
    Doctest logic
    >>> sortPoints2PNP([(2,1),(2,4),(1,3),(3,2)],[(7,1),(8,3),(6,2),(7,4)])
    [(2, 1), (3, 2), (2, 4), (6, 2), (7, 1), (7, 4)]
    """
    orderedPoints = []
    leftSorted = sorted(leftPoints,key=lambda p:p[1])
    rightSorted = sorted(rightPoints,key=lambda p:p[1])
    # Now we have a list of points, sorted by y
    topLPair = [leftSorted[0],leftSorted[1]]
    botLPair = [leftSorted[2],leftSorted[3]]
    # We now have the L points clumped by pair
    topRPair = [rightSorted[0],rightSorted[1]]
    botRPair = [rightSorted[2],rightSorted[3]]
    # We now have the R points clumped by pair

    logging.debug("Sorting points by x, with the leftmost first")

    # Sorting by x, with smallest x first
    topLPair = sorted(topLPair,key=lambda p:p[0])
    botLPair = sorted(botLPair,key=lambda p:p[0])

    topRPair = sorted(topRPair,key=lambda p:p[0])
    botRPair = sorted(botRPair,key=lambda p:p[0])

    # Appending proper points
    ### LEFT RECT ###
    # Top-left 
    orderedPoints.append(topLPair[0])
    # Top-right
    orderedPoints.append(topLPair[1])
    # Bot-right
    orderedPoints.append(botLPair[1])
    ### RIGHT RECT ###
    # Top-left
    orderedPoints.append(topRPair[0])
    # Top-right
    orderedPoints.append(topRPair[1])
    # Bot-left
    orderedPoints.append(botRPair[0])

    return np.array(orderedPoints,dtype="double")

def computeTargetOffSet(frame,center):
    # Only need the center of the target for this caluclation, not all points  
    # TODO: Phoenix documentation
    y,x,_ = frame.shape

    pixelToDegRatio = x / RPICAMFOV

    centerX = center[0]

    if centerX < x/2:
        # Left side of screen 
        centerDegOffset = -(centerX / pixelToDegRatio)

    elif centerX > x/2:
        # Right side of screen
        centerDegOffset = (centerX - x/2) / pixelToDegRatio 

    return centerDegOffset


def computeHeightError(lPts,rPts):
    # numpy.array([(a), (b), (c), (f), (e), (g)]), dtype="double") 
    # TODO: Phoenix documentation

    

    return None

def points2center(points):
    # Given a target in PNP format, return the center
    # XXX: Does not work as intended with rotated targets
    # TODO: Phoenix documentation

    lTopRightPt = points[1] # According to PNP order

    rTopLeftPt =  points[3]

    # How far apart those points are
    # Center is top left
    xDelta = lTopRightPt[0] - rTopLeftPt[0]
    '''
    Center art:
                   xDelta
                <--------->
        A-------B    X    F-------E
                |         |
                |         |
                |         |
                |         |
                C         G

    '''
    center = (lTopRightPt+xDelta/2,lTopRightPt[1])

    return center

def getRectHeight(rect):
    # Get the height from the topmost point to the bottommost point
    '''
    Doctest
    >>> getRectHeight(((544.0203857421875, 256.99468994140625), (29.743717193603516, 83.71994018554688), -14.620874404907227))
    
    '''
    pts = cv2.boxPoints(rect)
    boxPts = np.int32(pts)

    # Of points    
    boxPts = boxPts.tolist()

    # Lambda sorting does NOT work with a numpy array (properly)
    boxPtsSorted = sorted(boxPts,key=lambda p:p[1]) # Sort points by y

    # for point in boxPtsSorted:
    #     # Fixing numpy appending of objects
    #     point = point.tolist()
    #     orderedPoints.append(point)

    logging.debug(boxPtsSorted)
    # Widest Y
    height = boxPtsSorted[3] - boxPtsSorted[0]

    return height




    

if __name__ == "__main__":
    import doctest

    # Debug logging
    logFmt = "%(name)-8s %(levelname)-6s %(message)s"
    dateFmt = "%H:%M"
    logging.basicConfig(level=logging.DEBUG,format=logFmt, datefmt=dateFmt)

    logging.info("Began logger")

    doctest.testmod()