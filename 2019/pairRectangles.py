#! /usr/bin/ python3

# TODO: Explain the problem in ASCI art 
# XXX: Returns a maximum of 2 pairs.
# Helpful link explaining how cv2 generates angles:
# https://namkeenman.wordpress.com/2015/12/18/open-cv-determine-angle-of-rotatedrect-minarearect/


def pairRectangles(rectArray,debug=0):   
    """
    Given an input of rectangles, classify them into pairs and return the pairs
 
    :param rectArray: array of rectangles detected in a frame
    :type rectArray: tuple or array
    :return: at a maximum, two valid pairs of rectangles
    :rtype: two tuples
    -----
    Doctest
    >>> pairRectangles([((20,5),(10,5),15),((40,5),(10,5), -15)])
    ([((40, 5), (10, 5), -15), ((20, 5), (10, 5), 15)], [])
    """
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

    # Iterating a over a range the size of the left rectangles
    # See: ASCI art
    for i in range(len(leftRects)):
        # If the next right rectangle is closer than the next left rectangle
 
        rightRectX = rightRects[i][0][0]
        leftRectX = leftRects[i][0][0]
        try:
            nextLeftRectX = leftRects[i+1][0][0]
        except:
            # XXX: Technical debt
            nextLeftRectX = -1000

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
        return None,None
    else:
        return pair1,pair2

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
    doctest.testmod()




'''
:raises ValueError: if the message_body exceeds 160 characters
:raises TypeError: if the message_body is not a basestring
'''