from robot import *

class Robot2020(Robot):
    """
    # vision's goal is to identify landmarks in the camera then to convey
    # to location of the landmark to the robot code expressed in field coords.
    #
    # ie: want camera to robot to field transformation
    #
    # field coords (z is up)
    #
    #           y
    #       ._____|____. 
    #       |     |    | 
    #       |     o-----x
    #       |__________| 
    #
    # robot coords (z is up)
    #
    #           y
    #       .___|___. 
    #       |   |  T|
    #       |   o-----x
    #       |_______| 
    #
    # turret coords (T above), 0 degrees is x axis, z is up,
    # turret reports current aim angle periodically
    #
    # 
    # camera coords from the top (y is down)
    #
    #         /
    #        /       ______ z  
    #        \       |
    #         \      x
    #
    # camera is mounted with an angle of 20 around y and offset from robot origin
    >>> cameraToRobot = Affine3d.fromRotation(-20, [0, 1, 0]).translate(10, 10, 0) 
    >>> p = cameraToRobot.transformPoints([[0, 0, 0]])[0]

    # field is approx x: [0, 52*12], y: [-26*12, 26*12] (z is up)

    >>> r = Robot2020()
    >>> r.updateRobotPose(1, 2)
    >>> pts = np.array([[0, 0, 0]], dtype=np.float32)
    >>> npts = r.transformPoints(pts)
    >>> np.allclose(pts, npts)
    True
    """

    def __init__(self):
        super().__init__()
        self.mCameraToTurret = Affine3d()
        self.mTurretToRobot = Affine3d()
    
    def updateRobotPose(self, pose, timestamp):
        self.mCameraToField = Affine3d.concatenate(self.mCameraToTurret,
                                                   self.mTurretToRobot,
                                                   self.mCameraToRobot,
                                                   self.mRobotToField)

    def updateTurretPose(self, angle):
        pass

if __name__ == "__main__":
    import doctest
    doctest.testmod()