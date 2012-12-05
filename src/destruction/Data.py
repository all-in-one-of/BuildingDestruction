# -*- coding: utf-8 -*-
from ExternalClasses import GeoMath
import DetermineVectors
import copy
import hou #@UnresolvedImport
import logging
import math
import random


class GeneralPattern:
    def __init__(self):
        self.stackPattern = {}
        self.points = []

    def get_points_object_space(self):
        return self.__points


    def set_points(self, value):
        self.__points = value


    def del_points(self):
        del self.__points


    def applyPattern(self, single_pattern, wavelength):
        logging.debug("applyPattern in General, points: " + str(self.points))
        logging.debug("applyPattern in General, points of param: " + str(single_pattern.getPoints()))
        #Lazy comprobation
        #FIXME:Check if in the first if the second condition is correct, maybe it has to be .keys()
        if(len(sorted(self.stackPattern.values())) == 0 or sorted(self.stackPattern.values()).pop() < wavelength):
            self.stackPattern[wavelength] = single_pattern
            self.points = single_pattern.applyPattern(self.points)
            logging.debug("applyPattern in General first if, points: " + str(self.points))
        elif(len(sorted(self.stackPattern.values())) > 0):
            del self.stackPattern[wavelength]
            logging.debug("applyPattern in General, pattern: " + str(single_pattern.getPoints()))
            self.stackPattern[single_pattern.waveLenght] = single_pattern
            self.points = []
            for wavelength2 in self.stackPattern:
                self.points = self.stackPattern[wavelength2].applyPattern(self.points)
                logging.debug("Iteration of wavelengths, and points are " + str(self.points))
        else:
            logging.debug("applyPattern in General ERROR: ")
    #NOT IMPLEMENTED
    def calculatePattern(self):
        for patt in self.stackPattern:
            patt.applyPattern(self.points)

    def getLastPoint(self):
        return self.points[len(self.points) - 1]

    def getPoints(self):
        return self.points

    def getFirstPoint(self):
        return self.points[0]

    def getStack(self):
        return self.stackPattern

    def add_noise(self, height, frequency, for_edge, wavelength):
        #FIXME: only applied in this points, not in the single patterns...so the data
        #in the stack pattern will be corrupt
        if (wavelength in self.stackPattern):
            pattern = self.stackPattern[wavelength]
            pointI = self.getFirstPoint()
            pointF = self.getLastPoint()
            ad = Add_noise()
            logging.debug("Points in add noise General pattern: " + str(pointI) + " " + str(pointF))
            self.points = ad.apply_noise(self.points, pattern.getNormal(), height, for_edge, frequency)
            if(not (self.getFirstPoint() == pointI and self.getLastPoint() == pointF)):
                logging.debug("Pattern first, last: " + str(self.getFirstPoint()) + " " + str(self.getLastPoint()))
                logging.debug("Pattern Must be firts, last: " + str(pointI) + " " + str(pointF))
                exit()

    def clipPattern(self, point):
        #FIXME:Sort this points of general pattern, but not clip the points of the patterns in
        #the stack
        self.points, achieved = GeoMath.clipPoints(self.points, point, self.points[0])
        return achieved
    points = property(get_points_object_space, set_points, del_points, "points's docstring")

class Pattern:
    def __init__(self, normal=[0, 0, 0], points=[], size=[0, 0], wavelenght=0):
        self.normal = normal
        self.size = size
        self.wavelength = wavelenght
        self.points = points

    def rotatePattern(self, axis, angle):
        middlePoint = GeoMath.getCenterEdge([self.points[0], self.points[len(self.points) - 1]])
        middlePoint.append(1)
        trans = GeoMath.Matrix(4, 4)
        trans.matrix4Trans(middlePoint)
        transIn = GeoMath.Matrix(4, 4)
        transIn.copy(trans)
        transIn.matrix4Inverse()
        for num in range(len(self.points)):
            pointRot = list(self.points[num])
            pointRot.append(1)
            pointRot = transIn.mulPoint4ToMatrix4(pointRot)
            if(axis == [1, 0, 0]):
                Rx = GeoMath.Matrix(4, 4)
                Rx.singleRotx(angle)
                pointRot = Rx.mulPoint4ToMatrix4(pointRot)
            elif(axis == [0, 1, 0]):
                Ry = GeoMath.Matrix(4, 4)
                Ry.singleRoty(angle)
                pointRot = Ry.mulPoint4ToMatrix4(pointRot)
            else:
                Rz = GeoMath.Matrix(4, 4)
                Rz.singleRotz(angle)
                pointRot = Rz.mulPoint4ToMatrix4(pointRot)

            pointRot = trans.mulPoint4ToMatrix4(pointRot)
            self.points[num] = pointRot
        #Rotate normal
        logging.debug('Normal not rotated:' + str(self.normal))
        to_rotate_normal = self.normal
        to_rotate_normal.append(0)
        if(axis == [1, 0, 0]):
            Rx = GeoMath.Matrix(4, 4)
            Rx.singleRotx(angle)
            normalRot = Rx.mulPoint4ToMatrix4(to_rotate_normal)
        elif(axis == [0, 1, 0]):
            Ry = GeoMath.Matrix(4, 4)
            Ry.singleRoty(angle)
            normalRot = Ry.mulPoint4ToMatrix4(to_rotate_normal)
        else:
            Rz = GeoMath.Matrix(4, 4)
            Rz.singleRotz(angle)
            normalRot = Rz.mulPoint4ToMatrix4(to_rotate_normal)
        normalRot.pop()
        logging.debug('Normal rotated: ' + str(normalRot))
        self.normal = normalRot
        #self.normal = GeoMath.rotateVecByVec(self.normal, axis, angle)

    def cutPattern(self, point):
        pass

    def getPoints(self):
        return self.points

    def getDir(self):
        return GeoMath.vecSub(self.points[len(self.points) - 1], self.points[0])

    def getNormal(self):
        return self.normal
    def getLastPoint(self):
        return self.points[len(self.points) - 1]
    def getFirstPoint(self):
        return self.points[0]
    def setNormal(self, value):
        self.normal = value
    def add_noise(self, height, frequency, for_edge):
        if(GeoMath.vecModul(self.getNormal()) > 0):
            #If normal of pattern is valid
            ad = Add_noise()
            self.points = ad.apply_noise(self.points, self.normal, height, for_edge, frequency)

