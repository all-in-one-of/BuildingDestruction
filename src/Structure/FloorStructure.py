# -*- coding: utf-8 -*-
'''
Created on Oct 27, 2011

@author: carlos
'''
from ExternalClasses import GeoMath
from Structure import CreateFloors
import Floor
import logging
class FloorStructure(object):
    '''
    classdocs
    '''


    def __init__(self, floor_params, crack, base_node, geo):
        reload (Floor)
        '''
        Constructor
        user_restriction_parms:
            floors:
                floor_default_size_y
                floor_default_put_each_y
        '''
        self.floor_params = floor_params
        self.crack = crack
        self.put_floor_each_y = None
        self.base_node = base_node
        self.geo = geo
        
    def extract_parm_from_user_restrictions(self, parm, default=None):
        #TODO: define an get parms from building
        if(parm in self.get_user_restriction_parms()):
            return self.set_label_window(self.get_user_restriction_parms()[parm])
        return None
            
    def calculate_floors_position(self):
        logging.debug('START Class FloorStructure, method calculate_floors_position')
        points_base_node = [list(p.position()) for p in self.get_base_node().geometry().points()]
        lowest_point = list(self.get_base_node().geometry().boundingBox().minvec())
        
        #Now we stract the points of the floor from the building
        structure_of_floor = []
        for point in points_base_node:
            #If the point has the same y position than the lowest point, the
            #point will be a floor point
            #We cant do that beacuse the points returned from geometry of houdini
            #node are ordered, and the points can be the structure of the floor
            #just as it is
            if(point[1] == lowest_point):
                #Mapping to y=0
                structure_of_floor.append([point[0], 0, point[2]])
        center_point_of_structure = GeoMath.centerOfPoints(structure_of_floor)
        logging.debug("Center of structure " + str(center_point_of_structure))
        structure_of_floor = self.translate_structure_to_center(
                                center_point_of_structure, structure_of_floor)
        logging.debug("Structure of floor " + str(structure_of_floor))
        #=======================================================================
        # Now we want to found the lowest virtual plant with a crack primitive
        # touching it. Also we want the previous of this floor, because this 
        # floor will be visible trough the hole of the next floor
        #=======================================================================
        # Initialize position of the first virtual floor in the center point of the base
        position = center_point_of_structure
        virtual_floor = Floor.Floor(self.get_floor_params(), position, structure_of_floor)
        previous_virtual_floor = virtual_floor
        connected_prims_with_crack = (
            virtual_floor.connected_prims_with_floor(self.get_crack().patternCrack.keys()))
        floor_inside = virtual_floor.inside(self.get_base_node())
        #TEMP: display floor
        virtual_floor.display('First floor')
        #MAYFIX: structure points are the same for each floor, we assume that
        #the building have the same boundary for each floor
        increment = GeoMath.vecScalarProduct(
                    [0, 1, 0], self.extract_parm_from_user_restrictions('floor_default_put_each_y', 0.1))
        logging.debug("Increment " + str(increment))
        acumulated_increment = [0, 0, 0]
        while(not connected_prims_with_crack and floor_inside):
            #TEMP: display floor
            virtual_floor.display('Not conneced and inside')
            
            logging.debug("Position of floor" + str(position))
            logging.debug("Acumulated increment " + str(acumulated_increment))
            acumulated_increment = GeoMath.vecPlus(acumulated_increment, increment)
            position = GeoMath.vecPlus(center_point_of_structure, acumulated_increment)
            previous_virtual_floor = virtual_floor
            virtual_floor = Floor.Floor(self.get_floor_params(), position, structure_of_floor)
            connected_prims_with_crack = (
            virtual_floor.connected_prims_with_floor(self.get_crack().patternCrack.keys()))
            floor_inside = virtual_floor.inside(self.get_base_node())
        
            #If not inside, delete it
        if(not floor_inside):
            logging.debug("Floor outside")
            virtual_floor = None
        #=======================================================================
        # #=======================================================================
        # # once we found the first virtual floor, we check if is it the same 
        # # than the previous virtual floor. If it is the same will assign the
        # # next virtual floor possible. Then we check if this floor is outside
        # # the building. If the virtual floor reside outside building we delete it
        # # and not continue working with floors
        # #=======================================================================
        # if(previous_virtual_floor == virtual_floor):
        #    #Check if it is inside building
        #    floor_inside = virtual_floor.inside(points_base_node)
        #    #If not inside, delete it
        #    if(not floor_inside):
        #        virtual_floor = None
        #=======================================================================
        
        #=======================================================================
        # Now we have to create the other floors until we reached the first floor
        # outside building or not connected with crack prims
        #=======================================================================
        destroyed_virtual_floors = []
        if(virtual_floor):
            connected_prims_with_crack = True
            floor_inside_building = True

            while(connected_prims_with_crack and floor_inside_building):
                virtual_floor.display('Connected and inside')
                destroyed_virtual_floors.append(virtual_floor)
                acumulated_increment = GeoMath.vecPlus(acumulated_increment, increment)
                position = GeoMath.vecPlus(center_point_of_structure, acumulated_increment)
                virtual_floor = Floor.Floor(self.get_floor_params(), position, structure_of_floor)
                connected_prims_with_crack = (
                    virtual_floor.connected_prims_with_floor(
                                                self.get_crack().patternCrack.keys()))
                floor_inside_building = virtual_floor.inside(self.get_base_node())
            
            #Now add the last floor if needed
            if(virtual_floor.inside(self.get_base_node())):
                virtual_floor.display('Last floor inside')
                destroyed_virtual_floors.append(virtual_floor)
                
        else:
            #Only one floor, and its broken
            virtual_floor.display('Only one floor and broken')
            destroyed_virtual_floors.append(previous_virtual_floor)
            
        CreateFloors.CreateFloors(destroyed_virtual_floors, self.get_geo())
    logging.debug('END Class FloorStructure, method calculate_floors_position')    
            
    def translate_structure_to_center(self, center_point_of_structure, structure_of_floor):
        translation = GeoMath.vecSub([0, 0, 0], center_point_of_structure)
        new_structure = []
        for point in structure_of_floor:
            new_structure.append(GeoMath.vecPlus(point, translation))
        return new_structure
    
    def create_floors(self):
        pass

    def get_floor_params(self):
        return self.__floor_params


    def get_crack(self):
        return self.__crack


    def set_floor_params(self, value):
        self.__floor_params = value


    def set_crack(self, value):
        self.__crack = value

    def del_floor_params(self):
        del self.__floor_params


    def del_crack(self):
        del self.__crack

    floor_params = property(get_floor_params, set_floor_params, del_floor_params, "floor_params's docstring")
    crack = property(get_crack, set_crack, del_crack, "crack's docstring")

    def get_put_floor_each_y(self):
        return self.__put_floor_each_y


    def set_put_floor_each_y(self, value):
        self.__put_floor_each_y = value


    def del_put_floor_each_y(self):
        del self.__put_floor_each_y

    put_floor_each_y = property(get_put_floor_each_y, set_put_floor_each_y, del_put_floor_each_y, "put_floor_each_y's docstring")

    def get_base_node(self):
        return self.__base_node


    def set_base_node(self, value):
        self.__base_node = value


    def del_base_node(self):
        del self.__base_node

    base_node = property(get_base_node, set_base_node, del_base_node, "base_node's docstring")

    def get_geo(self):
        return self.__geo


    def set_geo(self, value):
        self.__geo = value


    def del_geo(self):
        del self.__geo

    geo = property(get_geo, set_geo, del_geo, "geo's docstring")
    
    
