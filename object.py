from colour import Colour

class Sphere():
    def __init__(self, centre, radius, material, colour=Colour(128, 128, 128), id=0):
        self.id = id
        self.centre = centre
        self.radius = radius
        self.material = material
        self.colour = colour
