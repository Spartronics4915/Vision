import numpy as np
class Vec3(object):
    """
    A helper class for 3d points, just to hide obscure numpy syntax

    >>> vec = [1,2,3]
    >>> len = Vec3.length(vec)
    >>> np.allclose(len, 3.7416573)
    True
    >>> nlen = Vec3.normalize(Vec3.asVec3(vec))
    >>> np.allclose(nlen, len)
    True
    """

    @staticmethod
    def length(vec3):
        return np.linalg.norm(vec3, 2, -1)
    
    @staticmethod
    def asVec3(vec3):
        assert len(vec3) == 3 
        return np.array(vec3, dtype=np.float64, copy=False)

    @staticmethod
    def normalize(vec3):
        """ nb: this wont overwrite vec3 unless it's an np.array """
        len = np.linalg.norm(vec3, 2, -1)
        vec3 /= len
        return len

if __name__ == "__main__":
    import doctest
    doctest.testmod()
