#!/usr/bin/python3s
'''
Holding cell for cv2 calles to approximate the 'acutal' reprojection error for a given resolution
'''

import cv2
import numpy as np
import math

# TODO: Feed into config.py
# The camera intresnics to run a test off of
focalLength = (639.83052859,639.70771165)

principalPoint = (322.56252014,250.77160068)

distortionCoeffs = np.array([ 1.11238973e-01, -1.04070952e+00,  2.61772165e-03,6.55387532e-04,  2.07132619e+00])

DIST = 12 #In inches, the distance we want to approximate our error 

# projPts: a point in camera space

rotVec = np.zeros((1,3))
xlateVec = np.array([0,0,DIST],dtype = "float32")

camMat = np.array([
                [focalLength[0], 0, principalPoint[0]],
                [0, focalLength[1], principalPoint[1]],
                [0, 0, 1],
                ], dtype = "double")

targetPts = np.array([
                        (5, 0, 0), # origin
                        (-5, 0, 0), # origin

                    ], dtype = "float32")

(projPts, _) = cv2.projectPoints(targetPts, rotVec, xlateVec, camMat, distortionCoeffs)

print("ProjPts: {}".format(projPts))