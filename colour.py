class Colour():
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def getList(self):
        return [self.r, self.g, self.b]

    def addColour(self, colour):
        return Colour(self.r + colour.r, self.g + colour.g, self.b + colour.b)

    def scaleRGB(self, scale, return_type=None):
        if return_type == None:
            return Colour(self.r * scale, self.g * scale, self.b * scale)
        if return_type == 'list':
            return [round(self.r * scale), round(self.g * scale), round(self.b * scale)]
        if return_type == 'Colour':
            return Colour(round(self.r * scale), round(self.g * scale), round(self.b * scale))

    def illuminate(self, light):
        r_factor = light.r / 255
        g_factor = light.g / 255
        b_factor = light.b / 255
        return Colour(
            round(self.r * r_factor),
            round(self.g * g_factor),
            round(self.b * b_factor)
        )