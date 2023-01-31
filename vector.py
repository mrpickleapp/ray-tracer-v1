import math
import numpy as np
from numpy import sin, cos, tan, arccos

class Vector:

    @staticmethod
    def fromNpArray(array):
        return Vector(x=array[0], y=array[1], z=array[2])

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def describe(self, caption=""):
        print(f"{caption}x: {self.x}, y: {self.y}, z: {self.z}")

    def getXYZ(self):
        return self.x, self.y, self.z

    def toNpArray(self):
        return np.array([self.x, self.y, self.z])

    def addVector(self, B, inplace=False):
        if inplace == True:
            self.x += B.x
            self.y += B.y
            self.z += B.z
            return self
        return Vector(self.x + B.x, self.y + B.y, self.z + B.z)

    def subtractVector(self, B, inplace=False):
        if inplace == True:
            self.x -= B.x
            self.y -= B.y
            self.z -= B.z
            return self
        return Vector(self.x - B.x, self.y - B.y, self.z - B.z)

    def invert(self, inplace=False):
        if inplace == True:
            self.x = -self.x
            self.y = -self.y
            self.z = -self.z
            return self
        return Vector(-self.x, -self.y, -self.z)
    
    def scaleByLength(self, l, inplace=False):
        if inplace == True:
            self.x *= l
            self.y *= l
            self.z *= l
            return self
        else:
            return Vector(self.x * l, self.y * l, self.z * l)

    def distanceFrom(self, B):
        return math.sqrt((B.x - self.x)**2 + (B.y - self.y)**2 + (B.z - self.z)**2)

    def angleBetween(self, B):
        return arccos(self.dotProduct(B) / (self.magnitude() * B.magnitude()))

    def reflectInVector(self, B):
        v = self.normalise()
        normal = B.normalise()
        return v.subtractVector(normal.scaleByLength(2 * v.dotProduct(normal))).normalise()

    def refractInVector(self, B, r_index_a, r_index_b):

        # https://www.scratchapixel.com/lessons/3d-basic-rendering/introduction-to-shading/reflection-refraction-fresnel.html

        v = self.normalise()
        normal = B.normalise()
        
        n = r_index_a / r_index_b

        cosI = v.dotProduct(normal)
        if cosI < -1:
            cosI = -1
        if cosI > 1:
            cosI = 1

        if cosI < 0:
            cosI = -cosI
        
        k = 1 - n**2 * (1 - cosI**2)

        if k < 0:
            return False

        return v.scaleByLength(n).addVector(normal.scaleByLength(n * cosI - math.sqrt(k))).normalise()

    def dotProduct(self, B):
        return self.x * B.x + self.y * B.y + self.z * B.z

    def crossProduct(self, B):
        # denoted by A x B
        return Vector(
            x=self.y*B.z - self.z*B.y,
            y=self.z*B.x - self.x*B.z,
            z=self.x*B.y - self.y*B.x
        )

    def magnitude(self):
        # ||v|| denotes the length of a vector
        dotProduct = self.dotProduct(self)
        return math.sqrt(dotProduct)

    def normalise(self):
        magnitude = self.magnitude()
        return Vector(x=self.x/magnitude, y=self.y/magnitude, z=self.z/magnitude)

    def multiplyByMatrix(self, T):
        return self.fromNpArray(np.matmul(self.toNpArray(), T))

    def rotate(self, angle, inplace=False):
        a, b, c = angle.x, angle.y, angle.z
        R = np.array([
            [cos(c)*cos(b)*cos(a) - sin(c)*sin(a), cos(c)*cos(b)*sin(a) + sin(c)*cos(a), -cos(c)*sin(b)],
            [-sin(c)*cos(b)*cos(a) - cos(c)*sin(a), -sin(c)*cos(b)*sin(a) + cos(c)*cos(a), sin(c)*sin(b)],
            [sin(b)*cos(a), sin(b)*sin(a), cos(b)]
        ])
        V = np.matmul(np.array([self.x, self.y, self.z]), R)
        if inplace == True:
            self = Vector(x=V[0], y=V[1], z=V[2])
        return Vector(x=V[0], y=V[1], z=V[2])



class Angle:

    # x = rotation in the xy plane
    # y = rotation around the y axis (positive is left)
    # z = bank (positive is left)

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z