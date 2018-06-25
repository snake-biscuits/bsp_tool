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
            raise TypeError(f"unsupported operand type(s) for +: 'vec2' and ''{other.__class__.__name__}'")
        return vec2(*map(math.fsum, zip(self, other)))

    def __eq__(self, other):
        if isinstance(other, vec2):
            if [self.x, self.y] == [other.x, other.y]:
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
        return iter([self.x, self.y])

    def __len__(self):
        return 2

    def __mul__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return vec2(self.x * other, self.y * other)
        elif isinstance(other, vec2) or isinstance(other, list) or isinstance(other, tuple):
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
        elif isinstance(other, vec2):
            raise ArithmeticError('Cannot divide vector by another vector.')
        raise TypeError(f"unsupported operand type(s) for /: 'vec2' and '{other.__class__.__name__}'")

    def magnitude(self):
        """Length of vector"""
        return math.sqrt(self.sqrmagnitude())

    def normalise(self):
        """Normalises (mutates) and returns the vector"""
        m = self.magnitude()
        if m != 0:
            return vec2(self.x/m, self.y/m)
        else:
            return self

    def rotate(self, degrees):
        theta = math.radians(degrees)
        cos_theta = math.cos(theta)
        sin_theta = math.sin(theta)
        x = round(math.fsum([self[0] * cos_theta, self[1] * sin_theta]), 6)
        y = round(math.fsum([self[1] * cos_theta, -self[0] * sin_theta]), 6)
        return vec2(x, y)

    def sqrmagnitude(self):
        """Magnitude without sqrt. For quick comparisions"""
        return math.fsum([pow(i, 2) for i in self])


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
            raise TypeError(f"unsupported operand type(s) for +: 'vec3' and '{other.__class__.__name__}'")
        return vec3(*map(math.fsum, zip(self, other)))

    def __eq__(self, other):
        if isinstance(other, vec3):
            if [self.x, self.y, self.z] == [other.x, other.y, other.z]:
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
        elif isinstance(other, vec3):
            raise ArithmeticError('Cannot divide vector by another vector.')
        raise TypeError(f"unsupported operand type(s) for //: 'vec3' and '{other.__class__.__name__}'")

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
                raise TypeError(f"unsupported operand type(s) for *: 'vec3' and '{other.__class__.__name__}'")
            return vec3(math.fsum([self.y * other.z, -self.z * other.y]),
                        math.fsum([self.z * other.x, -self.x * other.z]),
                        math.fsum([self.x * other.y, -self.y * other.x]))

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
        elif isinstance(other, vec3):
            raise ArithmeticError('Cannot divide vector by another vector.')
        raise TypeError(f"unsupported operand type(s) for /: 'vec3' and '{other.__class__.__name__}'")

    def magnitude(self):
        return math.sqrt(self.sqrmagnitude())

    def normalise(self):
        m = self.magnitude()
        if m != 0:
            return vec3(self.x/m, self.y/m, self.z/m)
        else:
            return self

    def rotate(self, *degrees):
        """Degrees must be an iterable with at least 3 items"""
        angles = [*map(math.radians, degrees)]
        cos_x, sin_x = math.cos(angles[0]), math.sin(angles[0])
        cos_y, sin_y = math.cos(angles[1]), math.sin(angles[1])
        cos_z, sin_z = math.cos(angles[2]), math.sin(angles[2])
        out = vec3(self[0],
                   math.fsum([self[1] * cos_x, -self[2] * sin_x]),
                   math.fsum([self[1] * sin_x, self[2] * cos_x]))
        out = vec3(math.fsum([out.x * cos_y, out.z * sin_y]),
                   out.y,
                   math.fsum([out.z * cos_y, out.x * sin_y]))
        out = vec3(math.fsum([out.x * cos_z, -out.y * sin_z]),
                   math.fsum([out.x * sin_z, out.y * cos_z]),
                   out.z)
        out.x = round(out.x, 6)
        out.y = round(out.y, 6)
        out.z = round(out.z, 6)
        return out

    def sqrmagnitude(self):
        """for fast compares where the actual length isn't needed"""
        return math.fsum([pow(i, 2) for i in self])


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
            raise TypeError(f"unsupported operand type(s) for +: 'vec4' and '{other.__class__.__name__}'")
        return vec4(self.w + other.w, self.x + other.x, self.y + other.y, self.z + other.z)

    def __eq__(self, other):
        if isinstance(other, vec4):
            if [self.w, self.x, self.y, self.z] == [other.w, other.x, other.y, other.z]:
                return True
        elif isinstance(other, int) or isinstance(other, float):
            if self.magnitude() == other:
                return True
        return False

    def __format__(self, format_spec=''):
        return ' '.join([format(i, format_spec) for i in self])

    def __floordiv__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return vec4(self.w // other, self.x // other, self.y // other, self.z // other)
        raise TypeError(f"unsupported operand type(s) for //: 'vec4' and '{other.__class__.__name__}'")

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
        raise TypeError(f"unsupported operand type(s) for *: 'vec4' and '{other.__class__.__name__}'")

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
            raise TypeError(f"unsupported operand type(s) for -: 'vec4' and '{other.__class__.__name__}'")
        return vec4(self.w - other.w, self.x - other.x, self.y - other.y, self.z - other.z)

    def __truediv__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return vec4(self.w / other, self.x / other, self.y / other, self.z / other)
        raise TypeError(f"unsupported operand type(s) for /: 'vec4' and '{other.__class__.__name__}'")

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
        return math.fsum([pow(i, 2) for i in self])


def dot(a, b):
    """Returns the dot product of two vectors"""
    if len(a) == len(b):
        return math.fsum([i * j for i, j in zip(a, b)])
    #itertools.zip_longest instead of repeating the solution?
    elif isinstance(a, vec4) and isinstance(b, vec3):
        return math.fsum([a.x * b.x, a.y * b.y, a.z * b.z, a.w])
    elif isinstance(a, vec3) and isinstance(b, vec4):
        return math.fsum([a.x * b.x, a.y * b.y, a.z * b.z, b.w])
    else:
        raise TypeError(f'Types cannot be dotted: {type(a)} & {type(b)}')

def lerp(a, b, t):
    """Interpolates between two given points by t"""
    types = type(a), type(b)
    if int in types or float in types:
        return math.fsum([a, t * math.fsum([b, -a])])
    elif len(a) == len(b):
        out = []
        for i, j in zip(a, b):
            out.append(lerp(i, j, t))
        return out
    else:
        raise TypeError(f'Types do not match: {type(a)} & {type(b)}')

def slerp(a, b, t):#hard to read
    """Interpolates between two quaternions by t"""
    a = vec4(a)
    b = vec4(b)
    a.normalize()
    b.normalize()
    vdot = dot(a, b)
    if vdot > 0.9995:
        return lerp(a, b, t)
    if vdot < 0.0:
        a = -a
        vdot = -vdot
    1 % vdot                    #clamp to range of acos() [-1, 1]
    theta_0 = math.acos(vdot)   #theta_0 = angle between v1 & v2
    theta = theta_0 * t         #theta = angle between v1 and result
    c = (b - a * vdot).normalise()
    return a * math.cos(theta) + c * math.sin(theta)

def rotate_vector_by_quaternion(vector, quaternion): #DODGY
    """Expects angle in degrees"""
    q = vec3(quaternion.x, quaternion.y, quaternion.z)
    theta = math.radians(quaternion.w)
    result = 2 * dot(q, vector) * q
    result += (theta ** 2 - dot(q, q)) * vector
    result += 2 * theta * q * vector
    return result

def rotate_to_normal(point, normal, start=vec3(0, 0, 1)):
    raise NotImplementedError

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
    A = vec3(-1, 1)
    B = vec3(1, 1)
    C = vec3(1, -1)
    D = vec3(-1, -1)
    
    N = vec3(0, 0, 1)
##    winding = [0, 1, 2, 3]
##    letters = 'ABCD'
##
##    import itertools
##    for order in itertools.permutations(winding, 4):
##        sorted_indices = CW_sort_index([A, B, C, D], order, N)
##        print(f'{letters[sorted_indices[0]]}{letters[sorted_indices[1]]}\n{letters[sorted_indices[2]]}{letters[sorted_indices[3]]}\n')
##
##    print("*** UNINDEXED")
##    for order in itertools.permutations(winding, 4):
##        sorted_points = CW_sort([A, B, C, D], N)
##        print(f'{sorted_points[0]}\t{sorted_points[1]}\n{sorted_points[2]}\t{sorted_points[3]}\n')


    A = (vec3() - A).normalise()
    B = (vec3() - B).rotate(0, 0, -45).normalise()
    theta = dot(A, B)
    print(f'<{A:.2f}>, <{B:.2f}> theta = {theta}')
