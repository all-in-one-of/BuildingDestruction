# -*- coding: utf-8 -*-


class CrackStructure(object):
    '''
    Base class of cracks. Specific crack types has to subclass this class and
    implement at least all methods.
    '''

    def __init__(self, start_point, final_point, crack_builder):
        self.start_point = start_point
        self.final_point = final_point
        self.crack_builder = crack_builder
        self.crack_points = []
        self.crack_nodes = []
        self.parameters = {}
        self.update_crack(crack_builder)

    def update_crack(self, crack_builder=None):
        if(crack_builder):
            self.crack_builder = crack_builder

        self.crack_points, self.crack_nodes = self.crack_builder.make_crack(
                                                          self.start_point,
                                                          self.final_point,
                                                          self.parameters,
                                                          self.crack_nodes)

    def tune_parameter(self, param, value):
        self.parameters[param] = value
        self.update_crack(self.crack_builder)

    def display_on(self):
        pass

    def display_off(self):
        pass
