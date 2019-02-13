#!/usr/bin/python3
# Deriving camera characteristics based on chessboard identification
# nb: 
#       Currently the only values from this script that are being implemented is the principal point, which (according to cv2.calibrateCamera()) is not at the center of the screen
#       Focal length is calculated according to some math found online
# Focal length:

# https://raspberrypi.stackexchange.com/questions/81964/calculating-focal-length-of-raspberry-pi-camera
# Focal math (using ‘swnsor width’ and ‘focal length’ in spec sheet)
# 
#       Focal_width_px =  (camera_focal_length / camera_sensor_size) * window size
# 
#       Focal_width_px  = ( 3.6 / 3.76) * 320
#       = 306.3829787
#
# When plugging in the calculated value for fx and fy, the distance estimation was much, much closer than
# when using the fx and fy returned by cv2.calibrateCamera, however currently the principal point given by
# calibrateCamera() is still in effect.

import numpy as np
import cv2
import glob

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
# 9x9
objp = np.zeros((9*9,3), np.float32)
objp[:,:2] = np.mgrid[0:9,0:9].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

# images = glob.glob('chess320x240_3_rotated.jpg')

img = cv2.imread('chess320x240.jpg')
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

# Find the chess board corners
ret, corners = cv2.findChessboardCorners(gray, (9,9),None)

# If found, add object points, image points (after refining them)
if ret == True:
        objpoints.append(objp)

corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
imgpoints.append(corners2)

# Draw and display the corners
img = cv2.drawChessboardCorners(img, (7,6), corners2,ret)

# Save image
cv2.imwrite('out.png',img)

ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)

# rvecs = rotation vectors
# tvecs = translation vectors

# dist = distance coeficcants
# mtx = camera matrix

# print relevent matricies

print("Camera Matrix: \n {0} ".format(mtx))

print("Distance coefficants: \n {0} ".format(dist))

print("Translation vector: \n {0}".format(tvecs))





