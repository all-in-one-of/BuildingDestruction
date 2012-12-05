# -*- coding: utf-8 -*-
'''
Created on Sep 28, 2011

@author: carlos
'''
from ExternalClasses import GeoMath
import math
import logging
import DetermineVectors
import cmath
epsilon = 0.001

class CreateTBN(object):
    '''
    This class create a tbn matrix in this manner:
    First we need a point which all is relative, this point will be the leftmost and lowest
    in tangent space. But, this point, have to be the same concept in object space, so, we
    have to found the point leftmost and lowest in object space of this primitive. I imagine
    a cilinder mapping. First we filter the points, getting the lowest points (the lowest 'y'
    component). Then, we get the point nearest considering the less angle between point and
    'z+' component.
    Once this is done, the vectors (bitangent, tangnet and normal) are normalized. So,
    if the prim has 4 edges, the prim have enclosure in [0,0],[1,1], so the area is 1. BUT
    if primitive has more edges, only the three first edges(edges to tbn) are 1(normalized),
    so the prim mapped in tangent space will be greater than 1. We have to take into account 
    to draw the texture.
    '''

    #TODO: remove prim dependancy, allowing points and normal in parameters
    def __init__(self, prim):
        '''
        Constructor
        '''
        self.__prim = prim
        self.__previousPoint = None
        self.__pointWhichIsRelative = None
        self.__nextPoint = None
        self.__tbn = None
        self.__tbnInverse = None

    def get_previous_point(self):
        return self.__previousPoint


    def get_point_which_is_relative(self):
        return self.__pointWhichIsRelative


    def get_next_point(self):
        return self.__nextPoint


    def get_prim(self):
        return self.__prim


    def get_tbn(self):
        return self.__tbn


    def get_tbn_inverse(self):
        return self.__tbnInverse


    def set_previous_point(self, value):
        self.__previousPoint = value


    def set_point_which_is_relative(self, value):
        self.__pointWhichIsRelative = value


    def set_next_point(self, value):
        self.__nextPoint = value


    def set_prim(self, value):
        self.__prim = value


    def set_tbn(self, value):
        self.__tbn = value


    def set_tbn_inverse(self, value):
        self.__tbnInverse = value


    def del_previous_point(self):
        del self.__previousPoint


    def del_point_which_is_relative(self):
        del self.__pointWhichIsRelative


    def del_next_point(self):
        del self.__nextPoint


    def del_prim(self):
        del self.__prim


    def del_tbn(self):
        del self.__tbn


    def del_tbn_inverse(self):
        del self.__tbnInverse

    def do(self, scale=False):
        #Calcule points to tbn matrix
        self.calculatePoints()
        #Get some arbitrary vectors conected from vertices of prim

        vec1 = GeoMath.vecSub(self.get_previous_point(), self.get_point_which_is_relative())
        vec2 = GeoMath.vecSub(self.get_next_point(), self.get_point_which_is_relative())
        #logging.debug('Two arbitrary vec1 and vec2:' + str(vec1) + ' ' + str(vec2))

        #We have to know which angle reside between the two coencted vectors, to know if suposed vectors
        #in tangent space will be correct

        angle = GeoMath.vecDotProduct(vec1, vec2) / (GeoMath.vecModul(vec1) * GeoMath.vecModul(vec2))
        angle = math.acos(angle)
        angle = math.degrees(angle)
        #logging.debug('Angle between vecs:' + str(angle))

        #We put relative one arbitrary point to tangent space


        #logging.debug('Point relative:' + str(self.get_point_which_is_relative()))
        #Determine x and y vectors, now we'll have suposed horizontal and vertical vectors acording to
        #prim and direction of the crack
        hasTheNormalToY = GeoMath.vecDotProduct(list(self.get_prim().normal()), [0, 1, 0])
        #logging.debug('Has the normal to y?:' + str(hasTheNormalToY))
        if(hasTheNormalToY < (1 - epsilon) and hasTheNormalToY > (-1 + epsilon)):
            vecH, vecV = DetermineVectors.DetermineVectors.detVec(self.get_prim(), [0, 1, 0], [0, 0, 1])
            #logging.debug('Yes, it has the normal to y and vecs are:' + str(vecH) + ' ' + str(vecV))
        else:
            vecH, vecV = DetermineVectors.DetermineVectors.detVec(self.get_prim(), [0, 0, 1], [0, 0, 1])
            #logging.debug('No, it isnt has the normal to y and vecs are:' + str(vecH) + ' ' + str(vecV))
        #CHAPUZA CON NUMEROS COMPLEJOS!!! Precision de python pésima, 1.000000001>1?? no! y math.acos error
        cosAngle = GeoMath.vecDotProduct(vecH, vec1) / (GeoMath.vecModul(vec1) * GeoMath.vecModul(vecH))
        complexAngle = cmath.acos(cosAngle)
        if(complexAngle.imag == 0):
            angleBetweenDetVecAndVecH = math.acos(cosAngle)
        else:
            if(cosAngle < 0):
                angleBetweenDetVecAndVecH = math.acos(-1)
            else:
                angleBetweenDetVecAndVecH = math.acos(1)

        #Now we have to ensure that the vec1 has the same direction that the horizontal vector, if not, we
        #change and the horizontal vector will be vec2. Also we have to check if the prim is not a quad,
        #in this case we have to get the vertical vector from horizontal vector, rotating the known angle
        #between the two vectors conected in prim (in quad we know that the angle is 90 and we already have the
        #good vectors)
        if((math.fabs(angleBetweenDetVecAndVecH) < epsilon) or (math.fabs(angleBetweenDetVecAndVecH) > (math.pi - epsilon))):
            if(scale):
                x = GeoMath.vecScalarProduct([1, 0, 0], GeoMath.vecModul(vec1))
            x = [1, 0, 0]
            y = GeoMath.rotateVecByVec(x, [0, 0, 1], angle)
            if(scale):
                y = GeoMath.vecScalarProduct(GeoMath.vecNormalize(y), GeoMath.vecModul(vec2))
            tbn = GeoMath.createTBNmatrix(self.get_previous_point(), self.get_point_which_is_relative(), self.get_next_point(), x, [0, 0], y)
        else:
            if(scale):
                x = [1, 0, 0]
            y = GeoMath.rotateVecByVec(x, [0, 0, 1], angle)
            if(scale):
                y = GeoMath.vecScalarProduct(GeoMath.vecNormalize(y), GeoMath.vecModul(vec1))
            tbn = GeoMath.createTBNmatrix(self.get_previous_point(), self.get_point_which_is_relative(), self.get_next_point(), y, [0, 0], x)
        #logging.debug('tbn: ' + str(tbn.printAttributes()))
        tbnInverse = GeoMath.Matrix(3, 3)
        tbnInverse.copy(tbn)
        tbnInverse.matrix3Inverse()

        self.set_tbn(tbn)
        self.set_tbn_inverse(tbnInverse)

    def calculatePoints(self):
        #Filter the points, first we get the undermost points, and then,
        #The point which less angle from z+ vector by y+ vector has.
        global epsilon
        vertices = [list(p.point().position()) for p in self.prim.vertices()]
        lessy = vertices[0][1]
        mayPoints = []
        for point in vertices:
            if((point[1] - epsilon) < lessy):
                mayPoints.append(point)
            if(point[1] < (lessy - epsilon)):
                lessy = point[1]
                mayPoints = [point]

        #We construct vectors from points to determine which is leftmost, so we delete 'y' component
        minAngle = 2 * math.pi + epsilon
        for point in mayPoints:
            vec = GeoMath.vecNormalize([point[0], 0, point[2]])
            angle = GeoMath.angleBetweenPointsByVec([0, 0, 1], vec, [0, 1, 0])
            if(angle < minAngle):
                minAngle = angle
                minPoint = point

        index = vertices.index(minPoint)
        previousPoint = vertices[index - 1]
        pointWhichIsRelative = minPoint
        nextPoint = vertices[(index + 1) % len(vertices)]

        self.set_previous_point(previousPoint)
        self.set_point_which_is_relative(pointWhichIsRelative)
        self.set_next_point(nextPoint)

    previousPoint = property(get_previous_point, set_previous_point, del_previous_point, "previousPoint's docstring")
    pointWhichIsRelative = property(get_point_which_is_relative, set_point_which_is_relative, del_point_which_is_relative, "pointWhichIsRelative's docstring")
    nextPoint = property(get_next_point, set_next_point, del_next_point, "nextPoint's docstring")
    prim = property(get_prim, set_prim, del_prim, "prim's docstring")
    previousPoint = property(get_previous_point, set_previous_point, del_previous_point, "previousPoint's docstring")
    pointWhichIsRelative = property(get_point_which_is_relative, set_point_which_is_relative, del_point_which_is_relative, "pointWhichIsRelative's docstring")
    nextPoint = property(get_next_point, set_next_point, del_next_point, "nextPoint's docstring")
    prim = property(get_prim, set_prim, del_prim, "prim's docstring")
    tbn = property(get_tbn, set_tbn, del_tbn, "tbn's docstring")
    tbnInverse = property(get_tbn_inverse, set_tbn_inverse, del_tbn_inverse, "tbnInverse's docstring")