class Add_noise():
    instance = None
    geo = None
    node_geo = None
    curve_node = None
    edge_divide_node = None
    point_node = None
    mountain_node = None
    def __new__(cls, *args, **kargs):
        if cls.instance is None:
            cls.instance = object.__new__(cls, *args, **kargs)
        return cls.instance
    @classmethod
    def __init__(cls, geo=None):
        #If it is the first intanciate
        if(not cls.geo):
            if(not geo):
                geo = hou.node('/obj')
                node_geo = geo.createNode('geo')
                node_geo.children()[0].destroy()
            else:
                node_geo = geo.createNode('geo')
                node_geo.children()[0].destroy()
            cls.geo = geo
            cls.node_geo = node_geo
            cls.curve_node = None
            cls.edge_divide_node = None
            cls.point_node = None
            cls.mountain_node = None

    @classmethod
    def calculate_frequency(cls, frequency_string):
        frequency_number = -1
        if(frequency_string == "little"):
            frequency_number = 0.5
        if(frequency_string == "medium"):
            frequency_number = 10
        if(frequency_string == "large"):
            frequency_number = 30
        assert frequency_number > 0
        return frequency_number

    @classmethod
    def apply_noise(cls, points, normal, height, for_edge, frequency="little",):
        logging.debug("Class Add_noise, method apply_noise")
        if(not cls.curve_node):
            logging.debug("Class GlassDynamicPatternGenerator, creating new nodes")
            #Create nodes to generate a pattern
            curve_node = cls.node_geo.createNode('curve')
            edge_divide_node = cls.node_geo.createNode('edgedivide')
            point_node = cls.node_geo.createNode('point')
            mountain_node = cls.node_geo.createNode('mountain')

            #connect it
            edge_divide_node.setNextInput(curve_node)
            point_node.setNextInput(edge_divide_node)
            mountain_node.setNextInput(point_node)

            #The first group, if we don't put the value, it doesnt work
            edge_divide_node.parm('group').set('0')


        else:
            curve_node = cls.curve_node
            edge_divide_node = cls.edge_divide_node
            point_node = cls.point_node
            mountain_node = cls.mountain_node
        final_points = []

        if (for_edge):
            #If we want a noise for each edge, we can get all edges from points
            edges = GeoMath.getEdgesFromPoints(points)
            #Delete last edge, because we are working with no closed pattern
            edges.pop()
        else:
            #If not, we apply noise to all points at the same time
            edges = [points]
        logging.debug("Class add noise")
        logging.debug("points" + str(points))
        logging.debug("normal" + str(normal))
        logging.debug("height" + str(height))
        logging.debug("for_edge" + str(for_edge))
        for points_for_iteration in edges:
            '''
            pointI = points_for_iteration[0]
            pointF = points_for_iteration[len(points_for_iteration) - 1]
            points_for_iteration = [pointI, pointF]
            '''
            pointsString = ""
            for point in points_for_iteration:
                pointsString = pointsString + str(point[0]) + "," + str(point[1]) + "," + str(point[2]) + " "
            curve_node.parm('coords').set(pointsString)

            #Set edge divisions, we set for a constant of 50, but it may to be any number
            #Only if we apply noise for each edge
            if(for_edge):
                multiplier_number_of_points = 1
                edge_divide_node.parm('numdivs').set(int(cls.calculate_frequency(frequency) * multiplier_number_of_points))
            else:
                point_node.setInput(0, curve_node)

            #Put the parameters
            point_node.parm('donml').set('on')
            point_node.parm('nx').deleteAllKeyframes()
            point_node.parm('ny').deleteAllKeyframes()
            point_node.parm('nz').deleteAllKeyframes()
            point_node.parm('nx').set(normal[0])
            point_node.parm('ny').set(normal[1])
            point_node.parm('nz').set(normal[2])

            #Set parameters to mountain node
            #self.sizex*50=number of points_for_iteration in the curve

            mountain_node.parm('height').set(height)
            frequency_number = cls.calculate_frequency(frequency)
            mountain_node.parm('freq1').set(frequency_number)
            mountain_node.parm('freq2').set(frequency_number)
            mountain_node.parm('freq3').set(frequency_number)
            #Put random offset to get random points_for_iteration
            mountain_node.parm('offset1').set(random.random() * 100)
            mountain_node.parm('offset2').set(random.random() * 100)
            mountain_node.parm('offset3').set(random.random() * 100)
            #We get the generate pattern
            pointI = points_for_iteration[0]
            pointF = points_for_iteration[len(points_for_iteration) - 1]
            mountain_node.cook()
            generated_pattern = [list(p.position()) for p in mountain_node.geometry().points()]
            #===================================================================
            # Important: If we do a division of edges, the points are numered in
            # this manner:
            # We get a edge numered as first point with number 0 and last point
            # with number 1. when we do a division, each division are numered from
            # point 0 to ndivision, but the point number 1 is still the number one
            # so for example, in a edge [0,1] with 5 divions the number are
            # [0,2,3,4,1].
            #===================================================================
            if(for_edge):
                #===============================================================
                # fix the above issue
                #===============================================================
                last_point = generated_pattern[1]
                del generated_pattern[1]
                generated_pattern.append(last_point)
            #Return initial point and final point to his original positions
            generated_pattern[0] = pointI
            generated_pattern[len(generated_pattern) - 1] = pointF

            final_points.extend(generated_pattern)
            logging.debug("Add noise points_for_iteration finish: " + str(points_for_iteration))

        if(not cls.curve_node):
            cls.curve_node = curve_node
            cls.edge_divide_node = edge_divide_node
            cls.point_node = point_node
            cls.mountain_node = mountain_node

        if(not for_edge):
            #Back to connect the nodes as before
            point_node.setInput(0, edge_divide_node)
        return final_points

