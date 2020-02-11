import numpy as np
import math
if __package__ is None or __package__ == "":
    import transformations as xform
    from quaternion import *
else:
    from . import transformations as xform
    from .quaternion import *

class Affine3(object):
    """We represent a 3D affine transformation as a 4x4 matrix."

    Lots of places to learn about affine transformations like this:    

    http://graphics.cs.cmu.edu/nsp/course/15-462/Spring04/slides/04-transform.pdf

    Basic idea: an affine matrix can be used to describe coordinate-system
    conversions as we have when characterizing how to convert from the
    camera coordinate-frame to the robot-coordinate frame.  Here the camera
    has a natural coordinate system and so does the robot.  The question
    we'd like to answer: what does a point (or direction) in the camera's 
    coordinate system mean to the robot?  Once we've "designed" a transformation 
    matrix, we can "multiply" (via "dot product") the point in one coordinate 
    system by the transformation matrix to obtain the point in another 
    coordinate system. But wait, there's more! We can "chain" coordinate 
    systems together to convert points from camera, then to robot, then to 
    field.  A combined matrix can be produced (by concatenate) to represent
    multiple transformations in one matrix.  We can also "invert" these 
    transformations and now we can compute where a field location should 
    appear in the camera coordinate system.

    To construct/design a matrix we must carefully consider the way that
    we must rotate one coordinate system to obtain another.  There are
    a number of ways to characterize this rotation, some more intuitive
    than others.  If you are dealing with 90 degree, rigid transformations,
    the "fromAxes" approach may be best.  Euler angles may be the most
    traditional in robotics, but multiple, sequential rotations can be difficult 
    to grasp.  Quaternions are very useful for interpolating arbitrary 3D
    rotations (and avoid "gimbal lock") but harder to design from scratch.  
    Quaternions are also a robust and compact representation for rotations.  
    So we offer/support a range of rotation specification methodologies.  
    See also the sibling Quaternion class.

    >>> a = Affine3()
    >>> b1 = Affine3.fromAxes([0, -1, 0], [0, 0, 1], [-1, 0, 0])
    >>> np.allclose(b1.transformBases(), [[0, -1, 0], [0, 0, 1], [-1, 0, 0]])
    True
    >>> b2 = Affine3.fromRotation(30, [1, 0, 0])
    >>> c = Affine3.fromTranslation(.5, 1.5, 2.5)
    >>> d = Affine3.fromQuaternion(1,2,3,4)
    >>> e = Affine3.fromQuaternion([1,2,3,4])
    >>> e.equals(d)
    True
    >>> f = Affine3.fromQuaternion(Quaternion())
    >>> a.equals(f)
    True
    >>> f = Affine3.concatenate(b2, c, d)
    >>> pts = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]]
    >>> npts = f.transformPoints(pts)
    >>> len(npts) == len(pts)
    True
    >>> str = f.asString()
    >>> ff = Affine3.fromString(str)
    >>> ff.equals(f)
    True
    
    """
    sBases = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

    @staticmethod
    def fromIdentity():
        return Affine3(xform.identity_matrix())

    @staticmethod
    def fromString(s):
        """assume s looks like:  'o 0.3 0.5 -2 q 1 2 3 4'  
         nb: we can't represent skew and scale but for our purposes
             this is fine.
        """
        vals = s.split(" ")
        assert(len(vals) == 9)
        assert(vals[0] == "o") 
        assert(vals[4] == "q")
        x = [float(vals[1]), float(vals[2]), float(vals[3])]
        q = [float(vals[5]), float(vals[6]), float(vals[7]), float(vals[8])]
        om = xform.translation_matrix(x)
        qm = xform.quaternion_matrix(q)
        result = xform.concatenate_matrices(om, qm)
        return Affine3(result)

    @staticmethod
    def fromTranslation(x, y, z):
        "return Affine3 representing translation of x, y and z"
        return Affine3(xform.translation_matrix([x, y, z]))

    @staticmethod
    def fromRotation(angle, dir):
        """return Affine3 representing rotation of angle (in degrees) around dir
        """
        return Affine3(xform.rotation_matrix(math.radians(angle), dir))

    def fromAxes(xtgt, ytgt, ztgt):
        """return Affine3 representing rotation of axes to targets
        NB: all targets should be normalized (unit length).
        """
        m = xform.identity_matrix()
        m[0][0] = xtgt[0]
        m[1][0] = xtgt[1]
        m[2][0] = xtgt[2]
        m[0][1] = ytgt[0]
        m[1][1] = ytgt[1]
        m[2][1] = ytgt[2]
        m[0][2] = ztgt[0]
        m[1][2] = ztgt[1]
        m[2][2] = ztgt[2]
        return Affine3(m)

    @staticmethod
    def fromEulerAngles(a, b, c, order):
        """
        return Affine3 representing rotation by angles a, b, c applied
        according to order:  "rxyz", "syxy" (rotating or static frame)
        """
        return Affine3(xform.euler_matrix(math.radians(a), math.radians(b), 
                                           math.radians(c), order))
                                           
    @staticmethod
    def fromQuaternion(*q):
        """return Affine3 representing rotation via quaternion.
        See Quaternion for a variety of methods to describe rotations.
        """
        if(len(q) == 1):
            q = q[0]
        if isinstance(q, Quaternion):
            q = q.q # access member of Quaternion
        return Affine3(xform.quaternion_matrix(q))

    @staticmethod
    def concatenate(*objs):
        "return Affine3 representing concatenation of Affine3s"
        mats = [x.matrix for x in objs]
        return Affine3(xform.concatenate_matrices(*mats))
    
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
    
    def getTranslation(self):
        xlate = xform.decompose_matrix(self.matrix)[3]
        return (xlate[0], xlate[1], xlate[2])
    
    def _decompose(self):
        """ returns tuple of:
            scale : vector of 3 scaling factors
            shear : list of shear factors for x-y, x-z, y-z
            angles : list of euler angles about sxyz
            translate : vector of 3
            perspective ; perspective partition
        """
        return xform.decompose_matrix(self.matrix)

    def asString(self):
        # nb: currently we assume no scales, skews, etc
        q = xform.quaternion_from_matrix(self.matrix)
        o = xform.decompose_matrix(self.matrix)[3]
        return "o %g %g %g %s" %  \
                (o[0], o[1], o[2], Quaternion(q).asString())

    def asInverse(self):
        return Affine3(xform.inverse_matrix(self.matrix))
    
    def asQuaternion(self):
        """Returns the rotational component of transform in quaternion form"""
        return Quaternion(xform.quaternion_from_matrix(self.matrix))
    
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
