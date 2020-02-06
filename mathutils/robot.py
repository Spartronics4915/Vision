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
        self.mRobotToField = Affine3()
        self.mCameraToMount = Affine3() # this updates occasionally
        self.mMountToRobot = Affine3()  # this may update regularly
        self.mCameraToRobot = Affine3() # this may update regularly
        self.mCameraToField = Affine3() # this updates regularly
        self.mDirty = True

    # Fixed mounting of camera on robot, expect this method on 
    # robot's Vision subsystem initialization.
    def setCameraMountPose(self, camPose): 
        # camPose is a string of the form "ox ox oz angle angle2 angle3 eulerstring"  
        vals = camPose.split(" ")
        if len(vals) == 7:
            ox = float(vals[0])
            oy = float(vals[1])
            oz = float(vals[2])
            a1 = float(vals[3])
            a2 = float(vals[4])
            a3 = float(vals[5])
            order = vals[6]
            rotMat = Affine3.fromEulerAngles(a1,a2,a3,order)
            offMat = Affine3.fromTranslation(ox, oy, oz)
            self.mCameraToMount = Affine3.concatenate(offMat, rotMat)
        else:
            print("Robot.setCamerasPose received unexpected input " + camPose)

    # robot field pose (ie: robot position in field coordinates)
    def updateRobotPose(self, pose, timestamp):
        # pose is a string of the form: 
        self.timestamp = timestamp
        self.mCameraToField = Affine3.concatenate(self.mCameraToRobot,
                                                  self.mRobotToField)

    def transformPoints(self, pts):
        return self.mCameraToField.transformPoints(pts)

if __name__ == "__main__":
    import doctest
    doctest.testmod()