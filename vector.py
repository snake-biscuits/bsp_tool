################################################################################
# vector.py                                                                    #
# basic vector classes                                                         #
#                                                                              #
# author:   Jared Ketterer                                                     #
# created:  22nd April 2017                                                    #
# liscense: CC 4.0 BY SA                                                       #
################################################################################
# TODO: fix CW_sort
import itertools
import math

__doc__ = """2D & 3D vector classes"""

class vec2:
    """2D vector class"""
    __slots__ = ['x', 'y']
    def __init__(self, x=0, y=0):
        if hasattr(x, '__iter__'):
            self.x, self.y = x[0], x[1]
        else:
            self.x, self.y = x, y

    def __abs__(self):
        return self.magnitude()

    def __add__(self, other):
        if hasattr(other, '__iter__'):
            return vec2(*map(math.fsum, itertools.zip_longest(self, other, fillvalue=0)))
        else:
            raise TypeError(f"unsupported operand type(s) for +: 'vec2' and ''{other.__class__.__name__}'")

    def __eq__(self, other):
        if isinstance(other, vec2):
            if [*self] == [*other]:
                return True
        elif isinstance(other, vec3):
            if [*self, 0] == [*other]:
                return True
        elif isinstance(other, int) or isinstance(other, float):
            if self.magnitude() == other:
                return True
        return False

    def __format__(self, format_spec=''):
        return ' '.join([format(i, format_spec) for i in self])

    def __floordiv__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return vec2(self.x // other, self.y // other)
        raise TypeError(f"unsupported operand type(s) for //: 'vec2' and '{other.__class__.__name__}'")

    def __getitem__(self, index):
        return [self.x, self.y][index]

    def __iter__(self):
        return iter((self.x, self.y))

    def __len__(self):
        return 2

    def __mul__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return vec2(self.x * other, self.y * other)
        elif hasattr(other, '__iter__'):
            raise NotImplementedError('vec2 cross product not implemented.')
        else:
            raise TypeError(f"unsupported operand type(s) for *: 'vec2' and '{other.__class__.__name__}'")

    def __neg__(self):
        return vec2(-self.x, -self.y)

    def __repr__(self):
        return str([self.x, self.y])

    def __rmul__(self, other):
        return self.__mul__(other)

    def __sub__(self, other):
        try:
            other = vec2(other)
        except:
            raise TypeError(f"unsupported operand type(s) for -: 'vec2' and '{other.__class__.__name__}'")
        return vec2(*map(math.fsum, zip(self, -other)))

    def __truediv__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return vec2(self.x / other, self.y / other)
        elif hasattr(other, '__iter__'):
            raise ArithmeticError('Cannot divide vector by another vector.')
        raise TypeError(f"unsupported operand type(s) for /: 'vec2' and '{other.__class__.__name__}'")

    def magnitude(self):
        """length of vector"""
        return math.sqrt(self.sqrmagnitude())

    def normalise(self):
        """returns unit vector without mutating"""
        m = self.magnitude()
        if m != 0:
            return vec2(self.x/m, self.y/m)
        else:
            return self

    def rotate(self, degrees):
        """rotates clockwise on Z-axis"""
        theta = math.radians(degrees)
        cos_theta = math.cos(theta)
        sin_theta = math.sin(theta)
        x = round(math.fsum([self[0] * cos_theta, self[1] * sin_theta]), 6)
        y = round(math.fsum([self[1] * cos_theta, -self[0] * sin_theta]), 6)
        return vec2(x, y)

    def sqrmagnitude(self):
        """Magnitude without sqrt. For quick comparisions"""
        return math.fsum([i ** 2 for i in self])


class vec3:
    """3D vector class"""
    __slots__ = ['x', 'y', 'z']
    def __init__(self, x=0, y=0, z=0):
        if hasattr(x, '__iter__'):
            self.x, self.y, self.z = x[0], x[1], x[2]
        else:
            self.x, self.y, self.z = x, y, z

    def __abs__(self):
        return self.magnitude()

    def __add__(self, other):
        try:
            other = vec3(other)
        except:
            raise TypeError(f"unsupported operand type(s) for +: 'vec3' and '{other.__class__.__name__}'")
        return vec3(*map(math.fsum, zip(self, other)))

    def __eq__(self, other):
        if isinstance(other, vec2):
            if [*self] == [*other, 0]:
                return True
        elif isinstance(other, vec3):
            if [*self] == [*other]:
                return True
        elif isinstance(other, int) or isinstance(other, float):
            if self.magnitude() == other:
                return True
        return False

    def __format__(self, format_spec=''):
        return ' '.join([format(i, format_spec) for i in self])

    def __floordiv__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return vec3(self.x // other, self.y // other, self.z // other)
        elif hasattr(other, '__iter__'):
            raise ArithmeticError('Cannot divide vector by another vector.')
        raise TypeError(f"unsupported operand type(s) for //: 'vec3' and '{other.__class__.__name__}'")

    def __getitem__(self, index):
        return [self.x, self.y, self.z][index]

    def __iter__(self):
        return iter((self.x, self.y, self.z))

    def __len__(self):
        return 3

    def __mul__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return vec3(*[i * other for i in self])
        elif hasattr(other, '__iter__'):
            return vec3(math.fsum([self[1] * other[2], -self[2] * other[1]]),
                        math.fsum([self[2] * other[0], -self[0] * other[2]]),
                        math.fsum([self[0] * other[1], -self[1] * other[0]]))
        raise TypeError(f"unsupported operand type(s) for *: 'vec3' and '{other.__class__.__name__}'")

    def __neg__(self):
        return vec3(-self.x, -self.y, -self.z)

    def __repr__(self):
        return str([self.x, self.y, self.z])

    def __rmul__(self, other):
        return self.__mul__(other)

    def __sub__(self, other):
        try:
            other = vec3(other)
        except:
            raise TypeError(f"unsupported operand type(s) for -: 'vec3' and '{other.__class__.__name__}'")
        return vec3(*map(math.fsum, zip(self, -other)))

    def __truediv__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return vec3(self.x / other, self.y / other, self.z / other)
        elif hasattr(other, '__iter__'):
            raise ArithmeticError('Cannot divide vector by another vector.')
        raise TypeError(f"unsupported operand type(s) for /: 'vec3' and '{other.__class__.__name__}'")

    def magnitude(self):
        """length of vector"""
        return math.sqrt(self.sqrmagnitude())

    def normalise(self):
        """returns unit vector without mutating"""
        m = self.magnitude()
        if m != 0:
            return vec3(self.x/m, self.y/m, self.z/m)
        else:
            return self

    def rotate(self, x, y, z):
        angles = [math.radians(i) for i in (x, y, z)]
        cos_x, sin_x = math.cos(angles[0]), math.sin(angles[0])
        cos_y, sin_y = math.cos(angles[1]), math.sin(angles[1])
        cos_z, sin_z = math.cos(angles[2]), math.sin(angles[2])
        out = vec3(self[0], #indices means any iterable can use this function
                   math.fsum([self[1] * cos_x, -self[2] * sin_x]),
                   math.fsum([self[1] * sin_x, self[2] * cos_x]))
        out = vec3(math.fsum([out.x * cos_y, out.z * sin_y]),
                   out.y,
                   math.fsum([out.z * cos_y, out.x * sin_y]))
        out = vec3(math.fsum([out.x * cos_z, -out.y * sin_z]),
                   math.fsum([out.x * sin_z, out.y * cos_z]),
                   out.z)
        out = vec3(*[round(i, 6) for i in out])
        return out

    def sqrmagnitude(self):
        """for fast compares where the actual length isn't needed"""
        return math.fsum([i ** 2 for i in self])


def dot(a, b):
    """Returns the dot product of two vectors"""
    if hasattr(a, '__iter__') and hasattr(b, '__iter__'):
        return math.fsum([i * j for i, j in itertools.zip_longest(a, b, fillvalue=0)])
    else:
        raise TypeError(f'Cannot dot {type(a)} & {type(b)}')

def lerp(a, b, t):
    """Interpolates between two given points by t"""
    types = (type(a), type(b))
    if int in types or float in types:
        return math.fsum([a, t * math.fsum([b, -a])])
    if hasattr(a, '__iter__') and hasattr(b, '__iter__'):
        out = []
        for i, j in itertools.zip_longest(a, b, fillvalue=0):
            out.append(lerp(i, j, t))
        return out
    else:
        raise TypeError(f'Cannot lerp {type(a)} & {type(b)}')

def angle_between(a, b):
    dot(a, b) / (a.magnitude() * b.magnitude())

def CW_sort(vectors, normal): # doesn't do it's job properly
    """vec3 only, for vec2 use a normal of (0, 0, 1)\nfor CCW, invert the normal"""
    O = sum(vectors, vec3()) / len(vectors)
    centered_vectors = [v - O for v in vectors]
    A = centered_vectors[0]
    indexed_thetas = {dot(A * B, normal): vectors[i+1] for i, B in enumerate(vectors[1:])}
    sorted_vectors = [vectors[0]]
    sorted_vectors += [indexed_thetas[key] for key in sorted(indexed_thetas)]
    return sorted_vectors

# EXTREMELY BORKED
##def CW_sort_index(vectors, indices, normal): #Doesn't handle >180 degrees (or direction of rotation)
##    """expects all vector to be vec3, returns sorted indices"""
##    indexed_vectors = [vectors[index] for index in indices]
##    A = indexed_vectors[0] * N
##    print(indexed_vectors[1:], indices[1:], sep='\n')
##    #dot gives angle between two vectors but not direction
##    #is also innacurate for angles >= 180 degrees
##    #MAP NEAREST POINTS TO CREATE A NEIGHBOUR MAP?!
##    #DISCERN NEGATIVE ROTATION FROM POSITIVE!
##    theta_map = [(dot(A * B, normal): index) for B, index in zip(indexed_vectors[1:], indices[1:])]
##    #sorted() uses a function to assign list items a scalar value and sorts these
##    #theta_map just sorts by closest (rotationally) to first point
##    sorted_indices = [indices[0]]
##    sorted_indices += ...
##    return sorted_indices
    

if __name__ == "__main__":
    pass
