#! /usr/bin/ python3

# Sorting openCV points to be in the proper orientation for solvePNP
import numpy as np

def sortPoints(leftPoints, rightPoints,debug=1):
    # XXX: change defualt debug value
    if debug:
        print("Received a leftPoints of: " + str(leftPoints))
        print("Received a rightPoints of:" + str(rightPoints))
        print("Type of the points is: " + str(type(leftPoints[0])))
        print("A sample point is: " + str(leftPoints[0]))
        print("A sample value is: " + str(type(leftPoints[0][0])))
    """
    Doctest logic
    >>> sortPoints([(2,1),(2,4),(1,3),(3,2)],[(7,1),(8,3),(6,2),(7,4)])
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

    print("Sorting points by x, with the leftmost first")

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

if __name__ == "__main__":
    import doctest
    doctest.testmod()
