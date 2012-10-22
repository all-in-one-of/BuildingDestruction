# -*- coding: utf-8 -*-
'''
Created on Oct 27, 2011

@author: carlos
'''

from ExternalClasses import GeoMath
from ExternalClasses.HouInterface import HouInterface

class Floor(object):
    '''
    classdocs
    '''


    def __init__(self, floor_params, position, structure_points):
        '''
        Constructor
        '''
        self.floor_params = floor_params
        self.position = position
        self.relative_points = structure_points
        self.absolute_points = []
        self.calculate_absolute_points()
        self.intersections = []

    def calculate_absolute_points(self):
        translation = GeoMath.vecSub(self.get_position(), [0, 0, 0])
        new_structure = []
        for point in self.get_relative_points():
            new_structure.append(GeoMath.vecPlus(point, translation))
        self.set_absolute_points(new_structure)

    #MAYFIX: We assume that the crack have to pass at least one time to one floor
    #but it is not correct, because the patterns can go between two floors
    #without passing floors
    def intersections_with_crack(self, crack, path_ordered):
        intersections = []
        edges_floor = GeoMath.getEdgesFromPoints(self.get_absolute_points())
        prev_intersection = None
        next_intersection = None
        #=======================================================================
        # we group the intersections in doublets, because after we have a different
        # destruction in the floor for each doublet of intersection
        #=======================================================================
        for prim in path_ordered:
            patterns = crack[prim]
            for pattern in patterns:
                pattern_edges = GeoMath.getEdgesFromPoints(pattern.getPoints())
                may_intersect = GeoMath.bolzanoIntersectionEdges2_5D(pattern_edges, edges_floor)
                if(may_intersect):
                    intersection = GeoMath.getIntersectionsBetweenEdges2D(
                                                    pattern_edges, edges_floor, 1)
                    if(intersection):
                        if(not prev_intersection):
                            prev_intersection = intersection
                            break
                        elif(not GeoMath.pointEqualPoint(intersection, prev_intersection)):
                            next_intersection = intersection
                            new_intersection = [prev_intersection, next_intersection]
                            intersections.append(new_intersection)
                            prev_intersection = None
                            next_intersection = None
                            break


    def inside(self, geometry):
        boun = geometry.geometry().boundingBox()
        for point in self.get_absolute_points():
            contains = boun.contains(point)
            if(not contains): break
        return contains
    def display(self, name):
        HI = HouInterface()
        HI.showCurve(self.get_absolute_points(), name, True)

    def get_floor_params(self):
        return self.__floor_params


    def get_position(self):
        return self.__position


    def get_relative_points(self):
        return self.__relative_points


    def get_absolute_points(self):
        if(not self.absolute_points):
            self.calculate_absolute_points()
        return self.__absolute_points


    def set_floor_params(self, value):
        self.__floor_params = value


    def set_position(self, value):
        self.__position = value


    def set_relative_points(self, value):
        self.__relative_points = value


    def set_absolute_points(self, value):
        self.__absolute_points = value



    def del_floor_params(self):
        del self.__floor_params


    def del_position(self):
        del self.__position


    def del_relative_points(self):
        del self.__relative_points


    def del_absolute_points(self):
        del self.__absolute_points



    floor_params = property(get_floor_params, set_floor_params, del_floor_params, "floor_params's docstring")
    position = property(get_position, set_position, del_position, "position's docstring")
    relative_points = property(get_relative_points, set_relative_points, del_relative_points, "relative_points's docstring")
    absolute_points = property(get_absolute_points, set_absolute_points, del_absolute_points, "absolute_points's docstring")


