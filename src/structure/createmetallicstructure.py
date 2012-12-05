# -*- coding: utf-8 -*-
'''
Created on Oct 27, 2011

@author: carlos
'''
from lib import HouInterface

class CreateMetallicStructure(object):
    '''
    classdocs
    '''


    def __init__(self, virtual_tubes, geo):
        reload(HouInterface)
        
        self.virtual_tubes = virtual_tubes
        self.geo = geo
        self.tubes_geo = HouInterface.HouInterface()
        self.do()

    def do(self):
        for orientation in self.virtual_tubes.keys():
            for tube in self.virtual_tubes[orientation]:
                tube.display(HI = self.tubes_geo)