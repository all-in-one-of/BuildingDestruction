# -*- coding: utf-8 -*-
'''
Created on Jul 5, 2011

@author: carlos
'''
from ExternalClasses import GeoMath
import CreateTBN
import DetermineVectors
import logging
import BoundingBox

primnumber = 29
DEBUG = False
epsilon = 0.001
class Texture(object):
    '''
    classdocs
    '''

    def __init__(self, material, absolutePoints=None, delimitedProportions=None
                  , absolutePointsNotErasable=None, OBJ=None, isDefault=False):
        reload(DetermineVectors)
        #Absolute points
        self.__absolutePoints = absolutePoints

        #Absolute points not erasables, fixed texture, not mapping
        self.__absolutePointsNotErasable = absolutePointsNotErasable

        #Relative points
        self.__delimitedProportions = delimitedProportions
        self.__material = material
        self.__OBJ = OBJ
        self.__isDefaultTexture = isDefault
        self.prim = None

    def get_prim(self):
        return self.__prim

    def set_prim(self, value):
        self.__prim = value

    def del_prim(self):
        del self.__prim

    def get_is_default_texture(self):
        return self.__isDefaultTexture

    def set_is_default_texture(self, value):
        self.__isDefaultTexture = value

    def del_is_default_texture(self):
        del self.__isDefaultTexture

    def get_absolute_points(self):
        return self.__absolutePoints

    def get_absolute_points_not_erasable(self):
        return self.__absolutePointsNotErasable

    def get_delimited_proportions(self):
        return self.__delimitedProportions

    def get_material(self):
        return self.__material

    def get_obj(self):
        return self.__OBJ

    def set_absolute_points(self, value):
        self.__absolutePoints = value

    def set_absolute_points_not_erasable(self, value):
        self.__absolutePointsNotErasable = value


    def set_delimited_proportions(self, value):
        self.__delimitedProportions = value


    def set_material(self, value):
        self.__material = value


    def set_obj(self, value):
        self.__OBJ = value


    def del_absolute_points(self):
        del self.__absolutePoints


    def del_absolute_points_not_erasable(self):
        del self.__absolutePointsNotErasable


    def del_delimited_proportions(self):
        del self.__delimitedProportions


    def del_material(self):
        del self.__material


    def del_obj(self):
        del self.__OBJ

    def checkIntersectionWithTexture(self, points, prim):
        global DEBUG
        global epsilon
        logging.debug("Start method checkIntersectionWithTexture, class Texture")
        #First we check intersection with boundingBox
        if(self.get_prim() and self.get_absolute_points()):
            param_points_bounding_box = BoundingBox.BoundingBox2D(points, prim)
            texture_bounding_box = BoundingBox.BoundingBox2D(
                                                        self.get_absolute_points(),
                                                         self.get_prim())
            intersections = (
            texture_bounding_box.intersect_bounding_box_without_limits_3D(
            param_points_bounding_box))

            if (not intersections):
                return None, None, []
        else:
            if(not self.get_prim()):
                logging.debug("Class Texture, not prim in method check intersection with texture")
            else:
                logging.debug("No object points")
                logging.debug(str(self))
                logging.debug(str(self.get_is_default_texture()))
                logging.debug(str(self.get_absolute_points()))
                logging.debug(str(self.get_absolute_points_not_erasable()))
                logging.debug(str(self.get_delimited_proportions()))
                logging.debug(str(self.get_obj()))

        pointsIntersect = []
        for n in range(len(points) - 1):
            edge = [points[n], points[n + 1]]
            for texIndex in range(len(self.absolutePoints)):
                nextTexIndex = (texIndex + 1) % len(self.absolutePoints)
                texEdge = [self.absolutePoints[texIndex], self.absolutePoints[nextTexIndex]]
                pointIntersect = GeoMath.getFalseIntersectionBetweenTwoEdges3D(edge, texEdge, prim)
                #We have to avoid first point, that surely intersect with some texture.
                #Also avoid the case where two texture are together and pattern intersect with
                #the first texture, but when 'exit' from this texture, it intersect with the
                #other texture anda pattern of length 0 is used; with this method we avoid this
                if(pointIntersect):
                    distacenToLastPoint = GeoMath.vecModul(GeoMath.vecSub(
                                        points[len(points) - 1], pointIntersect))
                    if(GeoMath.vecModul(GeoMath.vecSub(pointIntersect, points[0]))
                        > epsilon and distacenToLastPoint > epsilon):
                        pointsIntersect.append(pointIntersect)

        if(pointsIntersect):
            nearestPointIntersect = None
            #Big number
            minDistance = 999999

            #For each point we look if intersection is the minimum distance intersection
            for pointIntersect in pointsIntersect:
                distance, achieved = GeoMath.takeDistanceInTrackToPoint(points,
                                                     pointIntersect, points[0])
                if(achieved and distance < minDistance and distance > epsilon):
                    #We need the minimun distance, but to avoid errors, we have
                    # to discard the first point and the last
                    minDistance = distance
                    nearestPointIntersect = pointIntersect

            if(not nearestPointIntersect):
                minDistance = None
        else:
            nearestPointIntersect = None
            minDistance = None

        if(nearestPointIntersect):
            logging.debug('End method checkIntersectionWithTexture,'
                          'class Texture. State: Intersection')
        else:
            logging.debug('End method checkIntersectionWithTexture,'
                          'class Texture. State: No intersection')

        return minDistance, nearestPointIntersect, pointsIntersect

    def mappingToPrimitive(self, prim):
        #If ttexture have not erasable points, return this points
        if(not self.get_absolute_points_not_erasable()):

            #If not, map to prim
            global primnumber
            global epsilon
            logging.debug('Start method mappingToPrimitive, class Texture')
            vertices = [list(p.point().position()) for p in prim.vertices()]
            logging.debug('Prim: ' + str(prim.number()) + ' points object space: '
                           + str(vertices))

            #Convert prim to tangent space of patterns
            tbnCalculated = CreateTBN.CreateTBN(prim)
            tbnCalculated.do()
            absolutePoints = []
            for point in self.get_delimited_proportions():
                pRotateAndScaled = tbnCalculated.get_tbn().mulPoint3ToMatrix3(point)
                pointInPrim = GeoMath.vecPlus(tbnCalculated.get_point_which_is_relative(),
                                               pRotateAndScaled)
                absolutePoints.append(pointInPrim)
                logging.debug('Point without tbn ' + str(point))
                logging.debug('Points converted ' + str(pointInPrim))
            self.set_absolute_points(absolutePoints)
        else:
            self.set_absolute_points(self.get_absolute_points_not_erasable())

        self.prim = prim

    def pointInTexture(self, point):
        inside = None
        if(self.get_absolute_points_not_erasable()):
            inside = GeoMath.pointInPoints(point, self.get_absolute_points_not_erasable())
        elif(self.get_absolute_points()):
            inside = GeoMath.pointInPoints(point, self.get_absolute_points())

        if(inside == None):
            if(self.get_is_default_texture()):
                inside = True
        return inside

    def showTexture(self, HI):
        HI.showCurve(self.absolutePoints, 'tex_' + str(self.material.get_name()), True)

    absolutePoints = property(get_absolute_points, set_absolute_points,
                               del_absolute_points, "absolutePoints's docstring")
    absolutePointsNotErasable = property(get_absolute_points_not_erasable,
                                          set_absolute_points_not_erasable,
                                           del_absolute_points_not_erasable,
                                            "absolutePointsNotErasable's docstring")
    delimitedProportions = property(get_delimited_proportions,
                                     set_delimited_proportions,
                                      del_delimited_proportions,
                                       "delimitedProportions's docstring")
    material = property(get_material, set_material, del_material,
                         "material's docstring")
    OBJ = property(get_obj, set_obj, del_obj, "OBJ's docstring")
    isDefaultTexture = property(
                                get_is_default_texture, set_is_default_texture,
                                 del_is_default_texture, "isDefaultTexture's docstring")
    prim = property(get_prim, set_prim, del_prim, "prim's docstring")
