#!/usr/bin/env python3
#   https://www.learnopencv.com/head-pose-estimation-using-opencv-and-dlib
import cv2
import numpy as np
import math
import logging

#
# imgPts as numpy.array([(a), (b), (c), (f), (e), (g)]), dtype="double")
#   where (a) means (ax, ay) in pixel coords
#   nb: don't need d and h
#
#      a                        e
#     /x   b       0        f    \
#    /    /|                 \    \
#   /    / |                  \    \
#  d    /  |                   \    h
#      c   v                    g
#                  ^
#                  |
#                  z
#                  |
#      <-----y-----+
#
# 3D model points in robot-oriented coordinates: (x: forward, y: left, z: up)
#   Origin is chosen to be the midpoint between b and f.
#
#  let bf = 8"
#  Let ab = 2", bc = 5.5".
#  Let alpha = 14.5, be the angle between bc and bv (vertical)
#   sin(alpha) = cv / bc = ab / ax
#   cos(alpha) = bv / bc = ab / bx
#   cz = -cos(14.5) * 5.5
#
alpha = math.radians(14.5)
cosAlpha = math.cos(alpha)
sinAlpha = math.sin(alpha)

b = (0, 4, 0) # y is + to the left
f = (0, -4, 0) # y is - to the right
c = (0, b[1]+sinAlpha*5.5, b[2]-cosAlpha*5.5)
g = (0, f[1]-sinAlpha*5.5, f[2]-cosAlpha*5.5)
a = (0, b[1]+cosAlpha*2, b[2]+sinAlpha*2)
e = (0, f[1]-cosAlpha*2, f[2]+sinAlpha*2)
s_modelPts = np.array([a, b, c, f, e, g], dtype="double")

# s_modelPts:
# array([[ 0.       ,  5.93629528,  0.50076001],
#       [ 0.        ,  4.        ,  0.        ],
#       [ 0.        ,  5.37709002, -5.32481202],
#       [ 0.        , -4.        ,  0.        ],
#       [ 0.        , -5.93629528,  0.50076001],
#       [ 0.        , -5.37709002, -5.32481202]])
#
# estimatePose ----------------------------------------------------
# inputs:
#   image: can opencv image (Mat)
#   imgPts:	an numpy array imgPts as
# 	numpy.array([(a), (b), (c), (f), (e), (g)]), dtype="double")
#   focalLen: an optional parameter that characterizes the camera fov.
#    	should be provided in order to obtain accurate distances.
#
# return: None if we fail or (dx,dy,dtheta) required to move a robot at
# the origin # to the target.


# Camera Callibration results
# fx = 441.201212
# fy = 428.9449

# Principal point calculation
# SEE: cameraCallibrate.py
princPoint = (96.05094069, 108.39858878)

def estimatePose(im, imgPts, focalLen=None, display=False):
    ret = None
    size = im.shape
    # Camera internals
    if not focalLen:
        focalLen = size[1]
    center = (size[1]/2, size[0]/2)
    camMat = np.array(
                    [[focalLen, 0, princPoint[0]],
                    [0, focalLen, princPoint[1]],
                    [0, 0, 1]], dtype = "double"
                    )
    logging.debug("Camera Matrix :\n {0}".format(camMat))
    distCoeffs = np.zeros((4,1)) # Assuming no lens distortion
    (success, rotVec, xlateVec) = cv2.solvePnP(s_modelPts, imgPts, camMat,
                                        distCoeffs,
                                        flags=cv2.SOLVEPNP_ITERATIVE)
    if success:
        ret = (xlateVec[0][0], xlateVec[1][0], rotVec[0][0])
        #logging.debug("Rotation Vector:\n {0}".format(rotVec))
        #logging.debug("Translation Vector:\n {0}".format(xlateVec))
    else:
        logging.warning("solvePnP fail")

    # draw circles around our target points
    if display:
        for p in imgPts:
            cv2.circle(im, (int(p[0]), int(p[1])), 3, (0,0,255), -1)

        # Project a 3D point (-100, 0, 0.0) onto the image plane.
        # We use this to draw a line sticking out of origin of coordsys
        (projPts, jacobian) = cv2.projectPoints(np.array([(-100.0, 0.0, 0.0)]),
                                    rotVec, xlateVec, camMat, distCoeffs)

        # let imgOrigin be the midpoint between b and f
        imgOrigin = (int(.5 * (imgPts[1][0]+imgPts[3][0])),
                     int(.5 * (imgPts[1][1]+imgPts[3][1])))
        perpPt2 = (int(projPts[0][0][0]), int(projPts[0][0][1]))
        cv2.line(im, imgOrigin, perpPt2, (255,0,0), 2)

    return ret