class WallPattern(Pattern):
    def applyPattern(self, points):
        if (self.wavelength == 0):
            return copy.deepcopy(self.points)
        else:
            pass

    def copy(self):
        return WallPattern(list(self.normal), [list(p) for p in self.points], list(self.size), self.wavelength)

class GlassPatternDynamic(Pattern):
    def applyPattern(self, points):
        if (self.wavelength == 0):
            return copy.deepcopy(self.points)
        else:
            pass
    def copy(self):
        return GlassPatternDynamic(list(self.normal), [list(p) for p in self.points], list(self.size), self.wavelength)

class GlassPattern(Pattern):
    def applyPattern(self, points):
        if (self.wavelength == 0):
            return copy.deepcopy(self.points)
        else:
            pass
    def copy(self):
        return GlassPattern(list(self.normal), [list(p) for p in self.points], list(self.size), self.wavelength)

class DynamicPatternGenerator(object):
    instance = None
    def __new__(cls, * args, ** kargs):
        if cls.instance is None:
            cls.instance = object.__new__(cls, * args, ** kargs)
        return cls.instance

    def __init__(self):
        pass

    def is_dynamic(self):
        return True

    def getRandomPattern(self, wavelength, pointI, pointF, prim, height=None):
        pass

    def showPatterns(self, node, wavelength, numberOfPatterns):
        pass

    def getGeo(self):
        return self.geo

    def getSizex(self):
        return self.sizex

    def getSizey(self):
        return self.sizey

    def getRotz(self):
        return self.rotZ

    def getSimDir(self, pattern):
        horizontal = abs(GeoMath.vecDotProduct(pattern.getNormal(), [1, 0, 0]))
        vertical = abs(GeoMath.vecDotProduct(pattern.getNormal(), [0, 1, 0]))
        oblique = abs(GeoMath.vecDotProduct(pattern.getNormal(), [1, 0, 0]))
        if (horizontal > vertical and horizontal > oblique):
            #return vertical simetry
            return self.simDir[1]
        if(vertical > horizontal and vertical > oblique):
            #return horizontal simetry
            return self.simDir[0]
        if(oblique > horizontal and oblique > vertical):
            #return oblique simetry
            return self.simDir[2]

    def getSimNormal(self, pattern):
        horizontal = abs(GeoMath.vecDotProduct(pattern.getNormal(), [1, 0, 0]))
        vertical = abs(GeoMath.vecDotProduct(pattern.getNormal(), [0, 1, 0]))
        oblique = abs(GeoMath.vecDotProduct(pattern.getNormal(), [1, 0, 0]))
        if (horizontal > vertical and horizontal > oblique):
            #return vertical simetry
            return self.simN[1]
        if(vertical > horizontal and vertical > oblique):
            #return horizontal simetry
            return self.simN[0]
        if(oblique > horizontal and oblique > vertical):
            #return oblique simetry
            return self.simN[2]

    def getSimY(self, pattern):
        horizontal = abs(GeoMath.vecDotProduct(pattern.getNormal(), [1, 0, 0]))
        vertical = abs(GeoMath.vecDotProduct(pattern.getNormal(), [0, 1, 0]))
        oblique = abs(GeoMath.vecDotProduct(pattern.getNormal(), [1, 0, 0]))
        if (horizontal > vertical and horizontal > oblique):
            #return vertical simetry,  but how this is the y and direction... it will be false
            return self.simy[1]
        if(vertical > horizontal and vertical > oblique):
            #return horizontal, but how this is the y and normal... it will be false
            return self.simy[0]
        if(oblique > horizontal and oblique > vertical):
            #return oblique simetry
            return self.simy[2]

    def getSimX(self, pattern):
        horizontal = abs(GeoMath.vecDotProduct(pattern.getNormal(), [1, 0, 0]))
        vertical = abs(GeoMath.vecDotProduct(pattern.getNormal(), [0, 1, 0]))
        oblique = abs(GeoMath.vecDotProduct(pattern.getNormal(), [1, 0, 0]))
        if (horizontal > vertical and horizontal > oblique):
            #return vertical simetry, but how this is the x and normal... it will be false
            return self.simx[1]
        if(vertical > horizontal and vertical > oblique):
            #return horizontal
            return self.simx[0]
        if(oblique > horizontal and oblique > vertical):
            #return oblique simetry
            return self.simx[2]

    def setGeo(self, geo):
        self.geo = geo

