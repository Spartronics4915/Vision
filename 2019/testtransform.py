#!/usr/bin/env python
 
import cv2
import numpy as np
import math
 
# Read Image
size = [480,640]
     
#2D image points. If you change the image, you need to change vector
image_points = np.array([
                            (359, 391),     # Nose tip
                            (399, 561),     # Chin
                            (337, 297),     # Left eye left corner
                            (513, 301),     # Right eye right corne
                            (345, 465),     # Left Mouth corner
                            (453, 469)      # Right mouth corner
                        ], dtype="double")
 
# 3D model points.
model_points = np.array([
                            (0.0, 0.0, 0.0),             # Nose tip
                            (0.0, -330.0, -65.0),        # Chin
                            (-225.0, 170.0, -135.0),     # Left eye left corner
                            (225.0, 170.0, -135.0),      # Right eye right corne
                            (-150.0, -150.0, -125.0),    # Left Mouth corner
                            (150.0, -150.0, -125.0)      # Right mouth corner
                         
                        ])
 
 
# Camera internals
 
focal_length = size[1]
center = (size[1]/2, size[0]/2)
camera_matrix = np.array(
                         [[focal_length, 0, center[0]],
                         [0, focal_length, center[1]],
                         [0, 0, 1]], dtype = "double"
                         )
 
print("Camera Matrix :\n {0}".format(camera_matrix))
 
dist_coeffs = np.zeros((4,1)) # Assuming no lens distortion
(success, rotation_vector, translation_vector) = cv2.solvePnP(model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE)
 

rotation_vector = np.array([[math.pi/2.], [0.0], [0.0]])
(rotation_matrix,_) = cv2.Rodrigues(rotation_vector)

print("Rotation Vector {0}:\n {1}".format(np.shape(rotation_vector), 
                                                rotation_vector))
print("Rotation Matrix {0}:\n {1}".format(np.shape(rotation_matrix), 
                                                rotation_matrix))
print("Translation Vector {0}:\n {1}".format(np.shape(translation_vector),
                                                translation_vector))
# numpy.shape(translation_vector) is (1,3)
#
# [[ -113.84452688]
#  [ -297.88517426]
#  [-1340.13762528]]


campts = []
print("rot_matrix {0}, pointlist {1}".format(np.shape(rotation_matrix),
                                             np.shape(model_points)))
xlate = translation_vector.reshape((3,)) # to add to result of dot
for pt in model_points:
    rotpt = np.dot(rotation_matrix, pt) # (3,3)dot(3,1) ->  (3,)
    print("{0} dot {1} -> {2}".format(np.shape(rotation_matrix),
                                    np.shape(pt), np.shape(rotpt)))
    campt = rotpt + xlate
    print("{0} + {1} -> {2}".format(np.shape(rotpt),
                                np.shape(xlate),
                                np.shape(campt)))
    campts.append(campt)

print("\n\nAll campts")
print(campts)

if True:
    print("\nworld origin: {0}".format(campts[0]))
    v1 = campts[1] - campts[0] 
    v2 = campts[2] - campts[0] 
    v1Unit = v1 / np.linalg.norm(v1, 2, -1)
    #v2Unit = v2 / np.linalg.norm(v2, 2, -1)
    v2Unit = [0.0, 1.0, 0.0]
    dot = v1Unit.dot(v2Unit)
    print("dot {0}: {1}".format(np.shape(dot), dot))
    angle = math.degrees(math.acos(dot))
    print("angle between two vectors in camera space: {0}".format(angle))


