import transformations as xform
import numpy as np
import math

class Quaternion:
    """Robust representation of 3D rotation

    Quaternions w+ix+jy+kz are represented as [w, x, y, z].

    Examples:
    >>> a = Quaternion()
    >>> np.allclose(np.identity(4), a.asMatrix())
    True
    >>> b = Quaternion.fromAxisAngle(45, [0, 0, 1])
    >>> m = b.asMatrix()
    >>> q1 = Quaternion.fromMatrix(np.identity(4))
    >>> a.equals(q1)
    True
    >>> q2 = Quaternion.fromAngles(45, 0, 0)
    >>> q3 = Quaternion.fromAngles(0, 45, 0)
    >>> q4 = Quaternion.fromAngles(0, 0, 45)
    """

    @staticmethod
    def fromMatrix(matrix, isprecise=False):
        return Quaternion(xform.quaternion_from_matrix(matrix, isprecise))

    @staticmethod
    def fromAxisAngle(angle, axis):
        """ return quaternion for rotation (degrees) about axis 
        """
        return Quaternion(xform.quaternion_about_axis(math.radians(angle), axis))
    
    @staticmethod
    def fromAngles(ai, aj, ak, axes='sxyz'):
        m = xform.euler_matrix(math.radians(ai), 
                               math.radians(aj), 
                               math.radians(ak), 
                               axes)
        q = xform.quaternion_from_matrix(m) 
        return Quaternion(q)

    def __init__(self, initq=None):
        if initq is None:
            self.q = np.array([1,0,0,0], dtype=np.float32) # produces identity matrix
        else:
            self.q = initq

    def __repr__(self):
        "for interactive prompt inspection"
        return self.q.__repr__()

    def __str__(self):
        "for print"
        return "[ %f %f %f %f ]" % (self.q[0], self.q[1], self.q[2], self.q[3])
    
    def equals(self, other):
        if isinstance(other, Quaternion):
            return xform.is_same_quaternion(self.q, other.q)
        else:
            return xform.is_same_quaternion(self.q, other)
    
    def asMatrix(self):
        """ return a numpy array, to convert to Affine3, use Affine3.fromQuaternion
        """
        return xform.quaternion_matrix(self.q)

    def multiply(self, other):
        """
        >>> q1 = Quaternion([4, 1, -2, 3])
        >>> q2 = Quaternion([8, -5, 6, 7])
        >>> q3 = q1.multiply(q2)
        >>> q3.equals(Quaternion([28, -44, -14, 48]))
        True
        """
        return Quaternion(xform.quaternion_multiply(self.q, other.q))

if __name__ == "__main__":
    import doctest
    doctest.testmod()