class GlassDynamicPatternGenerator(DynamicPatternGenerator):
    def __init__(self, geo=None):
        #Properties of glass
        self.rotZ = 90
        self.simDir = [True, True, True]
        self.simN = [True, True, True]
        self.simy = [True, True, True]
        self.simx = [True, True, True]
        self.sizex = 0.5
        self.sizey = 0.5


    def is_dynamic(self):
        return True

    def getRandomPattern(self, wavelength, pointI, pointF, normal, height=None):
        logging.debug("Class Data, method getRandomPattern")

        add_noise = Add_noise()

        #Calculate height if not get
        if(not height):
            height = self.sizey / 2
        transformed_points = add_noise.apply_noise([pointI, pointF], normal, height, True, frequency='medium')
        #Now we add the heigth for each point, because the noise lies between [-sizey/2, sizey/2]
        #and we want [0, sizey]
        #So we get the direction of the noise and multiply by the heigth/2 and plus to the points
        positive_points = []
        #Calculate the sum to each point
        normal_with_module = GeoMath.vecScalarProduct(normal, height / 2)
        for point in transformed_points:
            positive_points.append(GeoMath.vecPlus(point, normal_with_module))
        logging.debug("Generated pattern finish: " + str(positive_points))

        dirWithModule = GeoMath.vecSub(pointF, pointI)
        #normal points size wavelenght
        pattern = GlassPatternDynamic(normal, positive_points, [dirWithModule[0], dirWithModule[1]], wavelength)

        return pattern

    def showPatterns(self, node, wavelength, numberOfPatterns):
        #TODO: show a set of random patterns
        pass

    def applyJoker(self, point1, point2, vecH, vecV):
        vec = GeoMath.vecSub(point2, point1)
        dotH = GeoMath.vecDotProduct(vec, vecH) / GeoMath.vecModul(vecH)
        dotV = GeoMath.vecDotProduct(vec, vecV) / GeoMath.vecModul(vecV)
        if(math.fabs(dotH) < math.fabs(dotV)):
            normal = vecH
        else:
            normal = vecV
        norV = GeoMath.vecNormalize(vecV)
        norH = GeoMath.vecNormalize(vecH)
        sizeX = GeoMath.vecModul(GeoMath.vecScalarProduct(norH, dotH))
        sizeY = GeoMath.vecModul(GeoMath.vecScalarProduct(norV, dotV))
        pointI1 = GeoMath.vecPlus(point1, GeoMath.vecScalarProduct(norH, dotH / 2))
        pointI2 = GeoMath.vecPlus(pointI1, GeoMath.vecScalarProduct(norV, dotV))
        return WallPattern(normal, [list(point1), pointI1, pointI2, list(point2)], [sizeX, sizeY], 0)

