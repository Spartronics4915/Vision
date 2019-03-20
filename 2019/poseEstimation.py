#!/usr/bin/env python3
#  https://docs.opencv.org/3.4/d9/d0c/group__calib3d.html
#  https://www.learnopencv.com/head-pose-estimation-using-opencv-and-dlib
#
#  https://www.raspberrypi.org/documentation/hardware/camera/
#
#                      picam1             picam2
#       sensor res     2592x1944px        3280x2464px
#       sensor size    3.76x2.74mm        3.68x2.76mm
#       aspect ratio   1.372              1.333
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
#                  +------x---------->
#                  |
#                  y
#                  |
#                  | 
#                  v
#                   (targets on the z=0 plane)
#
# imgPts as numpy.array([(a), (b), (c), (f), (e), (g)]), dtype="double")1
#   where (a) means (ax, ay) in pixel coords
#   nb: don't need d and h
#
# World Coordinate Convention
# 3D model points in robot-oriented coordinates. (x: right, y: down, z: in).
# Origin is chosen to be the midpoint between b and f.
#
# From the game specs:
#  let bf = 8"
#  Let ab = 2", bc = 5.5" (tape is 2x5.5)
#  Let alpha = 14.5, be the angle between bc and bv (vertical)
#   sin(alpha) = cv / bc = ab / ax
#   cos(alpha) = bv / bc = ab / bx
#   cz = -cos(14.5) * 5.5
#
alpha = math.radians(14.5)
cosAlpha = math.cos(alpha)
sinAlpha = math.sin(alpha)

b = (-4,0,0) # x is right
f = (4,0,0) 
c = (b[0]-sinAlpha*5.5, b[1]+cosAlpha*5.5,0)
g = (f[0]+sinAlpha*5.5, f[1]+cosAlpha*5.5,0)
a = (b[0]-cosAlpha*2, b[1]-sinAlpha*2,0)
e = (f[0]+cosAlpha*2, f[1]-sinAlpha*2,0)
s_modelPts = np.array([a, b, c, f, e, g], dtype="double")
s_firstTime = True

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

def estimatePose(im, imgPts, cfg, cameraMatrix=None, display=False):
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

    Known inputs -> known outputs
    These points are based on test images
    >>> class A(): pass
    >>> img = A()
    >>> img.shape = (480,640,1)
    >>> estimatePose(img,np.array([[269, 204],[301,212],[279,301],[429,211],[461,203],[451,299]],dtype='double'))
    (50, 0, 0), img
    """
    global s_firstTime

    distCoeffs = np.zeros((4,1)) # start: no lens distortion, may be overridden
    if cameraMatrix != None:
        camMat = cameraMatrix
        camnm = "<passed-in>"
    else:
        y,x,_ = im.shape  # shape is rows, cols (y, x)
        camnm = cfg["pnpCam"]
        if camnm == "couch":
            # couch-potato formulation
            fx = x
            fy = x
            cx,cy = (x/2, y/2)
        elif camnm == "theory":
            # we employ picam1 specs to compute fx
            fx = x*3.6/3.76
            fy = y*3.6/2.74
            cx,cy = (fx/2,fy/2)
        elif camnm == "dbcam8":
            # from calibration
            (fx,fy) = (656.176, 654.445)
            (cx,cy) = (350.305, 222.377)
            distCoeffs = np.array([0.117,  0.191,  0.012, 0.020, -1.12])
        elif camnm == "dbcam7":
            # from calibration
            (fx,fy) = (573.046, 593.765)
            (cx,cy) = (332.130, 285.449)
            distCoeffs = np.array([-0.159,  3.382,  0.0234, 0.0013 -20.5])
        else:
            # theory plus rotate 90?
            fx = 1.35*x*3.6/3.76
            fy = 1.35*y*3.6/2.74
            cx,cy = (fx/2,fy/2)
        camMat = np.array([
                    [fx, 0, cx],
                    [0, fy, cy],
                    [0, 0, 1]
                    ], dtype = "double"
                    )
    if s_firstTime:
        logging.info("Camera Matrix '{}':\n {}".format(camnm, camMat))
        s_firstTime = False

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

        # First transform target *world* points to camera coordinates.
        # In opencv x is to the right, y is down and z is fwd.
        targetPts = np.concatenate((np.array([
                            (0, 0, 0), # origin
                            (0, 0, 12), # away
                            (0, 0, -12),# toward
                            (0, -12, 0),# up
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

        if display:
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
            try:
                cv2.circle(im, org, 5, (0,0,255), -1)
                cv2.line(im, org, away, (255,255,0), 2) # cyan
                cv2.line(im, org, toward, (255,0,0), 2) # blue
                cv2.line(im, org, up, (0,255,0), 2) # green
                cv2.line(im, org, right, (0,0,255), 2) # red
            except Exception as e:
                # line drawing can throw execeptions for bogus 
                # values
                pass

            for i in range(5,projPts.shape[0]):
                p = (int(projPts[i][0][0]), int(projPts[i][0][1]))
                cv2.circle(im, p, 3, (0, 255,0), -1)

            if True:
                print("%5.2f, %5.2f, %.1f" %
                 (robotPts[0][0], robotPts[0][1], math.degrees(theta)),
                 end="\r")

        # we return the robot-relative x,y,z coords of target
        # as well as the angle between the robot heading and
        # targetPerp in the x/y plane.  (robot heading is (1,0,0))
        return (robotPts[0][0], robotPts[0][1], theta), im

if __name__ ==  "__main__":
    import doctest
    import logging

    logFmt = "%(name)-8s %(levelname)-6s %(message)s"
    dateFmt = "%H:%M"
    logging.basicConfig(level=logging.DEBUG,format=logFmt, datefmt=dateFmt)

    logging.info("Began logger")
    
    doctest.testmod()
