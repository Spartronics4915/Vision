#! /usr/bin/ python3

# TODO: Explain the problem in ASCI art 
# XXX: Returns a maximum of 2 pairs.
# Helpful link explaining how cv2 generates angles:
# https://namkeenman.wordpress.com/2015/12/18/open-cv-determine-angle-of-rotatedrect-minarearect/

# Philosophy:
# How should bad cases be handled?
#   I.E : When we don't get enough rects to generate a pair ; there isn't enough for a pair
# Current solutions
#     Ideal case (Input in the order of L, then R)
#    >>> pairRectangles([((20,5),(10,5),-89),((40,5),(10,5), -21)])
#    ([((40, 5), (10, 5), -15), ((20, 5), (10, 5), 15)], [])
def pairRectangles(rectArray,debug=0):   
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
    # Creating left-facing rectangles
    leftRects = list(filter(lambda r: getCorrectedAngle(r[0],r[2]) <= 90,rectArray))
    # Creating right-facing rectangles
    rightRects = list(filter(lambda r: getCorrectedAngle(r[0],r[2]) > 90,rectArray))

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

                else:
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

if __name__ == "__main__":
    import doctest
    import logging

    # Debug logging
    logFmt = "%(name)-8s %(levelname)-6s %(message)s"
    dateFmt = "%H:%M"
    logging.basicConfig(level=logging.DEBUG,format=logFmt, datefmt=dateFmt)

    logging.info("Began logger")

    doctest.testmod()




'''
Majority of old logic
    # Iterating a over a range the size of the left rectangles
    # See: ASCI art
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
'''
