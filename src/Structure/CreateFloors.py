# -*- coding: utf-8 -*-
'''
Created on Oct 27, 2011

@author: carlos
'''
from ExternalClasses import HouInterface

class CreateFloors(object):
    '''
    classdocs
    '''


    def __init__(self, virtual_floors, geo):
        reload(HouInterface)
        '''
        Constructor
        '''
        
        '''
        user_restriction_parms:
        floors:
            floor_default_size_y
            floor_default_put_each_y
        '''
        
        self.virtual_floors = virtual_floors
        self.geo = geo
        self.floors_geo = HouInterface.HouInterface()
        self.do()

    def do(self):
        for virtual_floor in self.virtual_floors:
            virtual_floor.display(HI = self.floors_geo)
            
    def extract_parm_from_user_restrictions(self, parm, default=None):
        #TODO: define an get parms from building
        if(parm in self.get_floor_params()):
            return self.get_floor_params()[parm]
        return default
