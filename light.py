from colour import Colour

def incidence(angle, max_angle):
    if angle > max_angle:
        return 0
    if angle == 0:
        return 1
    rel_strength = ((max_angle - angle) / max_angle)
    return rel_strength

class GlobalLight():
    def __init__(self, vector, colour, strength, max_angle, func=0):
        self.vector = vector         # angle light is coming from
        self.colour = colour
        self.strength = strength     # 0-1
        self.max_angle = max_angle   # the greatest angle light is reflected from - eg 90 degrees
        self.func = func             # 0: linear
    
    def relativeStrength(self, angle):
        if self.func == 0:
            return self.colour.scaleRGB(incidence(angle, self.max_angle) * self.strength)


class PointLight():
    def __init__(self, id, position, colour, strength, max_angle, func=0):
        self.id = id            # set id to object id if object is emitting light
        self.position = position     # point of origin
        self.colour = colour
        self.strength = strength     # 0-1
        self.max_angle = max_angle
        self.func = func                # 0: linear / inverse square rule

    def relativeStrength(self, angle, distance):
        if self.func == -1:
            return self.colour.scaleRGB(incidence(angle, self.max_angle) * self.strength)
        if self.func == 0:
            return self.colour.scaleRGB(incidence(angle, self.max_angle) * self.strength / distance)