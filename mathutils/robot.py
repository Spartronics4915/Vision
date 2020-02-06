from affine3d import Affine3d
import numpy as np

class Robot:
    """
    Abstract year-specific coordinate system setups that allow us
    to transform from camera-space to field coords

    >>> r = Robot()
    >>> r.updateRobotPose(1, 2)
    >>> pts = np.array([[0, 0, 0]], dtype=np.float32)
    >>> npts = r.transformPoints(pts)
    >>> np.allclose(pts, npts)
    True
    """

    def __init__(self):
        self.mRobotToField = Affine3d()
        self.mCameraToRobot = Affine3d()  # this updates regularly

    def updateCameraPose(self, cpose): # fixed mounting of camera on robot
        pass

    def updateRobotPose(self, pose, timestamp):
        self.mCameraToField = Affine3d.concatenate(self.mCameraToRobot,
                                                   self.mRobotToField)

    def transformPoints(self, pts):
        return self.mCameraToField.transformPoints(pts)

if __name__ == "__main__":
    import doctest
    doctest.testmod()