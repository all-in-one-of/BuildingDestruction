# -*- coding: utf-8 -*-

import crackbuilder
from lib import HouInterface
TYPE = 'Bezier smooth'


class CrackBuilderBezierSmooth(crackbuilder.CrackBuilder):

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CrackBuilderBezierSmooth, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        global TYPE
        super(CrackBuilderBezierSmooth, self).__init__(TYPE)

    def make_crack(self, start_point, final_point, parameters={}, nodes=[]):
        crack_points = []
        # TODO
        return crack_points, nodes

    def get_builder_type(self):
        return self.type_alias
