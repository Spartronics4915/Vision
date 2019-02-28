#!/usr/bin/env python3
#  https://docs.opencv.org/3.4/d9/d0c/group__calib3d.html
#  https://www.learnopencv.com/head-pose-estimation-using-opencv-and-dlib
#
#  https://www.raspberrypi.org/documentation/hardware/camera/
#
#                      picam1             picam2
#       sensor res     2592x1944px        3280x2464px
#       sensor size    3.76x2.74mm        3.68x2.76mm
#       aspect ratio   1.372              1.333 3
#       focal length   3.6mm              3.04mm
#       fov (h,v)      53.5,41.4deg       62.2,48.8deg
#
# https://en.wikipedia.org/wiki/Angle_of_view
#       fov = 2 * arctan(sensorSize/(2*focalLength))
#       for picam: hfov: 55.149  (which is bigger than 53.5)
#
#  http://answers.opencv.org/question/139166/focal-length-from-calibration-parameters/
#       fx = Fx * w / W  (Fx: focal length mm, w: pixels, W: sensor: mm)
#       for picam1, 640x480: fx=640*3.6/3.76=>612.77px, fy: 480*3.6/2.74=>630.66
#       for picam1, 320x240: fx=320*3.6/3.76=>306.38px, fy: 240*3.6/2.74=>315.32
#
# https://docs.opencv.org/2.4/doc/tutorials/calib3d/camera_calibration/camera_calibration.html
#   Darwin's initial Camera Callibration results (not sure what capture size was used)
#       fx = 441.201212, fy = 428.9449  (ie: pixels aren't exactly square)
#
#     "If for both axes a common focal length is used with a given a aspect ratio
#      (usually 1), then f_y=f_x*a and in the upper formula we will have a single
#      focal length f. The matrix containing these four parameters is referred to
#      as the camera matrix. While the distortion coefficients are the same
#      regardless of the camera resolutions used, these should be scaled along
#      with the current resolution from the calibrated resolution."
#
#  For transforming 3d points:
#  https://github.com/mapillary/OpenSfM/blob/61a98f6ab0f2d7b12592a92436648bd276f603d8/opensfm/transformations.py#L883
#
import cv2
import numpy as np
import math
import logging

# 2019 vision targets
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
# imgPts as numpy.array([(a), (b), (c), (f), (e), (g)]), dtype="double")
#   where (a) means (ax, ay) in pixel coords
#   nb: don't need d and h
#
# World Coordinate Convention
# 3D model points in robot-oriented coordinates. (x: forward, y: left, z: up).
# Origin is chosen to be the midpoint between b and f.
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

def estimatePose(im, imgPts, cameraMatrix=None, display=False):
    """
    Given an imput image and image points, guess where we are

    :param im: frame from which the image points were captured
    :type im: opencv frame (np.ndarray())

    :param imgPts: the critical points of the target figure
    :type imgPts: array

    :param cameraMatrix: The camera matrix to use. If this value is none, it is caluclated using domestic methods
    :type cameraMatrix: bool

    :param debug: logger.debug() prints
    :type debug: bool

    :return robotPoints: Where the robot is, with the target center as the point (0,0,0)
    :rtype: tuple, in the form of (x,y,theta)

    640x480
    Known inputs -> known outputs
    >>> class A(): pass
    >>> img = A()
    >>> img.shape = (480,640,1)
    >>> estimatePose(img,np.array([[269, 204],[301,212],[279,301],[429,211],[461,203],[451,299]],dtype='double'))
    (50, 0, 0), img
    """

    if cameraMatrix != None:
        camMat = cameraMatrix
    else:
        y,x,_ = im.shape  # shape is rows, cols (y, x)
        if False:
            # couch-potato formulation
            fx = x
            fy = x
            cx,cy = (x/2, y/2)
        else:
            # we employ picam1 specs to compute fx
            fx = x*3.6/3.76
            fy = y*3.6/2.74
            cx,cy = (fx/2,fy/2)

        camMat = np.array([
                    [fx, 0, cx],
                    [0, fy, cy],
                    [0, 0, 1]
                    ], dtype = "double"
                    )
    logging.debug("Camera Matrix :\n {0}".format(camMat))
    distCoeffs = np.zeros((4,1)) # Assuming no lens distortion
    (success, rotVec, xlateVec) = cv2.solvePnP(s_modelPts, imgPts, camMat,
                                        distCoeffs,
                                        flags=cv2.SOLVEPNP_ITERATIVE)
    if not success:
        logging.warning("solvePnP fail")
        return None
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

        # First transform target world points to camera coordinates.
        # In opencv x is to the right, y is down and z is fwd.
        targetPts = np.array([
            (0.0, 0.0, 0.0), # origin
            (1.0, 0.0, 0.0), # point "into" wall from pov of robot
            (0.0, 0.0, 1.0)  # point up
        ])
        (rotmat,_) = cv2.Rodrigues(rotVec) # produces 3x3 rotation matrix
        camPts = []
        xlateVec = xlateVec.reshape(3,) # so we can add to rotpt below
        for p in targetPts:
            rotpt = rotmat.dot(p) # (3,3)dot(3,1) -> (3,)
            campt = rotpt + xlateVec
            camPts.append(campt)

        # Next we convert our camera coordinates:
        #   x is right
        #   y is down
        #   z is into the screen
        # to robot coords:
        #   x is into the screen
        #   y is left
        #   z is up
        robotPts = []
        for p in camPts:
            robotPts.append(np.array([p[2], -p[0], p[1]]))

        # we return the robot-relative x,y,z coords of target
        # as well as the angle between the robot heading and
        # targetPerp in the x/y plane.  (robot heading is (1,0,0))
        perpVec = robotPts[1] - robotPts[0] # origin to perp point vector
        perpVec[2] = 0 # don't care about height
        perpUnit = perpVec / np.linalg.norm(perpVec, 2, -1)
        # dot of 2 unit-vectors is cos of angle
        theta = math.acos(perpUnit.dot([1.,0.,0.])) 

        if display:
            # draw red circles around our target (image) points
            for p in imgPts:
                cv2.circle(im, (int(p[0]), int(p[1])), 3, (0,0,255), -1)

            # Project two target points onto the image plane.
            # We use this to draw a line sticking out of origin of coordsys
            worldPts = np.array([(0.0, 0.0, 0.0), (-10.0,0.0,0.0)])
            (projPts, _) = cv2.projectPoints(worldPts,
                                        rotVec, xlateVec, camMat, distCoeffs)
            org = (int(projPts[0][0][0]), int(projPts[0][0][1]));
            perp = (int(projPts[0][1][0]), int(projPts[0][1][1]));
            cv2.circle(im, org, 3, (255,0,0), -1)
            cv2.line(im, org, perp, (255,0,0), 2) # blue line

        # in the form x,y, theta
        print("X 'point': " + str(robotPts[0][0]))
        print("Y 'point': " + str(robotPts[0][1]))
        print("Theta 'number': " + str(theta))

        return (robotPts[0][0], robotPts[0][1], theta), im

if __name__ ==  "__main__":
    import doctest
    import logging

    logFmt = "%(name)-8s %(levelname)-6s %(message)s"
    dateFmt = "%H:%M"
    logging.basicConfig(level=logging.DEBUG,format=logFmt, datefmt=dateFmt)

    logging.info("Began logger")
    
    doctest.testmod()