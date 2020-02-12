from camToField import *
from vec import *

class CamToField2020(CamToField):
    """
    # Vision's goal is to identify landmarks as seen by the camera (ie in 
    # camera space) then to convey the location of the landmark to the robot 
    # code expressed in field coords. It's possible that the camera will be 
    # mounted atop a moving turret.
    #
    # hence: we want camera-to-turret-to-robot-to-field transformation!
    #
    # summary:  
    #   camToMount (take origin of camera into mount space )
    #       we may choose to mount the camers on moving turret or directly
    #       on the robot.
    #   turretToRobot  (take origin/orientation of turret into robot space)
    #   robotToField   (take origin/orientation of robot into field space)
    #   camToField (take origin/orientation of camera into field space)
    #
    >>> r = CamToField2020()
    >>> r.updateRobotPose("150 150 20", 0)
    >>> fpt = r.transformPoints([[0, 0, -120]])[0]
    >>> np.allclose(fpt, [194.45436, 153, -24.7487])
    True
    """

    def __init__(self):
        super().__init__()
        camTilt = 45 # extreme example
        camPos = [0, -12, 0]  # "right" of turret origin, same height as turret origin
        self.camToMount = self._createCamToMount(camTilt, camPos)
        self.mountToRobot = self._createMountToRobot()

    def _createCamToMount(self, camTilt, camPos):
        """
        #  camera coordsys (ie: looking out the camera, cf poseEstimation.py)
        #    x is right, y is up, -z is into the screen
        #       
        #  camToMount:  assume that the camera is mounted on turret, C below.
        #  If we decide that we want a fixed camera, we can skip this step.
        #  
        # 
        #            , - ~ ~ 
        #     , '               ' ,
        #   ,           x           ,
        #  ,            |      -z    ,
        # ,             |       |     ,
        # ,     y-------o       C--x  ,   # at C, y is towards viewer
        # ,                           ,
        #  ,                         ,
        #   ,                       ,
        #     ,                  , '
        #       ' - , _ _ _ ,  '
        #
        # two ways to comput the camFlips (axes and euler angles)

        # 1. axes - map each axis (x, y, z) to target direction (expressed in src frame)
        >>> camFlips = Affine3.fromAxes([0,-1,0], [0,0,1], [-1,0,0])

        # 2. Euler angles
        # see: https://www.mecademic.com/resources/Euler-angles/Euler-angles
        # tinkertoy trick for Euler angles
        #     * place coords on paper matching target config
        #     * camFlips: find the two rotations needed to cause coords to match camera
        #       (90, -90, 0, "rxyz")
        >>> camFlipsEuler = Affine3.fromEulerAngles(90, -90, 0, "rxyz") 
        >>> camFlips.equals(camFlipsEuler)
        True

        # Verify that camFlips has the intended effect ---
        >>> d = camFlips.transformBases() # x, y, z axes in camera
        >>> np.allclose([[0,-1,0], [0,0,1], [-1,0,0]], d) # axes in camera mountspace
        True

        # Assume we tilt the camera up along a single rotational axis (its x axis)
        >>> TiltAngle = 45 # extreme example
        >>> CamPos = [0, -12, 0]  # "right" of turret origin, same height as turret origin
        >>> camTilt = Affine3.fromRotation(TiltAngle, [1, 0, 0])
        >>> camRot = Affine3.concatenate(camFlips, camTilt)
        >>> camRotQ = camRot.asQuaternion() # acquire compact rep
        >>> camRotQ.equals([0.27059805, 0.65328148, -0.65328148, -0.27059805]) # for 45 tilt
        True
        
        >>> camOffset = Affine3.fromTranslation(CamPos[0], CamPos[1], CamPos[2])
        >>> camToMount = Affine3.concatenate(camOffset, camRot)

        # Verify that the origin in camera space maps to the mount position
        >>> o = camToMount.transformPoints([[0,0,0]])[0]
        >>> np.allclose(o, CamPos)
        True

        # Verify that the turret mountpoint maps to the camera origin
        >>> mountToCamera = camToMount.asInverse()
        >>> o = mountToCamera.transformPoints([CamPos]) 
        >>> np.allclose(o[0], [0,0,0]) # verifies this is camspace origin
        True

        # Verify that the camera tilt works as expected. 
        # The vector [0, 0 ,-10] should transform to [7.071068, 0, 7.071068]
        >>> o = camToMount.transformVectors([[0,0,-10]])[0]
        >>> np.allclose(o, [7.071068, 0, 7.071068])
        True

        # Here we test point transformations.  Since the camera is offset
        # from turret origin, we expect points to be as well.
        # The point [0, 0, -120] 
        >>> tgtPtCam = [0, 0, -120] # center of camera 12 ft away
        >>> tgtPtMount = camToMount.transformPoints([tgtPtCam])[0]
        >>> np.allclose(CamPos[1], tgtPtMount[1]) # y coords match
        True

        # Check for non-zero angle between tgtPtMount and x axis
        >> cosAngle = np.dot(Vec3.normalize(tgPtCam), [1, 0, 0]]
        >> cosAngle > 0.001
        True

        """

        camFlips = Affine3.fromAxes([0,-1,0], [0,0,1], [-1,0,0])
        camTilt = Affine3.fromRotation(camTilt, [1, 0, 0])
        # Combine camFlips and camTitle, result is camRot
        camRot = Affine3.concatenate(camFlips, camTilt)
        # Produce the full camera transformation
        camOffset = Affine3.fromTranslation(camPos[0], camPos[1], camPos[2])
        camToMount = Affine3.concatenate(camOffset, camRot)
        return camToMount

    def _createMountToRobot(self):
        """
        # 
        # Robot coords (z is up)    
        #                           
        #           y               
        #       .___|___.          
        # Back  |   |   |  Front      
        #    x---T  o-----x      turret points opposite robot front, aim-angle
        #       ||______|        varies according to targeting requirements
        #        y             
        #
        >>> t2rRot = Affine3.fromRotation(180, [0,0,1])
        >>> t2rOffset = Affine3.fromTranslation(-15, -5, 0) # turret origin offset from robot origin
        >>> turretToRobot = Affine3.concatenate(t2rOffset, t2rRot)
        >>> dirs = turretToRobot.transformBases()
        >>> np.allclose(dirs, [[-1, 0, 0], [0, -1, 0], [0, 0, 1]])
        True
        >>> pts = turretToRobot.transformPoints([[0, 0, 0]])
        >>> np.allclose(pts[0], [-15, -5, 0])
        True
        """
        m2rRot = Affine3.fromRotation(180, [0,0,1]) # turret front points opposite robot front
        m2rOff = Affine3.fromTranslation(-15, -5, 0) # turret origin offset from robot origin
        m2r = Affine3.concatenate(m2rOff, m2rRot)
        return m2r

if __name__ == "__main__":
    import doctest
    import math
    import numpy as np
    doctest.testmod()
