from affine import Affine3
import numpy as np

class Robot:
    """
    Abstract Robot configuration for vision coordinate-system conversion. 
    Year-specific coordinate system setups are implemented in subclasses.

    >>> r = Robot()
    >>> r.updateRobotPose(1, 2)
    >>> pts = np.array([[0, 0, 0]], dtype=np.float32)
    >>> npts = r.transformPoints(pts)
    >>> np.allclose(pts, npts)
    True
    """

    def __init__(self):
        self.cameraToMount = Affine3() # this updates occasionally
        self.mountToRobot = Affine3()  # this may update regularly (moving turret)
        self.cameraToRobot = Affine3() # this may update regularly (moving turret)
        self.robotToField = Affine3()  # this updates regularly (moving robot)
        self.cameraToField = Affine3() # this updates regularly (moving robot)
        self.dirty = True

    # Express the *fixed* mounting of camera on robot or a turret. 
    # We expect this method on to be called upon robot's Vision 
    # subsystem initialization.
    def setCameraPose(self, camPose): 
        # camPose is a string of the form "ox oy oz [ q1 q2 q3 q4 ]"
        # if a camera is mounted on the robot pointing upward and directly forward
        # we might see "15 -15 8 [ .985 0 .1736 0 ]"
        # which means the camera is 
        #   * located in the front-right, 8 in off the ground
        #   * and pointing straight ahead, with an pitch/inclination of ~20 degrees
        # to obtain the quaternion, see Affine3
        vals = camPose.split(" ")
        if len(vals) == 9:
            ox = float(vals[0])
            oy = float(vals[1])
            oz = float(vals[2])
            q1 = float(vals[4])
            q2 = float(vals[5])
            q3 = float(vals[6])
            q4 = float(vals[6])
            rotMat = Affine3.fromQuaternion([q1, q2, q3, q4])
            offMat = Affine3.fromTranslation(ox, oy, oz)
            self.cameraToMount = Affine3.concatenate(offMat, rotMat)
            self.dirty = True
        else:
            print("Robot.setCamerasPose received unexpected input " + camPose)
    
    # Robot field pose (ie: robot position/heading in field coordinates)
    # aka the robotToField 
    def updateRobotPose(self, pose, timestamp):
        # pose is a string of the form: "xfield yfield heading"
        #   where x,y are inches and heading is degrees, with 0 degrees
        #   going along the field along x axis
        #   currently we don't receive robot origin height, we'll assume
        #   0 'til proven otherwise
        self.timestamp = timestamp
        self.pose = self._parseRobotPose(pose)

        xlate = Affine3.fromTranslation(self.pose[0], self.pose[1], 0)
        rot = Affine3.fromRotation(self.pose[2], [0, 0, 1])
        self.robotToField = Affine3.concatenate(xlate, rot)
        self.dirty = True

    def _parseRobotPose(self, pose):
        vals = pose.split(" ")
        if len(vals) == 3:
            x = float(vals[0])
            y = float(vals[1])
            heading = float(vals[2])
            return (x, y, heading)
        else:
            print("robot.py parseRobotPose botch " + pose)
            return ()
    
    def updateMountPose(self, pose, timestamp):
        # if camera is not mounted on turret, then this shouldn't be called
        # otherwise pose is a number representing the turret angle
        self.mountToRobot = None

    def transformPoints(self, pts):
        return self.mCameraToField.transformPoints(pts)

if __name__ == "__main__":
    import doctest
    doctest.testmod()