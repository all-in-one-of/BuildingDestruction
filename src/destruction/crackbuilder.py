# -*- coding: utf-8 -*-


class CrackBuilder(object):
    '''
    Base class to crack builders. Crack builder types(as dynamic or fixed) has
    to subclass this class and implement at least all methods.
    '''

    def __init__(self, type_alias):
        self.type_alias = type_alias

    def make_crack(self, start_point, final_point, parameters={}, nodes=[]):
        '''
        @parameters This is extra parameters not given by the program GUI. We
        assume the majority of the parameters are given by the 3D program GUI,
        then, you modify these parameters directly in the program GUI and then
        the crack is updated automatically. DO NOT PUT HERE PARAMETERS ALREADY
        GIVEN BY THE 3D PROGRAM. For the shake of cleanliness.
        '''
        pass
