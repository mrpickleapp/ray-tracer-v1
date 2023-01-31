import math
import numpy as np

from vector import Vector, Angle
from object import Sphere
from colour import Colour

class Intersection():

    @staticmethod
    def nearestIntersection(intersections):
        nearestIntersection = None
        for intersection in intersections:
            if intersection.intersects == True:
                if nearestIntersection == None:
                    nearestIntersection = intersection
                else:
                    if intersection.distance < nearestIntersection.distance:
                        nearestIntersection = intersection
        return nearestIntersection

    def __init__(self, intersects=False, distance=None, point=None, normal=None, object=None, bounces=0, through_count=0):
        self.intersects = intersects
        self.distance = distance
        self.point = point
        self.normal = normal
        self.object = object
        self.bounces = bounces
        self.through_count=through_count

    def directionRGB(self):
        # ray has not landed on anything, but might get light from light sources

        # test
        return Colour(0, 255,)

    def terminalRGB(self, spheres, background_colour=Colour(0, 0, 0), global_light_sources=[], point_light_sources=[], max_bounces=0):
        # colour of the thing landed on
        reflectivity, transparency, emitivity = self.object.material.reflective, self.object.material.transparent, self.object.material.emitive 
        
        illumination = self.object.colour.scaleRGB(emitivity)      # does not take distance from camera into account

        for light in global_light_sources:
            angle_to_light = self.normal.angleBetween(light.vector)
            illumination = illumination.addColour(light.relativeStrength(angle_to_light))
        
        for light in point_light_sources:
            if self.object.id != light.id:
                vector_to_light = light.position.subtractVector(self.point)
                ray_to_light = Ray(
                    origin=self.point,
                    D=vector_to_light
                )
                ray_to_light_terminus = ray_to_light.nearestSphereIntersect(spheres, suppress_ids=[self.object.id], max_bounces=max_bounces)

                if ray_to_light_terminus != None:
                    # clear line of sight
                    if ray_to_light_terminus.object.id == light.id:

                        angle_to_light = self.normal.angleBetween(vector_to_light)
                        distance_to_light = vector_to_light.magnitude()
                        illumination = illumination.addColour(light.relativeStrength(angle_to_light, distance_to_light))

        # resolve final total of illumination
        return background_colour.addColour(self.object.colour.illuminate(illumination))


class Ray():
    def __init__(self, origin, D):
        self.origin = origin
        self.D = D.normalise()  # direction in vector

    def sphereDiscriminant(self, sphere, point=0):      # set point to 1 when you want the second intersection
        O = self.origin
        D = self.D
        C = sphere.centre
        r = sphere.radius
        L = C.subtractVector(O)

        tca = L.dotProduct(D)
        if tca < 0:     # intersection is behind origin - this doesn't work when line is inside sphere
           return Intersection()

        d = None
        try:
            d = math.sqrt(L.dotProduct(L) - tca**2)
        except:
            d = 0       # crude error protection - in case D & L are too similar
        if d > r:       # line misses sphere
            return Intersection()

        thc = math.sqrt(r**2 - d**2)
        t0 = tca - thc      # distance to first intersection
        t1 = tca + thc      # distance to second intersection

        tmin = [t0, t1][point]

        phit = O.addVector(D.scaleByLength(tmin))     # point of intersection
        nhit = phit.subtractVector(C).normalise()     # normal of intersection

        return Intersection(
            intersects=True,
            distance = tmin,
            point = phit,
            normal = nhit,
            object = sphere
        )

    def sphereExitRay(self, sphere, intersection):

        # refract at first intersection
        refracted_ray_D = self.D.refractInVector(intersection.normal, 1, sphere.material.refractive_index)

        # get internal ray
        internal_ray = Ray(
            origin=intersection.point,
            D=refracted_ray_D
        )

        # get second intersection
        exit_intersection = internal_ray.sphereDiscriminant(sphere=sphere, point=1)

        exit_ray_D = None
        exit = False

        n = 0
        while (exit == False) & (n < 10):
            n+=1

            # refract exit ray
            exit_ray_D = refracted_ray_D.refractInVector(exit_intersection.normal.invert(), sphere.material.refractive_index, 1)

            if exit_ray_D != False:
                exit = True
            else:
                # TIR
                refracted_ray_D = refracted_ray_D.reflectInVector(exit_intersection.normal)
                # find next exit point
                exit_ray = Ray(
                    origin=exit_intersection.point,
                    D=refracted_ray_D
                )
                exit_intersection = exit_ray.sphereDiscriminant(sphere=sphere, point=1)
            
        if exit == True:

            return Ray(
                exit_intersection.point,
                exit_ray_D
            )

        # TRAPPED RAY:
        print("TRAPPED RAY:")
        self.origin.describe()
        self.D.describe()

        return None


    def nearestSphereIntersect(self, spheres, suppress_ids=[], bounces=0, max_bounces=1, through_count=0):

        intersections = []

        for i, sphere in enumerate(spheres):
            if sphere.id not in suppress_ids:
                intersections.append(self.sphereDiscriminant(sphere))

        nearestIntersection = Intersection.nearestIntersection(intersections)
        
        if nearestIntersection == None:
            return None

        if bounces > max_bounces:
            return None

        nearestIntersection.bounces = bounces
        nearestIntersection.through_count = through_count

        # NB - reflective objects return background colour if no reflections found
        if nearestIntersection.object.material.reflective == True:
            
            reflected_ray_D = self.D.reflectInVector(nearestIntersection.normal)
            
            reflected_ray = Ray(
                origin=nearestIntersection.point,
                D=reflected_ray_D
            )
            bounces += 1
            suppress_ids = [nearestIntersection.object.id]
            reflected_terminus = reflected_ray.nearestSphereIntersect(
                spheres=spheres,
                suppress_ids=suppress_ids,
                bounces=bounces,
                max_bounces=max_bounces,
                through_count=through_count
            )

            if reflected_terminus != None:
                return reflected_terminus
            
            return nearestIntersection

        # REFRACTION
        if nearestIntersection.object.material.transparent == True:

            sphere_exit_ray = self.sphereExitRay(
                sphere=nearestIntersection.object,
                intersection=nearestIntersection
            )

            if sphere_exit_ray == None:
                return None
            
            bounces += 1
            through_count += 1
            suppress_ids = [nearestIntersection.object.id]

            reflected_terminus = sphere_exit_ray.nearestSphereIntersect(
                spheres=spheres,
                suppress_ids=suppress_ids,
                bounces=bounces,
                max_bounces=max_bounces,
                through_count=through_count
            )

            if reflected_terminus != None:
                return reflected_terminus

            return None

        return nearestIntersection


