# -*- coding: utf-8 -*-
'''
Created on Oct 27, 2011

@author: carlos
'''
# FIXME: bounding box has to been ported
from destruction import BoundingBox
# FIXME deprectaed custom errors
from destruction import Errors
from lib import GeoMath
import destroystructure
import floorstructure
import metallicstructure
import logging
epsilon = GeoMath.littleEpsilon

class BuildingStructure(object):

    '''
    Manage all the building structure inside a building, like plants, metal structure, etc.
    We get the information based on the size of windows.
    '''

    def __init__(self, crack, path, inserts, geo, user_restriction_parms):
        reload(floorstructure)
        reload(metallicstructure)
        reload(BoundingBox)
        '''
        Constructor
        user_restriction_parms:
            general:
                label_window
                window_size_x
                window_size_y
            floors:
                floor_default_size_y
                floor_default_put_each_y
            tubes:
                tube_default_radius
                tube_default_put_each_x
                tube_default_put_each_z
        '''
        self.user_restriction_parms = user_restriction_parms
        self.crack = crack
        self.path = path
        self.all_building_primitives = None
        self.base_node = None
        self.geo = geo
        self.inserts = inserts
        self.floor_structure = None
        self.metal_structure = None

    def extract_parm_from_user_restrictions(self, parm, default = None):
        # TODO: define an get parms from building
        if(parm in self.get_user_restriction_parms()):
            return self.get_user_restriction_parms()[parm]
        return None
    def set_parm_user_restrictions(self, parm, value):
        self.user_restriction_parms[parm] = value

    def create_extra_structure(self):
        #=======================================================================
        # Get information about size of where can be the floors or tubes
        #=======================================================================
        try:
            if(not self.extract_parm_from_user_restrictions('label_window') and
               (not self.extract_parm_from_user_restrictions('window_size_x')
                 or not self.extract_parm_from_user_restrictions('window_size_y'))):
                logging.error('Class BuildingStructure, label_window cant be none')
                raise Errors.CantBeNoneError('Label window cant be none',
                                             'We need the label of windows to'
                                             'get information about windows')
        except Errors.CantBeNoneError as e:
            Errors.Error.display_exception(e)
            exit()

        window_size = self.calculate_windows_size()

        if(not self.extract_parm_from_user_restrictions('window_size_x')):
            self.set_parm_user_restrictions('window_size_x', window_size[0])
        if(not self.extract_parm_from_user_restrictions('window_size_y')):
            self.set_parm_user_restrictions('window_size_y', window_size[1])
        #=======================================================================
        # Create floor structure
        # Put plant each y-size of window - size of plant/2
        #=======================================================================
        self.find_base_node()
        if(not self.extract_parm_from_user_restrictions('floor_default_put_each_y')):
            self.set_parm_user_restrictions('floor_default_put_each_y', self.extract_parm_from_user_restrictions('window_size_y'))
        self.set_floor_structure(floorstructure.FloorStructure(
            self.get_user_restriction_parms(), self.get_crack(), self.get_path(),
             self.get_base_node(), self.get_geo()))

        #=======================================================================
        # Create metal structure
        # Put a tube each x-size window and each y-size window to create a grid
        #=======================================================================
        self.set_metal_structure(metallicstructure.MetallicStructure
                                 (self.get_user_restriction_parms(),
                                  self.get_floor_structure(),
                                  self.get_geo()))

    def calculate_windows_size(self):
        global epsilon
        #=======================================================================
        # Get the insert node with windows
        #=======================================================================
        insert_windows = None
        for insert in self.get_inserts():
            for filter_group in insert.parm('filter').evalAsString().split():
                if(filter_group == self.extract_parm_from_user_restrictions('label_window')):
                    insert_windows = insert
                    break
        try:
            if(not insert_windows):
                logging.error('Class BuildingStructure, Label window not found at inserts')
                raise Errors.CantBeNoneError('Window cant be none',
                                             'Label window not found at inserts')
        except Errors.CantBeNoneError as e:
            Errors.Error.display_exception(e)
            exit()

        #=======================================================================
        # Get the size of the geometry of own window primitive
        #=======================================================================
        # We use the parent node because the insertnode has a cooked geometry
        # with windows inserteds.

        previous_node = insert_windows.inputs()[0]
        delete_node = previous_node.createOutputNode('delete')
        delete_node.parm('group').set(self.extract_parm_from_user_restrictions('label_window'))
        delete_node.parm('negate').set('keep')
        some_window = delete_node.geometry().prims()[0]
        window_points = [list(p.point().position()) for p in some_window.vertices()]
        window_bounding_box = GeoMath.boundingBox(window_points)
        window_size = [window_bounding_box.sizevec()[0], window_bounding_box.sizevec()[1]]
        return window_size

    def find_base_node(self):
        geo = self.get_geo()
        all_childrens = geo.children()
        nodes = dict([(w.type().name(), w) for w in all_childrens])
        try:
            if('CreateBase' not in nodes):
                raise Errors.CantBeNoneError('Node base cant be none',
                                             'We need a base node to calculate'
                                             'the structure of the bulding')
        except Errors.CantBeNoneError as e:
            logging.error('Exception ocurred:' + e.expr)
            print 'Exception ocurred:', e.expr
            exit()
        self.set_base_node(nodes['CreateBase'])

    def get_user_restriction_parms(self):
        return self.__user_restriction_parms

    def destroy(self):
        reload(floorstructure)
        self.floor_structure.destroy()


























    def get_crack(self):
        return self.__crack

    def get_path(self):
        return self.path

    def get_all_building_primitives(self):
        return self.__all_building_primitives


    def get_inserts(self):
        return self.__inserts


    def get_label_window(self):
        return self.__label_window


    def get_window_height(self):
        return self.__window_height


    def get_window_width(self):
        return self.__window_width


    def get_floor_structure(self):
        return self.__floor_structure


    def get_metal_structure(self):
        return self.__metal_structure


    def set_user_restriction_parms(self, value):
        self.__user_restriction_parms = value


    def set_crack(self, value):
        self.__crack = value

    def set_path(self, value):
        self.path = value

    def set_all_building_primitives(self, value):
        self.__all_building_primitives = value


    def set_inserts(self, value):
        self.__inserts = value


    def set_label_window(self, value):
        self.__label_window = value


    def set_window_height(self, value):
        self.__window_height = value


    def set_window_width(self, value):
        self.__window_width = value


    def set_floor_structure(self, value):
        self.__floor_structure = value


    def set_metal_structure(self, value):
        self.__metal_structure = value


    def del_user_restriction_parms(self):
        del self.__user_restriction_parms


    def del_crack(self):
        del self.__crack


    def del_all_building_primitives(self):
        del self.__all_building_primitives


    def del_inserts(self):
        del self.__inserts


    def del_label_window(self):
        del self.__label_window


    def del_window_height(self):
        del self.__window_height


    def del_window_width(self):
        del self.__window_width


    def del_floor_structure(self):
        del self.__floor_structure


    def del_metal_structure(self):
        del self.__metal_structure

    user_restriction_parms = property(get_user_restriction_parms, set_user_restriction_parms, del_user_restriction_parms, "user_restriction_parms's docstring")
    crack = property(get_crack, set_crack, del_crack, "crack's docstring")
    all_building_primitives = property(get_all_building_primitives, set_all_building_primitives, del_all_building_primitives, "all_building_primitives's docstring")
    inserts = property(get_inserts, set_inserts, del_inserts, "inserts's docstring")
    label_window = property(get_label_window, set_label_window, del_label_window, "label_window's docstring")
    window_height = property(get_window_height, set_window_height, del_window_height, "window_height's docstring")
    window_width = property(get_window_width, set_window_width, del_window_width, "window_width's docstring")
    floor_structure = property(get_floor_structure, set_floor_structure, del_floor_structure, "floor_structure's docstring")
    metal_structure = property(get_metal_structure, set_metal_structure, del_metal_structure, "metal_structure's docstring")

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


