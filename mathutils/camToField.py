import numpy as np
if __package__ == "" or __package__ is None:
    from affine import *
    from vec import *
else:
    from .affine import *
    from .vec import *

class CamToField:
    """
    Abstract Robot configuration for vision coordinate-system conversion. 
    Year-specific coordinate system setups are implemented in subclasses.
    Our purpose is to convert target pts acquired from the POV of our camera
    into field coordinates for use by the robot's navigation/path-planning]
    system.  We expect to receive periodic updates to the robot pose.
    These poses are timestamped on the robot and when we deliver a target
    result, it represents the target field location as seen at the
    time in the past represented by the associated timestamp.

    Example
    >>> ctof = CamToField()
    >>> camToMountStr = "o 10 10 8 q 0.92388 0.382683 -0 -0"
    >>> mountToRobotStr = "o 0 0 0 q 0.5 0.5 -0.5 -0.5"
    >>> ctof.setCameraPose(camToMountStr)
    >>> ctof.setMountPose(mountToRobotStr) 
    >>> ctof.updateRobotPose("40 40 5.2", 333)
    >>> ctof.updateMountPose("5", 334) # optional, year-dependent pose
    >>> targetInCamera = [0, 0, -120]  # 10 feet from camera in center of its screen
    >>> targetField = ctof.transformPoints([targetInCamera])[0]
    >>> targetFieldDir = ctof.transformVectors([targetInCamera])[0]
    >>> np.allclose(Vec3.length(targetFieldDir), 120)
    True
    """

    def __init__(self):
        # camToMount is usually fixed, sent during init. If the camera
        #    is rigidly mounted on the robot, then you can express its pose
        #    entirely in camToMount (and leave mountToRobot untouched).
        #    camToMount must compensate for the difference between
        #    the camera coordinate system as well as it's position/orientation 
        #    relative to the mount point.
        self.camToMount = Affine3() 

        # mountToRobot may be the identity, fixed or changing as with
        #    a camera mounted on a moving turret.
        self.mountToRobot = Affine3()  # this may update regularly (moving turret)
        
        # robotToField represents the transform that takes the robot coordsys
        #    to the field.  Assuming our robot moves during the match this 
        #    should be updated regularly.
        self.robotPose = None  # received from robot, converted to robotToField
        self.robotToField = Affine3()  # this updates regularly (moving robot)

        # camToRobot - may be useful for diagnostics and should be the
        # same as camToMount if there is no separate mount (eg turret)
        self.camToRobot = Affine3() 

        # camToField is the primary result of all this - it represents
        # the entire chain of transformations from camera to mount to robot
        # to field.
        self.camToField = Affine3() # primary Vision result

        self.timestamp = 0
        self.dirty = True

    # Express the *fixed* mounting of camera on robot or a turret. 
    # We expect this method on to be called upon robot's Vision 
    # subsystem initialization.
    def setCameraPose(self, camPose): 
        # camPose is a string that represents an Affine3, usually obtained
        # by affineObj.asString()
        self.camToMount = Affine3.fromString(camPose)
        self.dirty = True

    def setMountPose(self, mountPose):
        # If camera is mounted directly onto robot then this shouldn't be called
        # otherwise pose is a number representing the mount's orientation
        # wrt to the robot (ie:  mountToRobot, robotToMount)
        # we might see "15 -15 8 [ .985 0 .1736 0 ]"
        self.mountToRobot = Affine3.fromString(mountPose)
        self.dirty = True
    
    # Robot field pose (ie: robot position/heading in field coordinates)
    # aka the robotToField 
    #
    # field coords (z is up)
    # field is approx x: [0, 52*12], y: [-26*12, 26*12] (z is up)
    #
    #                       y
    #                 ._____|____. 
    #  Blue Alliance  |     |    |  Red Alliance
    #                 |     o-----x
    #                 |__________| 
    #
    def updateRobotPose(self, robotPose, timestamp):
        """
        # Test
        # 1. place robot on the field at a heading of -20 degrees, at 150, 150, 
        #     robot center is 8 inches off the ground
        >>> robotToField = Affine3.fromTranslation(150, 150, 8).rotate(-20, [0, 0, 1])
        >>> pts = robotToField.transformPoints([[0, 0, 0], [1, 0, 0], [0, 1, 0]])
        >>> np.allclose(pts[0], [150, 150, 8])
        True

        # 2. verify field orientation of robot x axis
        >>> ndirs = robotToField.transformVectors([[1, 0, 0]])
        >>> angle = math.degrees(math.atan2(ndirs[0][1], ndirs[0][0]))
        >>> np.allclose(angle, -20)
        True
        """
        # robotPose is a string of the form: "xfield yfield heading"
        #   where x,y are inches and heading is degrees, with 0 degrees
        #   going along the field along x axis
        #   currently we don't receive robot origin height, we'll assume
        #   0 'til proven otherwise
        assert(timestamp >= self.timestamp)
        self.timestamp = timestamp
        vals = robotPose.split(" ")
        assert(len(vals) == 3)
        self.robotPose = (float(vals[0]), float(vals[1]), float(vals[2]))
        xlate = Affine3.fromTranslation(self.robotPose[0], self.robotPose[1], 0)
        rot = Affine3.fromRotation(self.robotPose[2], [0, 0, 1])
        self.robotToField = Affine3.concatenate(xlate, rot)
        self.dirty = True
    
    # If the vision camera is mounted on an articulated mechanism (eg turret)
    # we expect to receive an update to the mount description.  The format
    # of mountPose may differ from season-to-season.  In the case of a turret
    # we expect that the mountPose is merely an angle to capture the current
    # turret angle.  Note that this must be composed with other mount 
    # characteristics (ie: its offset and orientation of the zero angle)
    def updateMountPose(self, mountPose, timestamp):
        assert(timestamp >= self.timestamp)
    
    # Transform points provided in camera coordinates to field coordinates.
    def transformPoints(self, pts):
        if self.dirty:
            self._rebuildTransforms()
            self.dirty = False
        return self.camToField.transformPoints(pts)

    def transformVectors(self, pts):
        if self.dirty:
            self._rebuildTransforms()
            self.dirty = False
        return self.camToField.transformVectors(pts)
    
    def _rebuildTransforms(self):
        self.camToRobot = Affine3.concatenate(self.camToMount, self.mountToRobot)
        self.camToField = Affine3.concatenate(self.camToRobot, self.robotToField)

if __name__ == "__main__":
    import doctest
    import math
    doctest.testmod()