class SetPattern:
    instance = None
    def __new__(cls, *args, **kargs):
        if cls.instance is None:
            cls.instance = object.__new__(cls, *args, **kargs)
        return cls.instance

    def __init__(self):
        pass
    def is_dynamic(self):
        return False

    def getRandomPattern(self, wavelength):
        if(wavelength < len(self.patterns)):
            size = len(self.patterns) - 1
            numOfPatt = len(self.patterns[wavelength]) - 1
            index = random.randint(0, numOfPatt)
            return list(self.patterns[size][index])
        else:
            #Error
            return None

    def showPatterns(self, node, wavelength):
        for patt in self.patterns[wavelength]:
        #Show crack
            crackNode = node.createNode('curve', 'crack')
            pointsString = ""
            for point in patt.points:
                pointsString = pointsString + str(point[0]) + "," + str(point[1]) + "," + str(0.0) + " "
            crackNode.parm('coords').set(pointsString)
            crackNode.moveToGoodPosition()

    def applyJoker(self, point1, point2, vecH, vecV):
        """"""
        pass

    def getPatternsWavelength(self, wavelength):
        if(wavelength < len(self.patterns)):
            return self.patterns[wavelength]

    def getSizex(self):
        return self.sizex
    def getSizey(self):
        return self.sizey
    def getRotz(self):
        return self.rotZ
    def getSimDir(self, pattern):
        if (pattern.normal == [1, 0, 0] or pattern.normal == [-1, 0, 0]):
            #return vertical simetry
            return self.simDir[1]
        elif(pattern.normal == [0, 1, 0] or pattern.normal == [0, -1, 0]):
            #return horizontal simetry
            return self.simDir[0]
        else:
            #return oblique simetry
            return self.simDir[2]

    def getSimNormal(self, pattern):
        if (pattern.normal == [1, 0, 0] or pattern.normal == [-1, 0, 0]):
            #return vertical simetry
            return self.simN[1]
        elif(pattern.normal == [0, 1, 0] or pattern.normal == [0, -1, 0]):
            #return horizontal simetry
            return self.simN[0]
        else:
            #return oblique simetry
            return self.simN[2]

    def getSimY(self, pattern):
        if (pattern.normal == [1, 0, 0] or pattern.normal == [-1, 0, 0]):
            #return vertical simetry,  but how this is the y and direction... it will be false
            return self.simy[1]
        elif(pattern.normal == [0, 1, 0] or pattern.normal == [0, -1, 0]):
            #return horizontal, but how this is the y and normal... it will be false
            return self.simy[0]
        else:
            #return oblique simetry
            return self.simy[2]
    def getSimX(self, pattern):
        if (pattern.normal == [1, 0, 0] or pattern.normal == [-1, 0, 0]):
            #return vertical simetry, but how this is the x and normal... it will be false
            return self.simx[1]
        elif(pattern.normal == [0, 1, 0] or pattern.normal == [0, -1, 0]):
            #return horizontal
            return self.simx[0]
        else:
            #return oblique simetry
            return self.simx[2]

