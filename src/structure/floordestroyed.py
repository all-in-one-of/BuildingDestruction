# -*- coding: utf-8 -*-
import floor
from destruction import crack

class FloorDestroyed(floor.Floor):

    def __init__(self, floor_params, structure_points, control_points, crack):
        super(FloorDestroyed, self).__init__(floor_params, structure_points)
        self.control_points = control_points
        self.crack = crack

    def move_control_point(self, control_point_id, new_position):
        self.control_points[control_point_id] = new_position
        self.update_crack()

    def update_crack(self):
        self.crack.update_crack()

    def display_on(self):
        pass

    def display_off(self):
        pass

