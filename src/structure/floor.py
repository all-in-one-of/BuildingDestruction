# -*- coding: utf-8 -*-
'''
Created on Oct 27, 2011

@author: carlos
'''
import logging
from lib import GeoMath
from lib import HouInterface

class Floor(object):
    '''
    classdocs
    '''

    # FIXME: position needed? If we deleted relative points it is not long needed

    def __init__(self, floor_params, structure_points):
        reload(GeoMath)
        reload(HouInterface)
        '''
        Constructor
        '''
        '''
        Parms
        floors:
                floor_default_size_y
                floor_default_put_each_y
        '''
        reload (GeoMath)
        self.floor_params = floor_params
        self.absolute_points = structure_points
        self.associate_nodes = None
        self.intersections = []

    # TEMP: this functions is no longer used
    def calculate_absolute_points(self):
        translation = GeoMath.vecSub(self.get_position(), [0, 0, 0])
        new_structure = []
        for point in self.get_relative_points():
            new_structure.append(GeoMath.vecPlus(point, translation))
        self.set_absolute_points(new_structure)

    # FIXME: We assume that the crack have to pass at least one time to one floor
    # but it is not correct, because the patterns can go between two floors
    # without passing floors
    def intersections_with_crack(self, crack, path_ordered):
        reload(GeoMath)
        intersections = []
        edges_floor = GeoMath.getEdgesFromPoints(self.get_absolute_points())
        prev_intersection = None
        next_intersection = None
        #=======================================================================
        # we group the intersections in pairs, because after we'll have a different
        # destruction in the floor for each pair of intersection
        #=======================================================================

        for infoPrim in path_ordered:
            patterns = crack[infoPrim.getPrim()]
            for pattern in patterns:
                pattern_edges = GeoMath.getEdgesFromPoints(pattern.getPoints())
                may_intersect, pattern_edge_inter, floor_edge_inter = GeoMath.bolzanoIntersectionEdges2_5D(pattern_edges, edges_floor)
                if(may_intersect):
                    # FIXME: HACK: we take one point of the pattern edge and put the y of the floor.
                    # We are assuming the edge is perpendicular to the floor.
                    # TEMP:
                    point_intersection = [pattern_edge_inter[0][0], floor_edge_inter[0][1], pattern_edge_inter[0][2]]
                    logging.debug("Intersection bef" + str(point_intersection))
                    logging.debug("fllor_edge_inter " + str(floor_edge_inter))
                    #point2DToProjectOntoXZ = [point_intersection[0], 0, point_intersection[2]]
                    #floorEdge2DToCalculateProjectionOntoXZ = [[floor_edge_inter[0][0],0 , floor_edge_inter[0][2]], [floor_edge_inter[1][0], 0, floor_edge_inter[1][2]]]

                    #point_intersection = GeoMath.getPointProjectionOnLine(floorEdge2DToCalculateProjectionOntoXZ, point2DToProjectOntoXZ)
                    #point_intersection = [point_intersection[0], floor_edge_inter[0][1], point_intersection[2]]

                    logging.debug("Intersection " + str(point_intersection))
                    
                    if(not prev_intersection):
                        prev_intersection = point_intersection
                        break
                    elif(not GeoMath.pointEqualPoint(point_intersection, prev_intersection)):
                        next_intersection = point_intersection
                        new_intersection = [prev_intersection, next_intersection]
                        intersections.append(new_intersection)
                        prev_intersection = None
                        next_intersection = None
                        break
        return intersections


    def inside(self, geometry):
        boun = geometry.geometry().boundingBox()
        for point in self.get_absolute_points():
            contains = boun.contains(point)
            if(not contains): break
        return contains

    def display_on(self, name = 'floor', HI = None):
        if(not HI):
            HI = HouInterface.HouInterface()
        # Get the size of the floor using its points
        bounding_box = GeoMath.boundingBox(self.get_absolute_points())
        size = bounding_box.sizevec()
        # Put the size 'y' that user wants the floor to be
        size[1] = self.extract_parm_from_user_restrictions('floor_default_size_y')
        center = GeoMath.centerOfPoints(self.get_absolute_points())
        nodeName = HI.showCube(name, size, center)
        self.associate_nodes = HI.cubes[nodeName]

    def display_off(self):
        for node in self.associate_nodes:
            node.delete()

    def extract_parm_from_user_restrictions(self, parm, default = None):
        # TODO: define an get parms from building
        if(parm in self.get_floor_params()):
            return self.get_floor_params()[parm]
        return default

    def get_floor_params(self):
        return self.__floor_params


    def get_position(self):
        return self.__position


    def get_relative_points(self):
        return self.__relative_points


    def get_absolute_points(self):
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