#Set of wall patterns
class SetPatternWall(SetPattern):
    instance = None
    def __new__(cls, * args, ** kargs):
        if cls.instance is None:
            cls.instance = object.__new__(cls, * args, ** kargs)
        return cls.instance


    def __init__(self):
        self.rotZ = 180
        self.simDir = [True, True, False]
        self.simN = [True, True, False]
        self.simy = [True, True, True]
        self.simx = [True, True, True]
        self.sizex = 0.6
        self.sizey = 0.36
        #Set of patterns
        self.patterns = []
        self.joker = WallPattern([])
        #Size 1=0.30x0.09, castellian bricks
        #Horizontal
        self.patterns.append([])

        self.patterns[0].append(WallPattern([0, 1, 0], [[0, 0, 0], [0.6, 0, 0]], [0.6, 0.0, 0], 0))

        self.patterns[0].append(WallPattern([0, 1, 0], [[0, 0, 0], [0.15, 0.0, 0.0], [0.15, 0.09, 0.0], [0.45, 0.09, 0], \
                                [0.45, 0, 0], [0.6, 0, 0]], [0.6, 0.09, 0], 0))
        #Vertical

        self.patterns[0].append(WallPattern([1, 0, 0], [[0.0, 0.36, 0], [0.0, 0.0, 0]], [0, 0.36, 0], 0))

        self.patterns[0].append(WallPattern([1, 0, 0], [[0.0, 0.36, 0], [0.0, 0.27, 0], [0.15, 0.27, 0], [0.15, 0.18, 0], \
                                [0.0, 0.18, 0], [0, 0, 0]], [0.15, 0.36, 0], 0))
        self.patterns[0].append(WallPattern([1, 0, 0], [[0.0, 0.36, 0], [0.15, 0.36, 0], [0.15, 0.27, 0], [0.0, 0.27, 0], \
                                [0.0, 0.0, 0]], [0.15, 0.36, 0], 0))
        self.patterns[0].append(WallPattern([1, 0, 0], [[0.0, 0.36, 0], [0.0, 0.27, 0], [0.23, 0.27, 0], [0.23, 0.18, 0], \
                                [0.0, 0.18, 0], [0.0, 0.09, 0], [0.13, 0.09, 0], [0.13, 0.0, 0], [0.0, 0.0, 0]], [0.23, 0.36, 0], 0))

        #Oblique
        self.patterns[0].append(WallPattern([1, 0, 0], [[0.0, 0.0, 0.0], [0.30, 0.0, 0], [0.30, 0.09, 0], [0.0, 0.09, 0], \
                                [0.0, 0.18, 0], [0.15, 0.18, 0], [0.15, 0.27, 0], [0.0, 0.27, 0], [0.0, 0.36, 0], [0.6, 0.36, 0]], [0.60, 0.36, 0], 0))
        self.patterns[0].append(WallPattern([1, 0, 0], [[0.0, 0.36, 0], [0.0, 0.27, 0], [0.23, 0.27, 0], [0.23, 0.18, 0], \
                                [0.15, 0.18, 0], [0.15, 0.09, 0], [0.60, 0.09, 0], [0.6, 0.0, 0]], [0.6, 0.36, 0], 0))

    def applyJoker(self, point1, point2, vecH, vecV):
        vec = GeoMath.vecSub(point2, point1)
        dotH = GeoMath.vecDotProduct(vec, vecH) / GeoMath.vecModul(vecH)
        dotV = GeoMath.vecDotProduct(vec, vecV) / GeoMath.vecModul(vecV)
        if(math.fabs(dotH) < math.fabs(dotV)):
            normal = vecH
        else:
            normal = vecV
        norV = GeoMath.vecNormalize(vecV)
        norH = GeoMath.vecNormalize(vecH)
        sizeX = GeoMath.vecModul(GeoMath.vecScalarProduct(norH, dotH))
        sizeY = GeoMath.vecModul(GeoMath.vecScalarProduct(norV, dotV))
        pointI1 = GeoMath.vecPlus(point1, GeoMath.vecScalarProduct(norH, dotH / 2))
        pointI2 = GeoMath.vecPlus(pointI1, GeoMath.vecScalarProduct(norV, dotV))
        return WallPattern(normal, [list(point1), pointI1, pointI2, list(point2)], [sizeX, sizeY], 0)

