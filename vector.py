################################################################################
# vector.py                                                                    #
# basic vector classes                                                         #
#                                                                              #
# author:   Jared Ketterer                                                     #
# created:  22nd April 2017                                                    #
# liscense: CC 4.0 BY SA                                                       #
################################################################################
import math

__doc__ = """2D, 3D & 4D vector classes"""

class vec2:
    """2D vector class"""
    def __init__(self, x=0, y=0):
        if isinstance(x, list) or isinstance(x, tuple) and len(x) == 2:
            self.x, self.y = x
        elif isinstance(x, vec2):
            self.x, self.y = x.x, x.y
        else:
            self.x, self.y = x, y

    def __abs__(self):
        return self.magnitude()

    def __add__(self, other):
        try:
            other = vec2(other)
        except:
            raise TypeError("unsupported operand type(s) for +: 'vec2' and '" + other.__class__.__name__ + "'")
        return vec2(self.x + other.x, self.y + other.y)
        
    def __eq__(self, other):
        if isinstance(other, vec2):
            if [self.x, self.y] == [other.x, other.y]:
                return True
        elif isinstance(other, int) or isinstance(other, float):
            if self.magnitude() == other:
                return True
        return False

    def __floordiv__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return vec2(self.x // other, self.y // other)
        raise TypeError("unsupported operand type(s) for //: 'vec2' and '" + other.__class__.__name__ + "'")

    def __getitem__(self, index):
        return [self.x, self.y][index]

    def __iter__(self):
        return iter([self.x, self.y])

    def __len__(self):
        return 2

    def __mul__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return vec2(self.x * other, self.y * other)
        elif isinstance(other, vec2) or isinstance(other, list) or isinstance(other, tuple):
            raise NotImplementedError('vec2 cross product not implemented.')
        else:
            raise TypeError("unsupported operand type(s) for *: 'vec2' and '" + other.__class__.__name__ + "'")

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
            raise TypeError("unsupported operand type(s) for -: 'vec2' and '" + other.__class__.__name__ + "'")
        return vec2(self.x - other.x, self.y - other.y)
        
    def __truediv__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return vec2(self.x / other, self.y / other)
        elif isinstance(other, vec2):
            raise ArithmeticError('Cannot divide vector by another vector.')
        raise TypeError("unsupported operand type(s) for /: 'vec2' and '" + other.__class__.__name__ + "'")

    def magnitude(self):
        """Length of vector"""
        return math.sqrt(self.x**2 + self.y**2)

    def normalise(self):
        """Normalises (mutates) and returns the vector"""
        m = self.magnitude()
        if m != 0:
            self.x, self.y = self.x/m, self.y/m
        return self

    def sqrmagnitude(self):
        """Magnitude without sqrt. For quick comparisions"""
        return self.x**2 + self.y**2


class vec3:
    """3D vector class"""
    def __init__(self, x=0, y=0, z=0):
        if isinstance(x, list) or isinstance(x, tuple) and len(x) == 3:
            self.x, self.y, self.z = x
        elif isinstance(x, vec3):
            self.x, self.y, self.z = x.x, x.y, x.z
        else:
            self.x, self.y, self.z = x, y, z

    def __abs__(self):
        return self.magnitude()

    def __add__(self, other):
        try:
            other = vec3(other)
        except:
            raise TypeError("unsupported operand type(s) for +: 'vec3' and '"  + other.__class__.__name__ + "'")
        x = math.fsum([self.x, other.x])
        y = math.fsum([self.y, other.y])
        z = math.fsum([self.z, other.z])
        return vec3(x, y, z)

    def __eq__(self, other):
        if isinstance(other, vec3):
            if [self.x, self.y, self.z] == [other.x, other.y, other.z]:
                return True
        elif isinstance(other, int) or isinstance(other, float):
            if self.magnitude() == other:
                return True
        return False

    def __floordiv__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return vec3(self.x // other, self.y // other, self.z // other)
        elif isinstance(other, vec3):
            raise ArithmeticError('Cannot divide vector by another vector.')
        raise TypeError("unsupported operand type(s) for //: 'vec3' and '"  + other.__class__.__name__ + "'")

    def __getitem__(self, index):
        return [self.x, self.y, self.z][index]

    def __iter__(self):
        return iter([self.x, self.y, self.z])

    def __len__(self):
        return 3

    def __mul__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return vec3(self.x * other, self.y * other, self.z * other)
        else:
            try:
                other = vec3(other)
            except:
                raise TypeError("unsupported operand type(s) for *: 'vec3' and '"  + other.__class__.__name__ + "'")
            x = math.fsum([self.y * other.z, -self.z * other.y])
            y = math.fsum([self.z * other.x, -self.x * other.z])
            z = math.fsum([self.x * other.y, -self.y * other.x])
            return vec3(x, y, z)
        
    def __neg__(self):
        return vec3(-self.x, -self.y, -self.z)

    def __repr__(self):
        return str([self.x, self.y, self.z])

    def __rmul__(self, other):
        try:
            vec3(other)
        except TypeError:
            raise TypeError("unsupported operand type(s) for *: 'vec3' and '"  + other.__class__.__name__ + "'")
        finally:
            return self.__mul__(other)

    def __sub__(self, other):
        try:
            other = vec3(other)
        except:
            raise TypeError("unsupported operand type(s) for -: 'vec3' and '"  + other.__class__.__name__ + "'")
        return vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __truediv__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return vec3(self.x / other, self.y / other, self.z / other)
        elif isinstance(other, vec3):
            raise ArithmeticError('Cannot divide vector by another vector.')
        raise TypeError("unsupported operand type(s) for /: 'vec3' and '"  + other.__class__.__name__ + "'")

    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalise(self):
        m = self.magnitude()
        if m != 0:
            self.x, self.y, self.z = self.x/m, self.y/m, self.z/m
        return self

    def sqrmagnitude(self):
        """faster magnitude without sqrt()"""
        return self.x**2 + self.y**2 + self.z**2


class vec4:
    """Quaternion class"""
    def __init__(self, w=0, x=0, y=0, z=0):
        if (isinstance(w, list) or isinstance(w, tuple)) and len(w) == 4:
            self.w, self.x, self.y, self.z = w
        elif isinstance(w, list) or isinstance(w, tuple) and len(w) == 3:
            self.w = 1
            self.x, self.y, self.z = w
        elif isinstance(w, vec3):
            self.w = 1
            self.x, self.y, self.z = w
        elif isinstance(x, list) or isinstance(x, tuple) or isinstance(x, vec3):
            self.w = w
            self.x = x[0]
            self.y = x[1]
            self.z = x[2]
        elif isinstance(w, vec4):
            self.w, self.x, self.y, self.z = x.w, x.x, x.y, x.z
        else:
            self.w, self.x, self.y, self.z = w, x, y, z

    def __add__(self, other):
        try:
            other = vec4(other)
        except:
            raise TypeError("unsupported operand type(s) for +: 'vec4' and '"  + other.__class__.__name__ + "'")
        return vec4(self.w + other.w, self.x + other.x, self.y + other.y, self.z + other.z)
        
    def __eq__(self, other):
        if isinstance(other, vec4):
            if [self.w, self.x, self.y, self.z] == [other.w, other.x, other.y, other.z]:
                return True
        elif isinstance(other, int) or isinstance(other, float):
            if self.magnitude() == other:
                return True
        return False

    def __floordiv__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return vec4(self.w // other, self.x // other, self.y // other, self.z // other)
        raise TypeError("unsupported operand type(s) for //: 'vec4' and '" + other.__class__.__name__ + "'")

    def __getitem__(self, index):#scalar = 0
        return [self.w, self.x, self.y, self.z][index]

    def __iter__(self):
        return iter([self.w, self.x, self.y, self.z])

    def __len__(self):
        return 4

    def __mul__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return vec4(self.w * other, self.x * other, self.y * other, self.z * other)
        elif isinstance(other, vec4):
            return vec4((self.w * other.w) - (self.x * other.x) - (self.y * other.y) - (self.z * other.z),
                        (self.w * other.x) + (self.x * other.w) + (self.y * other.z) - (self.z * other.y),
                        (self.w * other.y) - (self.x * other.z) + (self.y * other.w) + (self.z * other.x),
                        (self.w * other.z) + (self.x * other.y) - (self.y * other.x) + (self.z * other.w))
        elif isinstance(other, vec3):
            raise NotImplementedError('vec3 multiplication not yet implemented.')
        raise TypeError("unsupported operand type(s) for *: 'vec4' and '" + other.__class__.__name__ + "'")

    def __neg__(self):#not legit
        return vec4(-self.w, self.x, self.y, self.z) 

    def __repr__(self):
        return str([self.w, self.x, self.y, self.z])

    def __rmul__(self, other):
        return self.__mul__(other)

    def __sub__(self, other):
        try:
            other = vec4(other)
        except:
            raise TypeError("unsupported operand type(s) for -: 'vec4' and '" + other.__class__.__name__ + "'")
        return vec4(self.w - other.w, self.x - other.x, self.y - other.y, self.z - other.z)

    def __truediv__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return vec4(self.w / other, self.x / other, self.y / other, self.z / other)
        raise TypeError("unsupported operand type(s) for /: 'vec2' and '" + other.__class__.__name__ + "'")

    def conjugate(self):
        return vec4(self.w, -1 * self.x, -1 * self.y, -1 * self.z)

    def magnitude(self):
        return math.sqrt(self.sqrmagnitude())

    def normalise(self):
        m = self.magnitude()
        if m != 0:
            self.q, self.x, self.y, self.z = self.w/m, self.x/m, self.y/m, self.z/m
        return self

    def sqrmagnitude(self):
        """magnitude without sqrt()"""
        return math.fsum([self.w**2, self.x**2, self.y**2, self.z**2])

def dot(a, b):
    """Returns the dot product of two vectors"""
    if isinstance(a, vec2) and isinstance(b, vec2):
        return math.fsum([a.x * b.x, a.y * b.y])
    elif isinstance(a, vec3) and isinstance(b, vec3):
        return math.fsum([a.x * b.x, a.y * b.y, a.z * b.z])
    elif isinstance(a, vec4) and isinstance(b, vec4):
        return math.fsum([a.w * b.w, a.x * b.x, a.y * b.y, a.z * b.z])
    elif isinstance(a, vec4) and isinstance(b, vec3):
        return math.fsum([a.x * b.x, a.y * b.y, a.z * b.z, a.w])
    elif isinstance(a, vec3) and isinstance(b, vec4):
        return math.fsum([a.x * b.x, a.y * b.y, a.z * b.z, b.w])
    else:
        raise TypeError(' '.join(['Cannot calculate', a.__class__.__name__, '&', b.__class__.__name__, 'dot product!']))

def dot2(a, b):
    dot_parts = []
    for i, j in zip(a, b):
        dot_parts.append(i * j)
    return math.fsum(dot_parts)

def lerp(a, b, t):
    """Interpolates between two given points by t"""
    if isinstance(a, int) or isinstance(a, float) and isinstance(b, int) or isinstance(b, float):
        return math.fsum([a, t * math.fsum([b, -a])])
    elif type(a) == type(b) and (isinstance(a, vec2) or isinstance(a, vec3) or isinstance(a, vec4)):
        return a + t * (b - a)
    else:
        raise TypeError(' '.join(['Cannot lerp', a.__class__.__name__, '&', b.__class__.__name__ + '!']))


def slerp(a, b, t):
    """Interpolates between two quaternions by t"""
    a.normalize()
    b.normalize()
    vdot = dot(a, b)
    if vdot > 0.9995: #fp accuracy magic
        return lerp(a, b, t)
    if vdot < 0.0:
        a = -a
        vdot = -vdot
    theta_0 = math.acos(math.fmod(1, vdot))   #angle between quaternions
    theta = theta_0 * t         #first vector and result angle
    c = (b - a * vdot).normalise()
    return a * math.cos(theta) + c * math.sin(theta)


def rotate(vector, angles):
    """Angles are expected to be in degrees. Inputs are expected to be vec3"""
    angles = vec3(math.radians(angles.x), math.radians(angles.y), math.radians(angles.z))
    cos_x, sin_x = math.cos(angles.x), math.sin(angles.x)
    cos_y, sin_y = math.cos(angles.y), math.sin(angles.y)
    cos_z, sin_z = math.cos(angles.z), math.sin(angles.z)
    vector = vec3(vector.x,
                  math.fsum([vector.y * cos_x, -vector.z * sin_x]),
                  math.fsum([vector.y * sin_x, vector.z * cos_x]))
    vector = vec3(math.fsum([vector.x * cos_y, vector.z * sin_y]),
                  vector.y,
                  math.fsum([vector.z * cos_y, -vector.x * sin_y]))
    vector = vec3(math.fsum([vector.x * cos_z, -vector.y * sin_z]),
                  math.fsum([vector.x * sin_z, vector.y * cos_z]),
                  vector.z)
    return vector


def rotate_vector_by_quaternion(vector, quaternion): #DODGY
    """Expects angle in degrees"""
    vector = vec3(vector)
    quaternion = vec4(quaternion)
    q = vec3(quaternion.x, quaternion.y, quaternion.z)
    theta = math.radians(quaternion.w)
    result = 2 * dot(q, vector) * q
    result += (theta ** 2 - dot(q, q)) * vector
    result += 2 * theta * q * vector
    return result


def rotate_by_normal(point, normal):
    point = vec3(point)
    vector = vec3(vector)
    pass

if __name__ == "__main__": #move final unittests elsewhere
    pass
