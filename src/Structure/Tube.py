# -*- coding: utf-8 -*-
'''
Created on Oct 27, 2011

@author: carlos
'''
from ExternalClasses import HouInterface

DEFAULT_RADIUS = 0.07

class Tube(object):


    def __init__(self, tube_params, center, height, orientation):
        reload(HouInterface)
        '''
        user_restriction_parms:
            tubes:
                tube_default_radius
                tube_default_put_each_x
                tube_default_put_each_z
        '''
        self.tube_params = tube_params
        self.center = center
        self.height = height
        self.orientation = orientation
        self.associate_nodes = None
        
    def display(self, name = 'tube', HI= None):
        global DEFAULT_RADIUS
        if(not HI):
            HI = HouInterface.HouInterface()
            
        radius = self.extract_parm_from_user_restrictions('tube_default_radius', DEFAULT_RADIUS)
        nodeName = HI.showTube(name, radius, self.center, self.height, self.orientation)
        
        self.associate_nodes = HI.tubes[nodeName]

    def extract_parm_from_user_restrictions(self, parm, default=None):
        #TODO: define an get parms from building
        if(parm in self.get_tube_params()):
            return self.get_tube_params()[parm]
        return default
    
    def get_tube_params(self):
        return self.tube_params