class SetPatternGlass(SetPattern):
    instance = None
    def __new__(cls, * args, ** kargs):
        if cls.instance is None:
            cls.instance = object.__new__(cls, * args, ** kargs)
        return cls.instance


    def __init__(self):
        self.rotZ = 90
        self.simDir = [True, True, True]
        self.simN = [True, True, True]
        self.simy = [True, True, True]
        self.simx = [True, True, True]
        self.sizex = 0.5
        self.sizey = 0.5
        #Set of patterns
        self.patterns = []
        self.joker = GlassPattern([])
        #Horizontal
        self.patterns.append([])
        '''
        self.patterns[0].append(GlassPattern([0, 1, 0], [[0, 0, 0], [0.065, 0.333, 0], \
                                [0.189, 0.287, 0], [0.242, 0.129, 0], [0.362, 0.150, 0], [0.425, 0.277, 0], [0.471, 0.061, 0], \
                                [0.521, 0.178, 0], [0.55, 0.07, 0], [0.6, 0, 0]], [0.6, 0.33, 0], 0))
        self.patterns[0].append(GlassPattern([0, 1, 0], [[0, 0, 0], [0.13, 0.04, 0], [0.20, 0.01, 0], \
                                [0.23, 0.02, 0], [0.24, 0, 0], [0.28, 0.04, 0], [0.33, 0.01, 0], [0.38, 0.04, 0], [0.60, 0, 0]], \
                                [0.6, 0.04, 0], 0))'''
        '''
        self.patterns[0].append(GlassPattern([0,1,0],[[0.00207236,0.00356816,0], [0.0342624,0.0464883,0],\
        [0.0664525,0.0303933,0], [0.0789709,0.00535654,0], [0.121891,0.0250282,0], [0.148716,0.0107215,0],\
        [0.191636,0.0393349,0], [0.191636,0.00714488,0], [0.245286,0.0339699,0], [0.304301,-0.00179683,0]],[0.304301,0.0393349],0))'''
        self.patterns[0].append(GlassPattern([0, 1, 0], [[0, 0, 0], [0.0609126, 0.109372, 0], [0.198263, 0.0872182, 0], [0.263246, 0.134479, 0], [0.304599, 0.0931258, 0], [0.286876, 0.0370041, 0], [0.406504, 0.011897, 0], [0.484779, 0.0739263, 0], [0.5, 0, 0]], [0.5, 0.134479], 0))
        #Vertical
        '''
        self.patterns[0].append(GlassPattern([1, 0, 0], [[0, 0.36, 0], [0.03, 0.23, 0], [0.09, 0.15, 0], \
                                [0.05, 0.10, 0], [0.08, 0.05, 0], [0, 0, 0]], [0.09, 0.36, 0], 0))
        self.patterns[0].append(GlassPattern([1, 0, 0], [[0, 0.36, 0], [0.1, 0.3, 0], [0.04, 0.27, 0], \
                                [0.20, 0.31, 0], [0.18, 0.27, 0], [0.06, 0.18, 0], [0.13, 0.14, 0], [0.05, 0.09, 0], [0.15, 0.08, 0], \
                                [0.13, 0.03, 0], [0.08, 0.01, 0], [0, 0, 0]], [0.2, 0.36, 0], 0))
        '''
        self.patterns[0].append(GlassPattern([1, 0, 0], [[0, 0.5, 0], [0.0638664, 0.435763, 0], [0.258815, 0.438717, 0], [0.309029, 0.361919, 0], [0.376966, 0.292505, 0], [0.193832, 0.367827, 0], [0.0756814, 0.342719, 0], [0.372535, 0.205369, 0], [0.255862, 0.147771, 0], [0.331183, 0.101987, 0], [0, 0, 0]], [0.376966, 0.5], 0))
        #Oblique
        '''
        self.patterns[0].append(GlassPattern([0, math.cos(math.pi / 4), math.sin(math.pi / 4)], [[0, 0.36, 0], \
                                [0.052, 0.150, 0], [0.13, 0.24, 0], [0.23, 0.20, 0], [0.31, 0.30, 0], [0.40, 0.042, 0], [0.50, 0.18, 0], \
                                [0.55, 0.14, 0], [0.53, 0.058, 0], [0.60, 0, 0]], [0.6, 0.36, 0], 0))
        self.patterns[0].append(GlassPattern([0, math.cos(math.pi / 4), math.sin(math.pi / 4)], [[0, 0.36, 0], \
                                [0.13, 0.27, 0], [0.23, 0.37, 0], [0.23, 0.15, 0], [0.41, 0.33, 0], [0.48, 0.27, 0], [0.47, 0.17, 0], \
                                [0.60, 0.13, 0], [0.55, 0.072, 0], [0.60, 0, 0]], [0.6, 0.36, 0], 0))

        '''
        self.patterns[0].append(GlassPattern([math.cos(math.pi / 4), math.sin(math.pi / 4), 0], [[0, 0.50, 0], [0.19974, 0.438717, 0], \
                                [0.136234, 0.332381, 0], [0.326752, 0.211277, 0], [0.424227, 0.453486, 0], [0.428657, 0.282167, 0], \
                                [0.405027, 0.127094, 0], [0.168725, 0.134479, 0], [0.18054, 0.0754031, 0], [0.340044, 0.0370041, 0], [0.50, 0, 0]], [0.5, 0.5], 0))

    def applyJoker(self, point1, point2, vecH, vecV):
        vec = GeoMath.vecSub(point2, point1)
        dotH = GeoMath.vecDotProduct(vec, vecH) / GeoMath.vecModul(vecH)
        dotV = GeoMath.vecDotProduct(vec, vecV) / GeoMath.vecModul(vecV)
        if(math.fabs(dotH) < math.fabs(dotV)):
            normal = vecH
        else:
            normal = vecV
        norV = GeoMath.vecNormalize(vecV)
        norH = GeoMath.vecNormalize(vecH)
        sizeX = GeoMath.vecModul(GeoMath.vecScalarProduct(norH, dotH))
        sizeY = GeoMath.vecModul(GeoMath.vecScalarProduct(norV, dotV))
        pointI1 = GeoMath.vecPlus(point1, GeoMath.vecScalarProduct(norH, dotH / 2))
        pointI2 = GeoMath.vecPlus(pointI1, GeoMath.vecScalarProduct(norV, dotV))
        return WallPattern(normal, [list(point1), pointI1, pointI2, list(point2)], [sizeX, sizeY], 0)

