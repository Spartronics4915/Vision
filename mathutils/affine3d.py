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
    
    """
    sBases = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

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
    def fromEulerAngles(a, b, c, order):
        """
        return Affine3d representing rotation by angles a, b, c applied
        according to order:  "rxyz", "syxy" (rotating or static frame)
        """
        return Affine3d(xform.euler_matrix(math.radians(a), math.radians(b), 
                                           math.radians(c), order))
                                           
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

    def invert(self):
        self.matrix = xform.inverse_matrix(self.matrix)
        return self # chainable

    def asInverse(self):
        return Affine3d(xform.inverse_matrix(self.matrix))
    
    def asAffine2d(self):
        """return a 2d representation of 
        """

    # --------------------------------------------------------------    
    def transformPoints(self, pts):
        """return an array of points transformed by my transformation matrix.
        pts is assumed to be an array of triples.
        """
        result = np.array(pts, dtype=np.float32)
        i = 0
        for p3 in pts:
            # p3 to p4 (so dot works)
            if isinstance(p3, list):
                p4 = p3 + [1]
            else:
                # assume its an np array
                p4 = p3.tolist() + [1] # -> a point
            npt = self.matrix.dot(p4)[:3] 
            # back to p3
            result[i] = npt # npt type s np.array, should we issue tolist()?
            i+=1
        return result

    def transformBases(self):
        return self.transformVectors(self.sBases)

    def transformVectors(self, dirs):
        """return an array of points transformed by my transformation matrix.
        dirs is assumed to be an array of triples. Might be a good idea of
        they are unit-length (ie: normalized)
        """
        result = np.array(dirs, dtype=np.float32)
        i = 0
        for d3 in dirs:
            # d3 to d4 (so dot works)
            if isinstance(d3, list):
                d4 = d3 + [0]  # 0 -> a vector
            else:
                # assume its an np array
                d4 = d3.tolist() + [0]
            ndir = self.matrix.dot(d4)[:3] 
            # back to d3
            result[i] = ndir # npt type s np.array, should we issue tolist()?
            i+=1
        return result

if __name__ == "__main__":
    import doctest
    doctest.testmod()
