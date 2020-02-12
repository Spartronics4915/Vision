#!/usr/bin/env python3

import cv2
import numpy as np
import math
import logging

# -= ASCII Art =-
#
#                        +y
#                         ^
#                         |
#                         |
#   a ___ h               Θ----->+X        e ___ d
#     \  \                                  /  /
#      \  \                                /  /
#       \  \                              /  /
#        \  \                            /  /
#         \  \                          /  /
#          \  \  g                  f  /  /
#           \  \______________________/  /
#            \__________________________/
#            b                           c

# Notes About Chameleon's Points
#       - 4 'Found points' are outer of the target

alpha = math.radians(30)
cosAlpha = math.cos(alpha)
sinAlpha = math.sin(alpha)
tanAlpha = math.tan(alpha)

tapeWidth = 2 # in inches
# Length of the inner side
# Length of the outer side 
outerLength = 13.573
# Length of side dividing between sections (equal to e-d, f-c, g-b, a-h ) 
# Also the hypotenuse of the triangle formed between the points f, c, and the outer side
divideLength = tapeWidth/cosAlpha
#    f
#    |\  
#    | \
# 2in|  \ 2.309in
#    |   \
#    |____\  c
#    1.154in    


# Chamelion Vision Model Points (x,y,z)
a = (-19.625,      0, 0)
b = (-9.819867, -17, 0)
c = (9.819867,  -17, 0)
d = (19.625,       0, 0)

e = (17.316,       0, 0)
f = (8.665867,   -15, 0)
g = (-9.819867,  -15, 0)
h = (-17.316,      0, 0)
'''
# Other 4 Model Points
# Creading e from d 
e = d
e[0] - divideLength

# Creating f from c 
f = c
f[0] - 1.154    # x
f[1] + 2        # y

# creating g from b
g = b
g[0] + 1.154    # x
g[1] + 2        # y

# creating h from a
h = a
h[0] + divideLength
'''
# Model Points
#s_modelPts = np.array([a, b, c, d], dtype="double")
s_modelPts = np.array([a, b, c, d, e, f, g, h], dtype="double")

s_firstTime = True

# s_modelPts:
# array([[-16.25    ,   0.      ,   0.      ],
#       [ -9.819867, -17.      ,   0.      ],
#       [  9.819867, -17.      ,   0.      ],
#       [ 16.25    ,   0.      ,   0.      ]])
#
# estimatePose ----------------------------------------------------

