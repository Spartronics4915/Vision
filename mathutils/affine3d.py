import numpy as np
import math
import transformations as xform
from quaternion import *
from affine2d import *

class Affine3d(object):
    """We represent a 3D affine transformation as a 4x4 matrix."

    Lots of places to learn about affine transformations like this:    

    http://graphics.cs.cmu.edu/nsp/course/15-462/Spring04/slides/04-transform.pdf

    Examples
    >>> a = Affine3d()
    >>> b = Affine3d.fromRotation(30, [1, 0, 0])
    >>> c = Affine3d.fromTranslation(.5, 1.5, 2.5)
    >>> d = Affine3d.fromQuaternion(1,2,3,4)
    >>> e = Affine3d.fromQuaternion([1,2,3,4])
    >>> e.equals(d)
    True
    >>> f = Affine3d.fromQuaternion(Quaternion())
    >>> a.equals(f)
    True
    >>> f = Affine3d.concatenate(b, c, d)
    >>> pts = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float32)
    >>> npts = f.transformPoints(pts)
    >>> len(npts) == len(pts)
    True

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
    #       |   |  c|
    #       |   o-----x
    #       |_______| 
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
    # robotToField = Affine3d.fromRotation()
    
    """

    @staticmethod
    def fromIdentity():
        return Affine3d(xform.identity_matrix())
    
    @staticmethod
    def fromTranslation(x, y, z):
        "return Affine3d representing translation of x, y and z"
        return Affine3d(xform.translation_matrix([x, y, z]))

    @staticmethod
    def fromRotation(angle, dir):
        "return Affine3d representing rotation of angle (in degrees) around dir"
        return Affine3d(xform.rotation_matrix(math.radians(angle), dir))

    @staticmethod
    def fromQuaternion(*q):
        """return Affine3d representing rotation via quaternion.
        See Quaternion for a variety of methods to describe rotations.
        """
        if(len(q) == 1):
            q = q[0]
        if isinstance(q, Quaternion):
            q = q.q # member of Quaternion
        return Affine3d(xform.quaternion_matrix(q))

    @staticmethod
    def concatenate(*objs):
        "return Affine3d representing concatenation of Affine3ds"
        mats = [x.matrix for x in objs]
        return Affine3d(xform.concatenate_matrices(*mats))
    
    # XXX: add more factories (scale, reflection, shear)

    def __init__(self, initmat=None):
        if initmat is None:
            self.matrix = xform.identity_matrix()
        else:
            self.matrix = initmat
    
    def __repr__(self):
        "for interactive prompt inspection"
        return self.matrix.__repr__()

    def __str__(self):
        "for print"
        return self.matrix.__str__()
    
    def equals(self, other):
        return np.allclose(self.matrix, other.matrix)
    
    def rotate(self, angle, dir):
        mr = xform.rotation_matrix(math.radians(angle), dir)
        self.matrix = xform.concatenate_matrices(self.matrix, mr)
        return self # chainable
    
    def translate(self, x, y, z):
        mt = xform.translation_matrix([x, y, z])
        self.matrix = xform.concatenate_matrices(self.matrix, mt)
        return self # chainable
    
    def transformPoints(self, pts):
        """return an array of points transformed by my transformation matrix.
        pts is assumed to be an array of triples.
        """
        result = np.array(pts, dtype=np.float32)
        i = 0
        for p3 in pts:
            # p3 to p4 (so dot works)
            if isinstance(p3, list)
                p4 = p3 + [1]
            else:
                # assume its an np array
                p4 = p3.tolist() + [1]
            npt = self.matrix.dot(p4)[:3] 
            # back to p3
            result[i] = npt # npt type s np.array, should we issue tolist()?
            i+=1
        return result

    def asInverse(self):
        return Affine3d(xform.inverse_matrix(self.matrix))
    
    def asAffine2d(self):
        """return a 2d representation of 
        """
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()
