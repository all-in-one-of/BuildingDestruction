# -*- coding: utf-8 -*-
'''
Created on Oct 27, 2011

@author: carlos
'''
from lib import GeoMath
import tube
import math
import createmetallicstructure
DEFAULT_PUT_TUBE_EACH_X = 0.50
DEFAULT_PUT_TUBE_EACH_Z = 0.70


class MetallicStructure(object):

    '''
    classdocs
    '''

    def __init__(self, tube_params, floor_structure, geo):
        reload(tube)
        reload(createmetallicstructure)
        reload(GeoMath)
        '''
        user_restriction_parms:
            tubes:
                tube_default_radius
                tube_default_put_each_x
                tube_default_put_each_z
        '''
        self.tube_params = tube_params
        self.floor_structure = floor_structure
        self.tubes = {'x': [], 'z': []}
        self.geo = geo
        self.calculate_tubes_position()

    def calculate_tubes_position(self):
        for floor in self.floor_structure.get_floors():
            center = GeoMath.centerOfPoints(floor.get_absolute_points())
            #==================================================================
            # Guess how many tubes for each part. We divide the floor into 4 parts
                        # in a half in x direction and in a half in z direction.
            #==================================================================
            boun = GeoMath.boundingBox(floor.get_absolute_points())

            height_x_tubes = boun.sizevec()[2]
            height_z_tubes = boun.sizevec()[0]
            orientation_x_tubes = 'z'
            orientation_z_tubes = 'x'
            size_x_half_section = boun.sizevec()[0] / 2.0
            put_tube_each_x = self.extract_parm_from_user_restrictions(
                'tube_default_put_each_x', DEFAULT_PUT_TUBE_EACH_X)
            n_tubes_x_half_section = int(
                math.floor(size_x_half_section / put_tube_each_x))

            size_z_half_section = boun.sizevec()[2] / 2.0
            put_tube_each_z = self.extract_parm_from_user_restrictions(
                'tube_default_put_each_z', DEFAULT_PUT_TUBE_EACH_Z)
            n_tubes_z_half_section = int(
                math.floor(size_z_half_section / put_tube_each_z))

            # The first time putting tubes in x we put a tube in the middle
            tube_instance = tube.Tube(
                self.tube_params, center, height_x_tubes, orientation_x_tubes)
            self.tubes['x'].append(tube_instance)
            # To the right in x, so we will adding 'x' value to the center
            # point
            increment = [put_tube_each_x, 0, 0]
            tube_center = GeoMath.vecPlus(center, increment)

            for _ in range(n_tubes_x_half_section):
                tube_instance = tube.Tube(
                    self.tube_params, tube_center, height_x_tubes, orientation_x_tubes)
                self.tubes['x'].append(tube_instance)
                tube_center = GeoMath.vecPlus(tube_center, increment)

            # To the left
            increment = [-put_tube_each_x, 0, 0]
            tube_center = GeoMath.vecPlus(center, increment)
            for _ in range(n_tubes_x_half_section):
                tube_instance = tube.Tube(
                    self.tube_params, tube_center, height_x_tubes, orientation_x_tubes)
                self.tubes['x'].append(tube_instance)
                tube_center = GeoMath.vecPlus(tube_center, increment)

            # The first time putting tubes in z we put a tube in the middle
            tube_instance = tube.Tube(
                self.tube_params, center, height_z_tubes, orientation_z_tubes)
            self.tubes['z'].append(tube_instance)
            # To the right in x, so we will adding 'x' value to the center
            # point
            increment = [0, 0, put_tube_each_z]
            tube_center = GeoMath.vecPlus(center, increment)

            for _ in range(n_tubes_z_half_section):
                tube_instance = tube.Tube(
                    self.tube_params, tube_center, height_z_tubes, orientation_z_tubes)
                self.tubes['z'].append(tube_instance)
                tube_center = GeoMath.vecPlus(tube_center, increment)

            # To the left
            increment = [0, 0, -put_tube_each_z]
            tube_center = GeoMath.vecPlus(center, increment)
            for _ in range(n_tubes_z_half_section):
                tube_instance = tube.Tube(
                    self.tube_params, tube_center, height_z_tubes, orientation_z_tubes)
                self.tubes['z'].append(tube_instance)
                tube_center = GeoMath.vecPlus(tube_center, increment)

            #Don't create tubes for now
            #createmetallicstructure.CreateMetallicStructure(
            #   self.tubes, self.geo)

    def extract_parm_from_user_restrictions(self, parm, default=None):
        # TODO: define an get parms from building
        if(parm in self.get_tube_params()):
            return self.get_tube_params()[parm]
        return default

    def get_tube_params(self):
        return self.tube_params