def estimatePose(im, imgPts, cfg):
    """
    Given an input image and image points, guess where we are

    :param im: frame from which the image points were captured
    :type im: opencv frame (np.ndarray())

    :param imgPts: the critical points of the target figure
    :type imgPts: array

    :param cfg: Config representing our current run at the 'algo' level
    :type cameraMatrix: dict

    :return : The rotation and translation vector from the ROBOTS position, to the center of the target,
              in CAMERA COORDINATES, and the image
    :rtype: array, in the form of xlateVector, rotVector, image

    Known inputs -> known outputs
    These points are based on test images
    >>> class A(): pass
    >>> img = A()
    >>> img.shape = (480,640,1)
    >>> cfg = {"pnpCam":"0"}

    """
    global s_firstTime

    # If there are camera intresncics set in the config, default to those
    try:

        fx,fy = cfg['camIntrensics1080p']['focalLength']
        cx,cy = cfg['camIntrensics1080p']['principalPoint']
        distCoeffs = cfg['camIntrensics1080p']['distortionCoeffs']
        
    except Exception as e:
        logging.debug("Running PnP with no camera intrensics in config!")
        distCoeffs = np.zeros((4,1)) 
        y,x,_ = im.shape
        # Default to theory camera intrensics, which seem to be closest to 
        fx = x*3.6/3.76
        fy = y*3.6/2.74
        cx,cy = (fx/2,fy/2)


    camMat = np.array([
                [fx, 0, cx],
                [0, fy, cy],
                [0, 0, 1],
                ], dtype = "double")

    if s_firstTime:
        logging.info("Camera Matrix '{}'\n".format(camMat))
        logging.info("Disortion Coefficients '{}'\n".format(distCoeffs))

        logging.info("Passing values into solvePnP: \n")
        logging.info("s_modelPts: {}\n".format(s_modelPts))
        logging.info("ImgPts: {}\n".format(imgPts))
        s_firstTime = False
    

    (success, rotVec, xlateVec) = cv2.solvePnP(s_modelPts, imgPts, camMat,
                                        distCoeffs,
                                        flags=cv2.SOLVEPNP_ITERATIVE)
    if not success:
        logging.warning("solvePnP fail")
        return None,None,None
    else:
        # here's the shapes and sizes of matrices for reference
        # Camera Matrix :
        #   [[ 640.    0.  320.]
        #    [   0.  640.  240.]
        #    [   0.    0.    1.]]
        # Rotation Vector (3, 1):
        #   [[ 1.57079633]
        #    [ 0.        ]
        #    [ 0.        ]]
        # Rotation Matrix (3, 3):
        # [[  1.00000000e+00   0.00000000e+00   0.00000000e+00]
        #  [  0.00000000e+00   6.12323400e-17  -1.00000000e+00]
        #  [  0.00000000e+00   1.00000000e+00   6.12323400e-17]]
        # Translation Vector (3, 1):
        # [[ -113.84452688]
        #  [ -297.88517426]
        #  [-1340.13762528]]
        #logging.debug("Rotation Vector:\n {0}".format(rotVec))
        #logging.debug("Translation Vector:\n {0}".format(xlateVec))

        # First transform target *world* points to camera coordinates.
        # In opencv x is to the right, y is down and z is fwd.

        # This matrix is used to draw the corrdinate axis on the ouput image
        targetPts = np.concatenate((np.array([
                            (0, 0, 0), # origin
                            (0, 0, 12), # away
                            (0, 0, -12),# toward
                            (0, 12, 0),# up (changed from 2019 due to SC change)
                            (12, 0, 0)  # right 
                        ]), s_modelPts))

        (rotmat,_) = cv2.Rodrigues(rotVec) # produces 3x3 rotation matrix


        camPts = []
        xlateVec = xlateVec.reshape(3,) # so we can add to rotpt below
        for tgp in targetPts:
            rotpt = rotmat.dot(tgp) # (3,3)dot(3,1) -> (3,)
            campt = rotpt + xlateVec
            camPts.append(campt)

        # camPerp is a vector in camera space
        camPerp = camPts[1] - camPts[0] 

        # next we compute theta in camera coords
        #   x is right
        #   y is down
        #   z is into the screen
        perpVec = camPts[1] - camPts[0] # origin to perp point vector
        perpVec[1] = 0 # don't care about y component of angle
        perpUnit = perpVec / np.linalg.norm(perpVec, 2, -1)
        # dot of 2 unit-vectors is cos of angle
        theta = math.acos(perpUnit.dot([0.,0.,1.])) 
        if perpUnit[0] > 0: # cos of small angles is always positive
            theta *= -1

        # to robot coords:
        #   x is into the screen
        #   y is left
        #   z is up
        robotPts = []
        for p in camPts:
            robotPts.append(np.array([p[2], -p[0], -p[1]]))

        if cfg['display']:
            if False: # draw red circles around our target (image) points
                for p in imgPts:
                    cv2.circle(im, (int(p[0]), int(p[1])), 3, (0,0,255), -1)

            # Project two target points onto the image plane.
            # We use this to draw a line sticking out of origin of coordsys
            (projPts, _) = cv2.projectPoints(targetPts,
                                        rotVec, xlateVec, camMat, distCoeffs)
            #print("shape of projPts:" + str(projPts.shape)) 
            #    returns (2, 1, 2)
            # print(str(projPts)) 
            #  returns  [[[ 125  153]]
            #            [[ 118 126.]]]
            # a[0] is [[125 153]],
            # a[1] is [[128 126]]
            # a[0][0][0] is 125
            # a[1][0][1] is 126
            org = (int(projPts[0][0][0]), int(projPts[0][0][1]))
            away = (int(projPts[1][0][0]), int(projPts[1][0][1]))
            toward = (int(projPts[2][0][0]), int(projPts[2][0][1]))
            up = (int(projPts[3][0][0]), int(projPts[3][0][1]))
            right = (int(projPts[4][0][0]), int(projPts[4][0][1]))
            # 
            # human (sgi) camera (rh) coords:
            #   red is +x
            #   green is +y
            #   blue is -z
            #   cyan is +z
            # Draws coordinate axis
            try:
                cv2.circle(im, org, 5, (0,0,255), -1)
                cv2.line(im, org, away, (255,255,0), 2) # cyan
                cv2.line(im, org, toward, (255,0,0), 2) # blue
                cv2.line(im, org, up, (0,255,0), 2) # green
                cv2.line(im, org, right, (0,0,255), 2) # red
            except Exception as e:
                # line drawing can throw execeptions for bogus values
                logging.debug("PnP draw coordinate system failed with: " + str(e))
                pass

            for i in range(5,projPts.shape[0]):
                p = (int(projPts[i][0][0]), int(projPts[i][0][1]))
                cv2.circle(im, p, 3, (0, 255,0), -1)

            if False:
                print("%5.2f, %5.2f, %.1f" %
                 (robotPts[0][0], robotPts[0][1], math.degrees(theta)),
                 end="\r")

        # we return the robot-relative x,y,z coords of target
        # as well as the angle between the robot heading and
        # targetPerp in the x/y plane.  (robot heading is (1,0,0))

        # TODO: Currently returns the most untampered data, however robot points may be useful in the future
        return xlateVec,rotVec,im

if __name__ ==  "__main__":
    import doctest
    import logging

    logFmt = "%(name)-8s %(levelname)-6s %(message)s"
    dateFmt = "%H:%M"
    logging.basicConfig(level=logging.DEBUG,format=logFmt, datefmt=dateFmt)

    logging.info("Began logger")
    