class SetPatternWallBroken(SetPattern):
    instance = None
    def __new__(cls, * args, ** kargs):
        if cls.instance is None:
            cls.instance = object.__new__(cls, * args, ** kargs)
        return cls.instance


    def __init__(self):
        self.rotZ = 180
        self.simDir = [True, True, False]
        self.simN = [True, True, False]
        self.simy = [True, True, True]
        self.simx = [True, True, True]
        self.sizex = 0.6
        self.sizey = 0.36
        #Set of patterns
        self.patterns = []
        self.joker = WallPattern([])
        #Size 1=0.30x0.09, castellian bricks
        #Horizontal
        self.patterns.append([])

        self.patterns[0].append(WallPattern([0, 1, 0], [[0, 0, 0], [0.15, 0.0, 0.0], [0.15, 0.045, 0.0], [0.25, 0.09, 0.0], [0.45, 0.09, 0], \
                                [0.45, 0, 0], [0.6, 0, 0]], [0.6, 0.09, 0], 0))
        #Vertical

        self.patterns[0].append(WallPattern([1, 0, 0], [[0.0, 0.36, 0], [0.0, 0.27, 0], [0.075, 0.27, 0], [0.12, 0.21, 0.0], [0.12, 0.18, 0], \
                                [0.0, 0.18, 0], [0, 0, 0]], [0.12, 0.36, 0], 0))
        self.patterns[0].append(WallPattern([1, 0, 0], [[0.0, 0.36, 0], [0.075, 0.36, 0], [0.12, 0.27, 0], [0.0, 0.27, 0], \
                                [0.0, 0.0, 0]], [0.15, 0.36, 0], 0))
        self.patterns[0].append(WallPattern([1, 0, 0], [[0.0, 0.36, 0], [0.0, 0.27, 0], [0.18, 0.27, 0], [0.18, 0.23 , 0.0], [0.23, 0.18, 0], \
                                [0.0, 0.18, 0], [0.0, 0.09, 0], [0.05, 0.09, 0], [0.08, 0.0, 0], [0.0, 0.0, 0]], [0.23, 0.36, 0], 0))

        #Oblique
        self.patterns[0].append(WallPattern([math.cos(math.pi / 4), math.sin(math.pi / 4), 0], [[0.0, 0.0, 0.0], [0.20, 0.0, 0], [0.15, 0.045, 0.0], [0.15, 0.09, 0], [0.0, 0.09, 0], \
                                [0.0, 0.18, 0], [0.10, 0.18, 0], [0.08, 0.22, 0.0], [0.10, 0.27, 0], [0.0, 0.27, 0], [0.0, 0.36, 0], [0.6, 0.36, 0]], [0.60, 0.36, 0], 0))
        self.patterns[0].append(WallPattern([math.cos(math.pi / 4), math.sin(math.pi / 4), 0], [[0.0, 0.36, 0], [0.0, 0.27, 0], [0.10, 0.27, 0], \
                                [0.15, 0.12, 0], [0.15, 0.09, 0], [0.17, 0.07, 0], [0.6, 0.0, 0]], [0.6, 0.36, 0], 0))

    def applyJoker(self, point1, point2, vecH, vecV):
        vec = GeoMath.vecSub(point2, point1)
        dotH = GeoMath.vecDotProduct(vec, vecH) / GeoMath.vecModul(vecH)
        dotV = GeoMath.vecDotProduct(vec, vecV) / GeoMath.vecModul(vecV)
        if(math.fabs(dotH) < math.fabs(dotV)):
            normal = GeoMath.vecNormalize(vecH)
        else:
            normal = GeoMath.vecNormalize(vecV)
        norV = GeoMath.vecNormalize(vecV)
        norH = GeoMath.vecNormalize(vecH)
        sizeX = GeoMath.vecModul(GeoMath.vecScalarProduct(norH, dotH))
        sizeY = GeoMath.vecModul(GeoMath.vecScalarProduct(norV, dotV))
        pointI1 = GeoMath.vecPlus(point1, GeoMath.vecScalarProduct(norH, dotH / 2))
        pointI2 = GeoMath.vecPlus(pointI1, GeoMath.vecScalarProduct(norV, dotV))
        return WallPattern(normal, [list(point1), pointI1, pointI2, list(point2)], [sizeX, sizeY], 0)


class ComplexMaterial:
    '''
    This class has got a dictionary of SingleMaterial with his wavelength
    '''
    def __init__(self, setMaterialsAndWavelength, name):
        self.__mat = setMaterialsAndWavelength
        self.__name = name

    def get_mat(self):
        return self.__mat


    def get_name(self):
        return self.__name


    def set_mat(self, value):
        self.__mat = value


    def set_name(self, value):
        self.__name = value


    def del_mat(self):
        del self.__mat


    def del_name(self):
        del self.__name

    mat = property(get_mat, set_mat, del_mat, "mat's docstring")
    name = property(get_name, set_name, del_name, "name's docstring")

class SingleMaterial:
    '''
    This class has got a dictionary of type of patterns and his percentage of posibility to appear
    '''
    def __init__(self, setClassesAndPercentage, name):
        self.__classesAndPercentage = setClassesAndPercentage
        self.__name = name

    def get_classes_and_percentage(self):
        return self.__classesAndPercentage


    def get_name(self):
        return self.__name


    def set_classes_and_percentage(self, value):
        self.__classesAndPercentage = value


    def set_name(self, value):
        self.__name = value


    def del_classes_and_percentage(self):
        del self.__classesAndPercentage


    def del_name(self):
        del self.__name

    classesAndPercentage = property(get_classes_and_percentage, set_classes_and_percentage, del_classes_and_percentage, "classesAndPercentage's docstring")
    name = property(get_name, set_name, del_name, "name's docstring")
